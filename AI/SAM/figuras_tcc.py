"""figuras_tcc — figuras explicativas da monografia, só com material de calibração.

Gera em `apresentações/Overleaf/TCC/figuras/`:

- `curva_joelho.png`: a curva da regra (D17) de uma sonda, somada nas três
  vagas de limiar, com o limiar da regra e o do autor marcados, e a mesma curva
  normalizada com a corda e o ponto mais distante dela (o joelho).
- `regra_x_autor.png`: os 45 pares (litologia, sonda) da faixa A, limiar da
  regra × limiar do autor, em escala log, com a diagonal y = x.
- `exemplo_<rocha>_<vaga>.jpg`: cópia das figuras regra × autor que o
  `figuras_regra_autor.py` grava em `apresentações/jacitec/figuras/`.

Lê só `selectRocks/` (imagens do `train/`, D17) e o `_cache/` das vagas: não
toca o `test/` nem a auditoria (D7). Não roda o SAM (D18).

    ..\\.venv\\Scripts\\python.exe figuras_tcc.py
    ..\\.venv\\Scripts\\python.exe figuras_tcc.py --rocha siena_white --sonda vein
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, LogLocator

import sam_cache

SAM_DIR = Path(__file__).parent.resolve()
SELECT_ROCKS = SAM_DIR / "selectRocks"
RAIZ = (SAM_DIR / ".." / "..").resolve()
SAIDA = RAIZ / "apresentações" / "Overleaf" / "TCC" / "figuras"
JACITEC = RAIZ / "apresentações" / "jacitec" / "figuras"

VAGAS_LIMIAR = ("limiar_sutil", "limiar_tipica", "limiar_forte")
MOVIMENTADAS = {"shadow_white", "san_francisco_green", "white_mirage", "golden_storm"}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})


def virgula(x: float, casas: int = 3) -> str:
    return f"{x:.{casas}f}".replace(".", ",")


def eixo_log_decimal(eixo) -> None:
    """Rótulos 0,01 / 0,1 / 1 em vez de 10^-2: o leitor do TCC não precisa de potência."""
    eixo.set_major_locator(LogLocator(base=10, subs=(1.0, 2.0, 5.0)))
    eixo.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    eixo.set_minor_formatter(FuncFormatter(lambda v, _: ""))


def curva_joelho(rocha: str, sonda: str) -> None:
    calib = json.loads((SELECT_ROCKS / rocha / "calibracao.json").read_text(encoding="utf-8"))
    registrado = calib["sondas"][sonda]
    dados = []
    for v in VAGAS_LIMIAR:
        # Igual ao calibrador (`_ler`): detecção sem peça não é marcação.
        scores, polys = sam_cache.carregar(sam_cache.caminho_cache(SELECT_ROCKS / rocha, v, sonda))
        dados.append(scores[sam_cache.indices_validos(polys)])
    todos = np.concatenate(dados)
    grade = sam_cache.limiares_sugeridos(todos, n=80)
    n = np.array([sum(int((d > t).sum()) for d in dados) for t in grade])
    t_regra = sam_cache.joelho(list(zip(grade, n)))
    if abs(t_regra - registrado["limiar_regra"]) > 1e-3:
        raise SystemExit(f"o joelho recalculado ({t_regra:.4f}) não bate com o registrado "
                         f"({registrado['limiar_regra']:.4f}): o cache não é o da calibração")
    t_autor = registrado["limiar_trabalho"]

    x = np.log(grade)
    xn = (x - x.min()) / (x.max() - x.min())
    yn = (n - n.min()) / (n.max() - n.min())
    i = int(np.argmax(np.abs(xn + yn - 1) / np.sqrt(2)))

    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
    a.plot(grade, n, color="#1f4e79", lw=2)
    a.set_xscale("log")
    eixo_log_decimal(a.xaxis)
    a.axvline(t_regra, color="#c55a11", ls="--", lw=1.6,
              label=f"regra (joelho): {virgula(t_regra, 4)}")
    a.axvline(t_autor, color="#548235", ls="-", lw=1.6,
              label=f"autor: {virgula(t_autor, 4)}")
    a.set_xlabel("limiar de confiança (escala logarítmica)")
    a.set_ylabel("marcações nas três imagens de limiar")
    a.set_title("(a) curva da regra", loc="left")
    a.legend(frameon=False)

    b.plot(xn, yn, color="#1f4e79", lw=2, label="curva normalizada")
    b.plot([0, 1], [1, 0], color="gray", ls=":", lw=1.4, label="corda")
    # segmento perpendicular do joelho até a corda
    d = (xn[i] + yn[i] - 1) / 2
    b.plot([xn[i], xn[i] - d], [yn[i], yn[i] - d], color="#c55a11", lw=1.4)
    b.scatter([xn[i]], [yn[i]], color="#c55a11", zorder=3, label="joelho: ponto mais distante da corda")
    b.set_xlabel("limiar normalizado (log)")
    b.set_ylabel("marcações normalizadas")
    b.set_title("(b) o joelho", loc="left")
    for e in (b.xaxis, b.yaxis):
        e.set_major_formatter(FuncFormatter(lambda v, _: virgula(v, 1)))
    b.set_aspect("equal")
    b.legend(frameon=False, loc="lower left", fontsize=9)

    fig.tight_layout()
    fig.savefig(SAIDA / "curva_joelho.png", dpi=200)
    plt.close(fig)
    print(f"curva_joelho.png  ({rocha}, {sonda}: regra {t_regra:.4f}, autor {t_autor:.4f})")


def regra_x_autor() -> None:
    pts = []
    for f in sorted(SELECT_ROCKS.glob("*/calibracao.json")):
        c = json.loads(f.read_text(encoding="utf-8"))
        for s, v in c["sondas"].items():
            pts.append((c["rock"], s, v["limiar_regra"], v["limiar_trabalho"]))
    r = np.array([p[2] for p in pts])
    u = np.array([p[3] for p in pts])
    mov = np.array([p[0] in MOVIMENTADAS for p in pts])

    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    lo, hi = 0.002, 1.0
    ax.plot([lo, hi], [lo, hi], color="gray", ls=":", lw=1.3, label="autor = regra")
    ax.plot([lo, hi], [3.3 * lo, 3.3 * hi], color="gray", ls="--", lw=1.0,
            label="autor = 3,3 × regra (mediana)")
    ax.scatter(r[~mov], u[~mov], color="#1f4e79", s=36, label="demais litotipos")
    ax.scatter(r[mov], u[mov], color="#c55a11", marker="^", s=44, label="movimentados")
    ax.set_xscale("log")
    ax.set_yscale("log")
    eixo_log_decimal(ax.xaxis)
    eixo_log_decimal(ax.yaxis)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("limiar da regra")
    ax.set_ylabel("limiar adotado pelo autor")
    ax.set_aspect("equal")
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(SAIDA / "regra_x_autor.png", dpi=200)
    plt.close(fig)
    acima = int((u > r).sum())
    print(f"regra_x_autor.png  ({len(pts)} pares, {acima} com o autor acima da regra)")


def quatro_vagas(rocha: str) -> None:
    """As quatro imagens de calibração de uma litologia, lado a lado (todas do `train/`)."""
    from PIL import Image

    meta = json.loads((SELECT_ROCKS / rocha / "meta.json").read_text(encoding="utf-8"))
    titulos = {"descoberta": "descoberta", "limiar_sutil": "limiar: sutil",
               "limiar_tipica": "limiar: típica", "limiar_forte": "limiar: forte"}
    fig, eixos = plt.subplots(1, 4, figsize=(13, 3.6))
    for ax, vaga in zip(eixos, titulos):
        arq = next((SELECT_ROCKS / rocha).glob(f"{vaga}.*"))
        ax.imshow(Image.open(arq))
        origem = meta["slots"][vaga]["origem"]          # ex.: train/1107.JPG
        ax.set_title(f"{titulos[vaga]}\n({origem})", fontsize=10)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(SAIDA / f"vagas_{rocha}.jpg", dpi=170, bbox_inches="tight", pil_kwargs={"quality": 88})
    plt.close(fig)
    print(f"vagas_{rocha}.jpg")


def copiar_exemplos() -> None:
    if not JACITEC.exists():
        print("sem apresentações/jacitec/figuras: rode o figuras_regra_autor.py antes")
        return
    for f in sorted(JACITEC.glob("*.jpg")):
        shutil.copy2(f, SAIDA / f"exemplo_{f.name}")
    print(f"exemplos copiados: {len(list(JACITEC.glob('*.jpg')))}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rocha", default="siena_white")
    ap.add_argument("--sonda", default="vein")
    a = ap.parse_args()
    SAIDA.mkdir(parents=True, exist_ok=True)
    curva_joelho(a.rocha, a.sonda)
    regra_x_autor()
    quatro_vagas(a.rocha)
    copiar_exemplos()


if __name__ == "__main__":
    main()
