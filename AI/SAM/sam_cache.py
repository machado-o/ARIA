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

**Uma detecção, várias peças.** A máscara de uma detecção do SAM pode ter vários
contornos soltos. `Masks.xyn` os funde numa poligonal só, ligando-os por pontes
de ida e volta (`masks2segments(strategy="all")` → `merge_multi_segment`); essas
pontes viravam retas atravessando a chapa na preview e iam para o rótulo. Desde
2026-10-09 a captura tira os contornos direto da máscara e guarda **uma lista de
peças por detecção**, sem ponte nenhuma (decisão do autor: cada peça é uma
marcação própria no `.txt`). O score continua sendo da detecção: as peças de uma
mesma detecção entram e saem juntas na varredura, então a D18 não muda.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

# Piso de confiança da captura. Baixo o bastante para não descartar nada que
# qualquer limiar de trabalho plausível fosse querer (as configs vão de 0,007 a 0,3).
CONF_PISO = 0.001

CACHE_DIRNAME = "_cache"

# Formato do .npz. O 1 (implícito, sem o campo) guardava a poligonal fundida do
# `Masks.xyn`; o 2 guarda as peças de cada detecção. Cache de formato antigo é
# tratado como ausente (`cache_atual`) e recapturado.
FORMATO = 2

Pecas = list[np.ndarray]        # os contornos de UMA detecção, cada um (n, 2)


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


def salvar(caminho: Path, scores: np.ndarray, polys: list[Pecas]) -> None:
    pts, offsets = _achatar([p for pecas in polys for p in pecas])
    caminho.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        caminho,
        scores=np.asarray(scores, dtype=np.float32),
        pts=pts,
        offsets=offsets,
        pecas=np.asarray([len(pecas) for pecas in polys], dtype=np.int64),
        conf_piso=np.float32(CONF_PISO),
        formato=np.int64(FORMATO),
    )


def cache_atual(caminho: Path) -> bool:
    """O arquivo existe e está no formato de hoje (peças por detecção)."""
    if not caminho.exists():
        return False
    with np.load(caminho) as z:
        return "formato" in z.files and int(z["formato"]) == FORMATO


def carregar(caminho: Path) -> tuple[np.ndarray, list[Pecas]]:
    """(scores, peças por detecção). `polys[i]` são os contornos da detecção `i`."""
    with np.load(caminho) as z:
        if "formato" not in z.files or int(z["formato"]) != FORMATO:
            raise ValueError(
                f"{caminho.name} é cache de formato antigo (poligonal fundida) — "
                "apague-o ou recapture; ver `cache_atual`.")
        soltas = _desachatar(z["pts"], z["offsets"])
        cortes = np.concatenate([[0], np.cumsum(z["pecas"])])
        return z["scores"], [soltas[cortes[i]:cortes[i + 1]]
                             for i in range(len(cortes) - 1)]


def caminho_cache(base_dir: Path, imagem: str, sonda: str) -> Path:
    """Um .npz por (imagem, sonda). A sonda vira nome de arquivo seguro."""
    seguro = "".join(c if c.isalnum() or c in "-_" else "_" for c in sonda)
    return base_dir / CACHE_DIRNAME / f"{imagem}__{seguro}.npz"


# ─────────────────────────────────────────────────────────────────────────────
# Varredura offline — o coração do D18
# ─────────────────────────────────────────────────────────────────────────────

def filtrar(
    scores: np.ndarray, polys: list[Pecas], conf: float
) -> tuple[np.ndarray, list[Pecas]]:
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

def pecas_por_deteccao(resultado) -> list[Pecas]:
    """Os contornos de cada detecção, normalizados, **sem ponte entre eles**.

    Faz o que `Masks.xyn` faz — `cv2.findContours(RETR_EXTERNAL,
    CHAIN_APPROX_SIMPLE)` sobre a máscara e `ops.scale_coords(normalize=True)` —
    menos o passo que funde os contornos numa poligonal só. Contorno com menos
    de 3 pontos não é polígono e fica de fora; uma detecção pode, portanto,
    ficar com lista vazia (ver `indices_validos`).

    É a fonte única das peças: o cache do calibrador e o `.txt` do
    `inference.py` saem daqui, para que a preview mostre o que vira rótulo.

    Os imports são tardios de propósito: este módulo é importado pela seleção
    de imagens, que não deve arrastar o ultralytics.
    """
    import cv2
    from ultralytics.utils import ops

    masks = resultado.masks
    if masks is None:
        return []
    dados = masks.data
    dados = (dados.astype("uint8") if isinstance(dados, np.ndarray)
             else dados.byte().cpu().numpy())
    saida: list[Pecas] = []
    for m in np.ascontiguousarray(dados):
        contornos = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        saida.append([
            ops.scale_coords(dados.shape[1:], c.reshape(-1, 2).astype("float32"),
                             masks.orig_shape, normalize=True)
            for c in contornos if len(c) > 2
        ])
    return saida


def capturar(predictor, imagem: Path, sonda: str) -> tuple[np.ndarray, list[Pecas]]:
    """Roda o SAM3 uma vez no piso e devolve (scores, peças por detecção).

    O predictor precisa já ter feito `set_image(imagem)`.
    """
    predictor.args.conf = CONF_PISO
    resultado = predictor(text=[sonda])[0]
    if resultado.masks is None:
        return np.zeros(0, dtype=np.float32), []
    scores = resultado.boxes.conf.cpu().numpy().astype(np.float32)
    polys = pecas_por_deteccao(resultado)
    if len(scores) != len(polys):  # defensivo: os dois vêm do mesmo `keep`
        raise RuntimeError(
            f"scores ({len(scores)}) e polígonos ({len(polys)}) divergem para "
            f"'{sonda}' em {imagem.name} — o cache seria inconsistente."
        )
    return scores, polys


def indices_validos(polys: list[Pecas]) -> list[int]:
    """Índices das detecções que viram rótulo: as que têm ao menos uma peça.

    Devolve índice, e não os polígonos, porque quem chama precisa filtrar os
    scores pelos MESMOS itens — cache com scores e polígonos desalinhados é
    exatamente o erro que `capturar()` já se dá ao trabalho de checar.

    O SAM devolve detecção SEM peça quando a máscara não sobrevive à
    interpolação para o tamanho original (`findContours` não acha contorno de 3
    pontos ou mais). Medido em siena_white/descoberta: acontece de verdade. Ela
    não grava linha nenhuma no .txt — então contá-la como "marcação" no
    calibrador seria mostrar um número que o treino não vê. Esta é a definição
    única de "marcação" (= detecção) para os dois lados; o número de peças é
    outra grandeza, e é `sum(len(p) for p in polys)`.
    """
    return [i for i, p in enumerate(polys) if len(p) > 0]


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
