"""sam_cache — roda o SAM3 uma vez e varre limiares offline (docs/decisoes.md D18).

Por que isso funciona (lido na fonte do ultralytics,
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

A equivalência vale **por versão do ultralytics** (o filtro vive no `postprocess`
dela), não por máquina. O número da versão não fica escrito aqui de propósito: o
autor alterna entre dois PCs e esta docstring já esteve errada por isso. As versões
verificadas estão em `d18_verificado.json`, que o `verificar_d18.py` grava e o
`../ambiente.py` lê.

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


def indices_validos(polys: list[np.ndarray]) -> list[int]:
    """Índices das detecções que viram rótulo: polígono com 3 pontos ou mais.

    Devolve índice, e não os polígonos, porque quem chama precisa filtrar os
    scores pelos MESMOS itens — cache com scores e polígonos desalinhados é
    exatamente o erro que `capturar()` já se dá ao trabalho de checar.

    O SAM devolve detecção com polígono VAZIO quando a máscara não sobrevive à
    interpolação para o tamanho original (`masks2segments` não acha contorno).
    Medido em siena_white/descoberta: acontece de verdade. `inference.py` já as
    descarta com `len(poly) > 2` na hora de gravar o .txt — então contar a
    detecção como "marcação" no calibrador seria mostrar um número que o treino
    não vê. Esta é a definição única de "marcação" para os dois lados.
    """
    return [i for i, p in enumerate(polys) if len(p) > 2]


def joelho(curva: list[tuple[float, int]]) -> float | None:
    """Limiar de maior curvatura da curva (limiar × marcações) — a regra da **D17**.

    É o **limiar da regra** (fechada em 2026-09-26, opção (b)): sem parâmetro livre
    e idêntico para as 45 litologias. O autor pode divergir dele no calibrador; o
    valor ajustado é o limiar de trabalho, gravado ao lado deste em `calibracao.json`.

    Método (Kneedle): normaliza log(limiar) e contagem em [0,1] e devolve o ponto
    de maior distância à corda que liga as duas pontas. Log no eixo x porque os
    scores se concentram na década baixa — em escala linear o joelho cairia
    sempre no primeiro ponto.
    """
    if len(curva) < 4:
        return None
    x = np.log(np.array([t for t, _ in curva], dtype=float))
    y = np.array([n for _, n in curva], dtype=float)
    if x.max() <= x.min() or y.max() <= y.min():
        return None
    xn = (x - x.min()) / (x.max() - x.min())
    yn = (y - y.min()) / (y.max() - y.min())
    # A curva é decrescente: as pontas normalizadas são (0,1) e (1,0), logo a
    # corda é xn + yn - 1 = 0 e a distância perpendicular é |xn + yn - 1|/raiz(2).
    dist = np.abs(xn + yn - 1.0) / np.sqrt(2.0)
    return float(np.exp(x[int(np.argmax(dist))]))
