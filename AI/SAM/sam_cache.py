"""sam_cache — roda o SAM3 uma vez e varre limiares offline (docs/decisoes.md D18).

Por que isso funciona (verificado na fonte do ultralytics 8.4.61,
`SAM3SemanticPredictor.postprocess`):

    pred_scores = (pred_logits.sigmoid() * presence_score).squeeze(-1)
    keep = pred_scores > self.args.conf          # filtro puro, DEPOIS do modelo
    keep = torchvision.ops.nms(boxes, scores, self.args.iou)

O modelo produz máscaras e scores sem conhecer o `conf` — ele apenas descarta. O NMS
roda depois do filtro, mas processa em ordem decrescente de score e só remove usando
um sobrevivente de score MAIOR; portanto incluir detecções de score baixo não altera
as decisões sobre as de score alto.

Consequência: rodar uma vez com o `conf` no piso e filtrar offline é **exatamente
equivalente** a rodar de novo em cada limiar — não é aproximação. Isso troca um ciclo
de calibração de minutos por um de milissegundos.

O cache guarda POLÍGONOS (formato YOLO, coords normalizadas) e não máscaras densas:
é o que acaba no .txt de treino, e evita guardar centenas de bitmaps em disco.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

# Piso de confiança da captura. Baixo o bastante para não descartar nada que
# qualquer limiar de trabalho plausível fosse querer (as configs vão de 0,007 a 0,3).
CONF_PISO = 0.001

CACHE_DIRNAME = "_cache"


# ─────────────────────────────────────────────────────────────────────────────
# Serialização
# ─────────────────────────────────────────────────────────────────────────────

def _achatar(polys: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Polígonos de tamanhos diferentes -> (pontos concatenados, offsets). Sem pickle."""
    if not polys:
        return np.zeros((0, 2), dtype=np.float32), np.zeros(1, dtype=np.int64)
    pts = np.concatenate([np.asarray(p, dtype=np.float32).reshape(-1, 2) for p in polys])
    tamanhos = [len(np.asarray(p).reshape(-1, 2)) for p in polys]
    offsets = np.concatenate([[0], np.cumsum(tamanhos)]).astype(np.int64)
    return pts, offsets


def _desachatar(pts: np.ndarray, offsets: np.ndarray) -> list[np.ndarray]:
    return [pts[offsets[i]:offsets[i + 1]] for i in range(len(offsets) - 1)]


def salvar(caminho: Path, scores: np.ndarray, polys: list[np.ndarray]) -> None:
    pts, offsets = _achatar(polys)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        caminho,
        scores=np.asarray(scores, dtype=np.float32),
        pts=pts,
        offsets=offsets,
        conf_piso=np.float32(CONF_PISO),
    )


def carregar(caminho: Path) -> tuple[np.ndarray, list[np.ndarray]]:
    with np.load(caminho) as z:
        return z["scores"], _desachatar(z["pts"], z["offsets"])


def caminho_cache(base_dir: Path, imagem: str, sonda: str) -> Path:
    """Um .npz por (imagem, sonda). A sonda vira nome de arquivo seguro."""
    seguro = "".join(c if c.isalnum() or c in "-_" else "_" for c in sonda)
    return base_dir / CACHE_DIRNAME / f"{imagem}__{seguro}.npz"


# ─────────────────────────────────────────────────────────────────────────────
# Varredura offline — o coração do D18
# ─────────────────────────────────────────────────────────────────────────────

def filtrar(
    scores: np.ndarray, polys: list[np.ndarray], conf: float
) -> tuple[np.ndarray, list[np.ndarray]]:
    """Aplica um limiar ao cache. Equivale a ter rodado o SAM com esse `conf`.

    Usa `>` e não `>=` para bater exatamente com o `pred_scores > self.args.conf`
    do ultralytics.
    """
    keep = scores > conf
    return scores[keep], [p for p, k in zip(polys, keep) if k]


def curva_de_limiar(
    scores: np.ndarray, limiares: np.ndarray | list[float]
) -> list[tuple[float, int]]:
    """(limiar, nº de detecções) para cada limiar — alimenta o gráfico do calibrador.

    Deixa visível de imediato onde o limiar 'explode' em número de marcações, que é a
    informação que hoje só se descobre rodando o SAM várias vezes.
    """
    return [(float(t), int((scores > t).sum())) for t in limiares]


def limiares_sugeridos(scores: np.ndarray, n: int = 40) -> np.ndarray:
    """Grade de limiares útil para ESTES scores (log-espaçada entre o piso e o máximo).

    Grade linear é inútil aqui: os limiares de trabalho vivem entre 0,007 e 0,3, então
    quase todos os pontos de uma grade linear cairiam numa região sem detecção nenhuma.
    """
    if len(scores) == 0:
        return np.array([CONF_PISO])
    lo = max(float(scores.min()) * 0.9, 1e-4)
    hi = float(scores.max())
    if hi <= lo:
        return np.array([lo])
    return np.geomspace(lo, hi, n)


# ─────────────────────────────────────────────────────────────────────────────
# Captura (precisa de GPU + modelo)
# ─────────────────────────────────────────────────────────────────────────────

def capturar(predictor, imagem: Path, sonda: str) -> tuple[np.ndarray, list[np.ndarray]]:
    """Roda o SAM3 uma vez no piso e devolve (scores, polígonos normalizados).

    O predictor precisa já ter feito `set_image(imagem)`.
    """
    predictor.args.conf = CONF_PISO
    resultado = predictor(text=[sonda])[0]
    if resultado.masks is None:
        return np.zeros(0, dtype=np.float32), []
    scores = resultado.boxes.conf.cpu().numpy().astype(np.float32)
    polys = [np.asarray(p, dtype=np.float32) for p in resultado.masks.xyn]
    if len(scores) != len(polys):  # defensivo: os dois vêm do mesmo `keep`
        raise RuntimeError(
            f"scores ({len(scores)}) e polígonos ({len(polys)}) divergem para "
            f"'{sonda}' em {imagem.name} — o cache seria inconsistente."
        )
    return scores, polys


def obter(
    predictor, base_dir: Path, imagem: Path, sonda: str, forcar: bool = False
) -> tuple[np.ndarray, list[np.ndarray]]:
    """Cache-or-capture: lê do disco se existir, senão roda o SAM e grava."""
    alvo = caminho_cache(base_dir, imagem.stem, sonda)
    if alvo.exists() and not forcar:
        return carregar(alvo)
    scores, polys = capturar(predictor, imagem, sonda)
    salvar(alvo, scores, polys)
    return scores, polys
