"""auditoria_analisar — resultado do Experimento 1 a partir dos julgamentos (D5, D7).

Lê `auditoria/itens.json` (que braço contém cada item e o tamanho de cada
estrato) e os arquivos que o aplicativo exporta, em `auditoria/respostas/`.
Para cada avaliador, estima por braço:

  precisão          marcações julgadas "sim" / marcações do braço
  recall relativo   acertos do braço / acertos do conjunto reunido dos 4 braços

Os dois são estimados por estrato e ponderados pelo tamanho do estrato
(N_h / julgados_h), porque a amostra sobre-representa de propósito os
estratos pequenos (ver `auditoria_preparar.sortear_itens`). "Não sei" fica fora
das contas e é contado à parte. Intervalos de 95% por bootstrap dentro dos
estratos; as diferenças entre braços usam as mesmas reamostragens, então o
intervalo da diferença já leva em conta que os braços dividem itens.

Com dois avaliadores, também a concordância entre eles (kappa de Cohen) nos
itens que os dois julgaram com sim ou não.

Uso, a partir de AI/SAM/:

    ..\\.venv\\Scripts\\python.exe auditoria_analisar.py
    ..\\.venv\\Scripts\\python.exe auditoria_analisar.py --respostas outra/pasta
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

SAM_DIR = Path(__file__).parent.resolve()
AUD = SAM_DIR / "auditoria"

# As litologias que o autor identificou como movimentadas (docs/dataset.md,
# *Litologias movimentadas*; D20).
MOVIMENTADAS = {"shadow_white", "san_francisco_green", "white_mirage", "golden_storm"}

COMPARACOES = (   # (braço, contra), cada uma mudando um fator só (D5)
    ("regra_todas", "unico", "escopo do limiar (H1)"),
    ("regra_autor", "regra_todas", "seleção de sondas"),
    ("autor", "regra_autor", "ajuste do autor"),
)


def ler_respostas(pasta: Path, pacote: str) -> dict[str, dict[str, str]]:
    """{avaliador: {item: resposta}}. Vários exports do mesmo avaliador se juntam,
    e vale a resposta mais recente de cada item."""
    por_avaliador: dict[str, dict[str, tuple[str, str]]] = {}
    nomes: dict[str, str] = {}
    for arq in sorted(pasta.glob("*.json")):
        d = json.loads(arq.read_text(encoding="utf-8"))
        if d.get("pacote") != pacote:
            print(f"ignorado (outro pacote): {arq.name}")
            continue
        chave = d["avaliador"].strip().lower()
        nomes.setdefault(chave, d["avaliador"].strip())
        atual = por_avaliador.setdefault(chave, {})
        for item, r in d["respostas"].items():
            if item not in atual or r["t"] > atual[item][1]:
                atual[item] = (r["r"], r["t"])
    return {nomes[k]: {i: r for i, (r, _) in v.items()} for k, v in por_avaliador.items()}


def julgados_por_estrato(itens: list[dict], respostas: dict[str, str],
                         filtro=lambda it: True) -> tuple[dict[str, list[int]], int]:
    """{estrato: [1, 0, ...]} com sim = 1 e não = 0; e quantos "não sei"."""
    por_h: dict[str, list[int]] = {}
    nao_sei = 0
    for it in itens:
        r = respostas.get(it["id"])
        if r is None or not filtro(it):
            continue
        if r == "nao_sei":
            nao_sei += 1
            continue
        por_h.setdefault(it["estrato"], []).append(1 if r == "sim" else 0)
    return por_h, nao_sei


def estimar(p: dict[str, float], tamanhos: dict[str, int], bracos: list[str]) -> dict:
    """Precisão e recall relativo por braço, dadas as proporções de "sim" por estrato.

    Um braço só tem estimativa se todos os seus estratos tiverem algum julgamento;
    o recall relativo, se todos os estratos do conjunto reunido tiverem.
    """
    vivos = {h: n for h, n in tamanhos.items() if n > 0}
    pool_ok = all(h in p for h in vivos)
    acertos_pool = sum(n * p[h] for h, n in vivos.items() if h in p)
    saida = {}
    for i, b in enumerate(bracos):
        hs = [h for h in vivos if h[i] == "1"]
        if not hs or not all(h in p for h in hs):
            saida[b] = None
            continue
        total = sum(vivos[h] for h in hs)
        acertos = sum(vivos[h] * p[h] for h in hs)
        saida[b] = {
            "precisao": acertos / total,
            "recall_relativo": (acertos / acertos_pool) if pool_ok and acertos_pool > 0 else None,
            "marcacoes": total,
        }
    return saida


def analisar(por_h: dict[str, list[int]], tamanhos: dict[str, int], bracos: list[str],
             reamostras: int, semente: int) -> dict:
    p = {h: float(np.mean(v)) for h, v in por_h.items() if v}
    ponto = estimar(p, tamanhos, bracos)
    rng = np.random.default_rng(semente)
    amostras = {b: {"precisao": [], "recall_relativo": []} for b in bracos}
    difs = {f"{a}-{c}": {"precisao": [], "recall_relativo": []} for a, c, _ in COMPARACOES}
    arrays = {h: np.asarray(v) for h, v in por_h.items() if v}
    for _ in range(reamostras):
        pb = {h: float(rng.choice(v, size=len(v), replace=True).mean()) for h, v in arrays.items()}
        e = estimar(pb, tamanhos, bracos)
        for b in bracos:
            if e[b] is None:
                continue
            for m in ("precisao", "recall_relativo"):
                if e[b][m] is not None:
                    amostras[b][m].append(e[b][m])
        for a, c, _ in COMPARACOES:
            if e[a] is None or e[c] is None:
                continue
            for m in ("precisao", "recall_relativo"):
                if e[a][m] is not None and e[c][m] is not None:
                    difs[f"{a}-{c}"][m].append(e[a][m] - e[c][m])

    def ic(v):
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if v else None

    for b in bracos:
        if ponto[b] is not None:
            for m in ("precisao", "recall_relativo"):
                ponto[b][f"{m}_ic95"] = ic(amostras[b][m])
    comparacoes = {}
    for a, c, rotulo in COMPARACOES:
        if ponto[a] is None or ponto[c] is None:
            continue
        comparacoes[f"{a}-{c}"] = {"mede": rotulo}
        for m in ("precisao", "recall_relativo"):
            if ponto[a][m] is not None and ponto[c][m] is not None:
                comparacoes[f"{a}-{c}"][m] = ponto[a][m] - ponto[c][m]
                comparacoes[f"{a}-{c}"][f"{m}_ic95"] = ic(difs[f"{a}-{c}"][m])
    return {"bracos": ponto, "comparacoes": comparacoes,
            "julgados_por_estrato": {h: len(v) for h, v in sorted(por_h.items())}}


def kappa(r1: dict[str, str], r2: dict[str, str]) -> dict | None:
    comuns = [i for i in r1 if i in r2 and r1[i] != "nao_sei" and r2[i] != "nao_sei"]
    if not comuns:
        return None
    a = np.array([r1[i] == "sim" for i in comuns])
    b = np.array([r2[i] == "sim" for i in comuns])
    po = float((a == b).mean())
    pe = float(a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean()))
    return {"itens": len(comuns), "concordancia": po,
            "kappa": (po - pe) / (1 - pe) if pe < 1 else None}


def pct(v) -> str:
    return "   —  " if v is None else f"{100 * v:5.1f}%"


def imprimir(nome: str, res: dict, chapas: int, nao_sei: int) -> None:
    print(f"\n── {nome} ── julgados por estrato: {res['julgados_por_estrato']}  ·  não sei: {nao_sei}")
    print(f"  {'braço':12s} {'marc./chapa':>11s} {'precisão':>9s} {'IC 95%':>17s} "
          f"{'recall rel.':>11s} {'IC 95%':>17s}")
    for b, e in res["bracos"].items():
        if e is None:
            print(f"  {b:12s}  (faltam julgamentos em algum estrato)")
            continue
        icp = e.get("precisao_ic95") or [None, None]
        icr = e.get("recall_relativo_ic95") or [None, None]
        print(f"  {b:12s} {e['marcacoes'] / chapas:11.1f} {pct(e['precisao']):>9s} "
              f"{pct(icp[0])}–{pct(icp[1])} {pct(e['recall_relativo']):>11s} "
              f"{pct(icr[0])}–{pct(icr[1])}")
    for k, c in res["comparacoes"].items():
        icp = c.get("precisao_ic95") or [None, None]
        icr = c.get("recall_relativo_ic95") or [None, None]
        print(f"  {k:24s} ({c['mede']}): precisão {pct(c.get('precisao'))} "
              f"[{pct(icp[0])}, {pct(icp[1])}]   recall {pct(c.get('recall_relativo'))} "
              f"[{pct(icr[0])}, {pct(icr[1])}]")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--respostas", type=Path, default=AUD / "respostas")
    ap.add_argument("--reamostras", type=int, default=2000)
    ap.add_argument("--saida", type=Path, default=AUD / "resultados.json")
    args = ap.parse_args()
    # O console do Windows, com saída redirecionada, cai em cp1252 e quebra nos acentos.
    sys.stdout.reconfigure(encoding="utf-8")

    meta = json.loads((AUD / "itens.json").read_text(encoding="utf-8"))
    itens, bracos, chapas = meta["itens"], meta["bracos"], meta["chapas"]
    respostas = ler_respostas(args.respostas, meta["pacote"])
    if not respostas:
        print(f"nenhum arquivo de respostas em {args.respostas}")
        return

    def tamanhos_de(rochas: set[str]) -> dict[str, int]:
        t: dict[str, int] = {}
        for r in rochas:
            for h, n in meta["tamanho_estrato_por_litologia"].get(r, {}).items():
                t[h] = t.get(h, 0) + n
        return t

    todas = set(meta["tamanho_estrato_por_litologia"])
    grupos = {"todas": todas, "movimentadas": todas & MOVIMENTADAS,
              "demais": todas - MOVIMENTADAS}
    saida = {"pacote": meta["pacote"], "avaliadores": {}}
    for n, (nome, resp) in enumerate(respostas.items()):
        saida["avaliadores"][nome] = {"respondidas": len(resp)}
        for g, rochas in grupos.items():
            por_h, nao_sei = julgados_por_estrato(itens, resp, lambda it: it["rocha"] in rochas)
            res = analisar(por_h, tamanhos_de(rochas), bracos, args.reamostras, 2026 + n)
            res["nao_sei"] = nao_sei
            saida["avaliadores"][nome][g] = res
            imprimir(f"{nome} · {g}", res, chapas if g == "todas" else
                     chapas * len(rochas) // len(todas), nao_sei)

    nomes = list(respostas)
    if len(nomes) >= 2:
        k = kappa(respostas[nomes[0]], respostas[nomes[1]])
        saida["concordancia"] = {"avaliadores": nomes[:2], **(k or {})}
        if k:
            print(f"\nconcordância {nomes[0]} × {nomes[1]}: {k['itens']} itens, "
                  f"{pct(k['concordancia'])} iguais, kappa = {k['kappa']:.2f}")

    args.saida.write_text(json.dumps(saida, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\n-> {args.saida}")


if __name__ == "__main__":
    main()
