"""sondas — registro ÚNICO das sondas que podem virar rótulo (docs/decisoes.md D8).

Este cadastro já morou em dois lugares ao mesmo tempo: `inference.py` e
`calibrator.py` tinham cada um a sua cópia do `CLASS_ID_MAP`, com um comentário
pedindo que fossem mantidas iguais à mão, e cada um a sua tabela de cores — com
valores **diferentes**. O efeito prático era calibrar olhando uma cor e receber
o resultado final noutra; "Dark patches", em particular, saía preto puro sobre
rocha escura, ou seja, invisível. Um cadastro só elimina as duas classes de erro.

Quem usa:
  - `calibrator.py`  — deixa explorar sonda fora do mapa, mas não a salva (D8).
  - `inference.py`   — aborta antes de carregar o modelo se alguma sonda ficou
                       fora do mapa; sem id de classe não existe rótulo válido.

Para promover uma sonda nova a rótulo, acrescente-a **aqui** — e só aqui.
O id é posicional e vai para o `.txt` de treino: **nunca renumerar** uma sonda
já usada, porque os `.txt` gravados antes passariam a dizer outra coisa. Sonda
nova entra no fim.
"""

from __future__ import annotations

# sonda → id de classe no formato YOLO. A ordem é histórica; só cresce no fim.
CLASS_ID_MAP: dict[str, int] = {
    "vein": 0,
    "crack": 1,
    "Stain": 2,
    "Dark patches": 3,
    "light spot": 4,
    "scratch": 5,
}

# Cor de cada sonda na sobreposição, em **BGR** (é o que o OpenCV espera).
# Escolhidas para se distinguirem entre si e da rocha: nada de preto puro nem
# de branco puro, que desaparecem sobre granito escuro e sobre mármore claro.
CORES: dict[str, tuple[int, int, int]] = {
    "vein":         (255,  90,  40),
    "crack":        ( 40,  70, 255),
    "Stain":        (  0, 170, 255),
    "Dark patches": (200,  40, 200),
    "light spot":   ( 60, 230, 240),
    "scratch":      (120, 255,  90),
}

# Sonda em exploração, ainda sem id: aparece em cinza no calibrador.
COR_EXTRA = (170, 170, 170)


def cor(sonda: str) -> tuple[int, int, int]:
    return CORES.get(sonda, COR_EXTRA)


def nao_registradas(sondas) -> list[str]:
    """As sondas do iterável que não estão no cadastro — na ordem recebida."""
    return [s for s in sondas if s not in CLASS_ID_MAP]


def conhecidas() -> str:
    """As sondas do cadastro em texto, para mensagem de erro."""
    return ", ".join(CLASS_ID_MAP)
