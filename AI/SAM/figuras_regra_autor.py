"""figuras_regra_autor — a mesma chapa com o limiar da regra e com o do autor (D5, D17).

Lê o `calibracao.json` de cada litologia calibrada e o `_cache/` das vagas, e
desenha três painéis lado a lado: a chapa, as marcações no limiar da regra
(joelho) e no limiar de trabalho do autor. As sondas são as do autor nos dois
painéis, então isto é o braço "regra com as sondas do autor" contra o
"calibrado pelo autor" — não o "default" da D5, que só existe depois de as
litologias reunidas estarem calibradas.

Não roda o SAM: filtra o cache (D18). As imagens das vagas são todas do
`train/` (D17), então nenhuma figura toca o `test/`, de onde sai o
conjunto-ouro (D7).

Também grava `regra_x_autor.csv`, uma linha por (litologia, sonda).

    python figuras_regra_autor.py                     # vagas típica e forte
    python figuras_regra_autor.py --vagas descoberta limiar_sutil limiar_tipica limiar_forte
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np

import sam_cache
from sondas import cor

SAM_DIR = Path(__file__).parent.resolve()
SELECT_ROCKS = SAM_DIR / "selectRocks"
SAIDA_PADRAO = (SAM_DIR / ".." / ".." / "apresentações" / "jacitec").resolve()

LADO_PAINEL = 640   # px do maior lado de cada painel
ALTURA_FAIXA = 34   # faixa de legenda acima de cada painel


def abrir_imagem(caminho: Path):
    """`cv2.imread` não abre caminho com acento no Windows (ver calibrator.abrir_imagem)."""
    dados = np.fromfile(caminho, dtype=np.uint8)
    return cv2.imdecode(dados, cv2.IMREAD_COLOR) if dados.size else None


def reduzir(im, lado: int = LADO_PAINEL):
    h, w = im.shape[:2]
    e = lado / max(h, w)
    return cv2.resize(im, (int(w * e), int(h * e)), interpolation=cv2.INTER_AREA)


def desenhar(base, camadas, alpha: float = 0.5):
    """Mesmo desenho do calibrador: uma peça por polígono, uma camada por sonda."""
    out = base.copy()
    h, w = out.shape[:2]
    for polys, cor_bgr in camadas:
        contornos = [np.round(np.asarray(p, dtype=np.float32) * (w, h)).astype(np.int32)
                     for pecas in polys for p in pecas if len(p) > 2]
        if not contornos:
            continue
        sobre = out.copy()
        for c in contornos:
            cv2.fillPoly(sobre, [c], cor_bgr)
        out = cv2.addWeighted(sobre, alpha, out, 1.0 - alpha, 0)
    return out


def com_legenda(painel, texto: str):
    faixa = np.full((ALTURA_FAIXA, painel.shape[1], 3), 255, dtype=np.uint8)
    cv2.putText(faixa, texto, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 1,
                cv2.LINE_AA)
    return np.vstack([faixa, painel])


def camadas_no_limiar(rocha: Path, papel: str, sondas: dict, chave: str):
    """(camadas para desenhar, nº de marcações) com cada sonda no limiar `chave`."""
    camadas, total = [], 0
    for sonda, v in sondas.items():
        arq = sam_cache.caminho_cache(rocha, papel, sonda)
        if not sam_cache.cache_atual(arq):
            raise FileNotFoundError(f"sem cache atual: {arq}")
        scores, polys = sam_cache.carregar(arq)
        validos = sam_cache.indices_validos(polys)
        scores, polys = scores[validos], [polys[i] for i in validos]
        _, vis = sam_cache.filtrar(scores, polys, v[chave])
        camadas.append((vis, cor(sonda)))
        total += len(vis)
    return camadas, total


def legenda_sondas(sondas: dict, largura: int):
    """Faixa inferior com a cor de cada sonda."""
    faixa = np.full((30, largura, 3), 255, dtype=np.uint8)
    x = 8
    for s in sondas:
        cv2.rectangle(faixa, (x, 9), (x + 14, 23), cor(s), -1)
        cv2.putText(faixa, s, (x + 20, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30), 1,
                    cv2.LINE_AA)
        x += 34 + 9 * len(s)
    return faixa


def figura(rocha: Path, calib: dict, papel: str):
    meta = json.loads((rocha / "meta.json").read_text(encoding="utf-8"))
    slot = meta["slots"][papel]
    base = reduzir(abrir_imagem(rocha / slot["arquivo"]))
    sondas = calib["sondas"]
    c_regra, n_regra = camadas_no_limiar(rocha, papel, sondas, "limiar_regra")
    c_autor, n_autor = camadas_no_limiar(rocha, papel, sondas, "limiar_trabalho")
    vaga = papel.removeprefix("limiar_")
    linha = np.hstack([
        com_legenda(base, f"{calib['rock']} - {vaga} ({slot['origem']})"),
        com_legenda(desenhar(base, c_regra), f"regra (joelho): {n_regra} marcacoes"),
        com_legenda(desenhar(base, c_autor), f"autor: {n_autor} marcacoes"),
    ])
    return np.vstack([linha, legenda_sondas(sondas, linha.shape[1])]), n_regra, n_autor


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--vagas", nargs="+", default=["limiar_tipica", "limiar_forte"])
    ap.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    args = ap.parse_args()

    dir_fig = args.saida / "figuras"
    dir_fig.mkdir(parents=True, exist_ok=True)
    linhas = []
    for arq in sorted(SELECT_ROCKS.glob("*/calibracao.json")):
        rocha = arq.parent
        calib = json.loads(arq.read_text(encoding="utf-8"))
        for s, v in calib["sondas"].items():
            linhas.append([calib["rock"], s, v["limiar_regra"], v["limiar_trabalho"],
                           round(v["limiar_trabalho"] / v["limiar_regra"], 2)])
        for papel in args.vagas:
            img, nr, na = figura(rocha, calib, papel)
            destino = dir_fig / f"{calib['rock']}_{papel.removeprefix('limiar_')}.jpg"
            cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])[1].tofile(destino)
            print(f"{destino.name:40s} regra {nr:3d}  autor {na:3d}")

    with open(args.saida / "regra_x_autor.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["litologia", "sonda", "limiar_regra", "limiar_autor", "razao"])
        w.writerows(linhas)
    acima = sum(1 for l in linhas if l[3] > l[2])
    razoes = sorted(l[4] for l in linhas)
    print(f"\n{len(linhas)} sondas; autor acima da regra em {acima}; "
          f"razão mediana {float(np.median(razoes)):.1f} ({razoes[0]} a {razoes[-1]})")


if __name__ == "__main__":
    main()
