"""auditoria_preparar — monta a auditoria cega do Experimento 1 (docs/decisoes.md D5, D7).

A avaliação do Experimento 1 deixou de ser o conjunto-ouro (emenda da D7 de
19/11/2026). Em vez de desenhar polígonos, o avaliador vê uma marcação por vez,
sorteada, sem saber de que braço veio, e responde se a marcaria como defeito.
Como os quatro braços da D5 são filtros do mesmo cache do SAM (D18), cada
julgamento vale para todos os braços que contêm aquela detecção.

Etapas (cada uma pode ser reexecutada; só refaz o que falta):

  1. sorteia 3 chapas do `test/` por litologia calibrada, com semente fixa
       -> auditoria/amostra.json                    (vai para o git)
  2. garante o cache das 3 vagas de limiar de cada litologia, para TODAS as
     sondas do cadastro: o braço único e o "regra, todas as sondas" precisam
     do joelho das sondas que o autor não admitiu
       -> selectRocks/<rocha>/_cache/                 (gitignored)
  3. captura o SAM no piso nas chapas sorteadas, com todas as sondas
       -> auditoria/<rocha>/_cache/                   (gitignored)
  4. calcula os limiares dos quatro braços
       -> auditoria/limiares.json                   (vai para o git)
  5. reúne as detecções, estratifica, sorteia os itens e monta o pacote
       -> auditoria/itens.json   com braços e pesos  (vai para o git; NÃO vai
                                                      para o avaliador)
       -> auditoria/pacote/      index.html + itens.js + imagens
       -> auditoria/pacote_<id>.zip                   (o que se envia)

Os quatro braços (D5, quarto braço de 10/10/2026):

  unico        todas as sondas, joelho sobre as 11 litologias reunidas
  regra_todas  todas as sondas, joelho da litologia
  regra_autor  sondas admitidas na descoberta, joelho da litologia
  autor        sondas admitidas na descoberta, limiar de trabalho do autor

Uso, a partir de AI/SAM/:

    ..\\.venv\\Scripts\\python.exe auditoria_preparar.py            # tudo
    ..\\.venv\\Scripts\\python.exe auditoria_preparar.py --ate 4    # para antes do pacote
    ..\\.venv\\Scripts\\python.exe auditoria_preparar.py --atualizar-app

`--atualizar-app` só copia o `auditoria_app.html` para `pacote/index.html` e
refaz o .zip. Não sorteia, não captura e não recalcula nada: o `itens.js`, as
imagens e os ids (m001…) ficam como estão, e o progresso salvo no navegador do
avaliador continua valendo (a chave dele é o id do pacote, não o aplicativo).
"""

# ── Monkey-patch CLIP antes de qualquer import do SAM — ver inference.py ──────
# Sem ele o SAM3 falha em silêncio, sem exceção e sem saída.
try:
    import clip as _clip
    import clip.simple_tokenizer as _clip_st
    if "__call__" not in _clip_st.SimpleTokenizer.__dict__:
        _clip_st.SimpleTokenizer.__call__ = (
            lambda self, texts, context_length=77, truncate=False:
            _clip.tokenize(texts, context_length=context_length, truncate=truncate)
        )
except ImportError:
    pass

import argparse
import json

import random
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np

import rock_viewer as protocolo
import sam_cache
from sondas import CLASS_ID_MAP

SAM_DIR = Path(__file__).parent.resolve()
SELECT_ROCKS = SAM_DIR / "selectRocks"
DATASET_DIR = (SAM_DIR / ".." / "dataset").resolve()
AUD = SAM_DIR / "auditoria"
PACOTE = AUD / "pacote"
MODELO = (SAM_DIR / ".." / "models" / "sam3.pt").resolve()

OVERRIDES = dict(task="segment", mode="predict", model=str(MODELO),
                 imgsz=644, half=False, save=False)       # as mesmas do calibrador

PAPEIS_LIMIAR = tuple(p for p in protocolo.PAPEL_CHAVES if p.startswith("limiar_"))
SONDAS = list(CLASS_ID_MAP)                               # o cadastro inteiro (D8)
IMG_EXTS = {".jpg", ".jpeg", ".png"}

SEMENTE = 20261119
CHAPAS_POR_LITOLOGIA = 3
ITENS_ALVO = 420          # tamanho do pacote; o avaliador pode parar antes
CASAS = 4                # as mesmas do calibrador: o limiar da regra sai igual

BRACOS = ("unico", "regra_todas", "regra_autor", "autor")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Amostra de chapas
# ─────────────────────────────────────────────────────────────────────────────

def litologias_calibradas() -> list[str]:
    return sorted(p.parent.name for p in SELECT_ROCKS.glob("*/calibracao.json"))


def ler_calib(rocha: str) -> dict:
    return json.loads((SELECT_ROCKS / rocha / "calibracao.json").read_text(encoding="utf-8"))


def sortear_chapas() -> dict:
    """Sorteia as chapas UMA vez. Depois disso a amostra é lida, nunca refeita.

    Uma semente por litologia (texto, que o `random` trata de forma determinística),
    para que acrescentar uma litologia não mude as chapas das outras.
    """
    arq = AUD / "amostra.json"
    if arq.exists():
        return json.loads(arq.read_text(encoding="utf-8"))
    amostra = {"semente": SEMENTE, "por_litologia": CHAPAS_POR_LITOLOGIA,
               "sorteado_em": datetime.now().isoformat(timespec="seconds"),
               "particao": "test", "chapas": {}}
    for rocha in litologias_calibradas():
        pasta = DATASET_DIR / "test" / rocha
        arquivos = sorted(p.name for p in pasta.iterdir() if p.suffix.lower() in IMG_EXTS)
        rng = random.Random(f"{SEMENTE}-{rocha}")
        amostra["chapas"][rocha] = sorted(rng.sample(arquivos, CHAPAS_POR_LITOLOGIA))
    AUD.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(amostra, indent=2, ensure_ascii=False), encoding="utf-8")
    return amostra


# ─────────────────────────────────────────────────────────────────────────────
# 2 e 3. Captura (GPU)
# ─────────────────────────────────────────────────────────────────────────────

def cache_vaga(rocha: str, papel: str, sonda: str) -> Path:
    return sam_cache.caminho_cache(SELECT_ROCKS / rocha, papel, sonda)


def cache_chapa(rocha: str, arquivo: str, sonda: str) -> Path:
    return sam_cache.caminho_cache(AUD / rocha, Path(arquivo).stem, sonda)


def pendentes(amostra: dict) -> list[tuple[Path, Path, str]]:
    """(imagem, destino do cache, sonda) de tudo que ainda não foi capturado."""
    faltam = []
    for rocha in litologias_calibradas():
        vagas = protocolo.slots_preenchidos(rocha)
        for papel in PAPEIS_LIMIAR:
            for sonda in SONDAS:
                destino = cache_vaga(rocha, papel, sonda)
                if not sam_cache.cache_atual(destino):
                    faltam.append((vagas[papel], destino, sonda))
        for arquivo in amostra["chapas"][rocha]:
            for sonda in SONDAS:
                destino = cache_chapa(rocha, arquivo, sonda)
                if not sam_cache.cache_atual(destino):
                    faltam.append((DATASET_DIR / "test" / rocha / arquivo, destino, sonda))
    return faltam


def capturar(faltam: list[tuple[Path, Path, str]]) -> None:
    """Uma `set_image` por imagem e uma chamada por sonda, como no calibrador."""
    if not faltam:
        print("captura: nada a fazer")
        return
    from ultralytics.models.sam import SAM3SemanticPredictor
    predictor = SAM3SemanticPredictor(overrides=OVERRIDES)
    por_imagem: dict[Path, list[tuple[Path, str]]] = {}
    for img, destino, sonda in faltam:
        por_imagem.setdefault(img, []).append((destino, sonda))
    feitos = 0
    for img, lista in por_imagem.items():
        predictor.set_image(str(img))
        for destino, sonda in lista:
            scores, polys = sam_cache.capturar(predictor, img, sonda)
            sam_cache.salvar(destino, scores, polys)
            feitos += 1
        print(f"  capturado {feitos}/{len(faltam)}  {img.parent.name}/{img.name}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Limiares dos braços
# ─────────────────────────────────────────────────────────────────────────────

def ler_validos(arq: Path) -> tuple[np.ndarray, list]:
    """Sem as detecções de máscara vazia, exatamente como o calibrador conta."""
    scores, polys = sam_cache.carregar(arq)
    ok = sam_cache.indices_validos(polys)
    return scores[ok], [polys[i] for i in ok]


def joelho_de(listas: list[np.ndarray]) -> float | None:
    """O limiar da regra (D17) sobre um conjunto de imagens — a mesma conta do
    `calibrator.limiar_da_regra`: grade de 80 limiares geométricos sobre os scores
    reunidos, curva somada imagem a imagem, joelho, arredondado em 4 casas."""
    todos = np.concatenate(listas) if listas else np.zeros(0, dtype=np.float32)
    if len(todos) == 0:
        return None
    grade = [float(v) for v in sam_cache.limiares_sugeridos(todos, n=80)]
    curva = [(t, sum(int((s > t).sum()) for s in listas)) for t in grade]
    j = sam_cache.joelho(curva)
    return None if j is None else round(j, CASAS)


def calcular_limiares() -> dict:
    import ultralytics

    litos = litologias_calibradas()
    vagas = {(r, p, s): ler_validos(cache_vaga(r, p, s))[0]
             for r in litos for p in PAPEIS_LIMIAR for s in SONDAS}
    saida = {"versao_ultralytics": ultralytics.__version__,
             "calculado_em": datetime.now().isoformat(timespec="seconds"),
             "unico": {}, "litologias": {}}
    for s in SONDAS:
        saida["unico"][s] = joelho_de([vagas[(r, p, s)] for r in litos for p in PAPEIS_LIMIAR])
    for r in litos:
        calib = ler_calib(r)
        admitidas = list(calib["sondas"])
        saida["litologias"][r] = {
            "admitidas": admitidas,
            "regra": {s: joelho_de([vagas[(r, p, s)] for p in PAPEIS_LIMIAR]) for s in SONDAS},
            "regra_registrada": {s: calib["sondas"][s]["limiar_regra"] for s in admitidas},
            "autor": {s: calib["sondas"][s]["limiar_trabalho"] for s in admitidas},
        }
    (AUD / "limiares.json").write_text(json.dumps(saida, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
    return saida


def conferir_regra(lim: dict) -> None:
    """O joelho recalculado aqui deve bater com o gravado pelo calibrador."""
    difs = [(r, s, d["regra"][s], d["regra_registrada"][s])
            for r, d in lim["litologias"].items() for s in d["admitidas"]
            if d["regra"][s] != d["regra_registrada"][s]]
    total = sum(len(d["admitidas"]) for d in lim["litologias"].values())
    print(f"regra recalculada x registrada: {total - len(difs)}/{total} iguais")
    for r, s, novo, velho in difs:
        print(f"  {r:22s} {s:13s} recalculado {novo}  registrado {velho}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Itens e pacote
# ─────────────────────────────────────────────────────────────────────────────

def pertencimento(lim: dict, rocha: str, sonda: str, score: float) -> dict[str, bool]:
    d = lim["litologias"][rocha]
    tu, tr = lim["unico"][sonda], d["regra"][sonda]
    admitida = sonda in d["admitidas"]
    return {
        "unico": tu is not None and score > tu,
        "regra_todas": tr is not None and score > tr,
        "regra_autor": admitida and tr is not None and score > tr,
        "autor": admitida and score > d["autor"][sonda],
    }


def reunir(amostra: dict, lim: dict) -> list[dict]:
    """Toda detecção que ao menos um braço marcaria, nas chapas sorteadas."""
    conjunto = []
    for rocha, arquivos in amostra["chapas"].items():
        for arquivo in arquivos:
            for sonda in SONDAS:
                scores, polys = ler_validos(cache_chapa(rocha, arquivo, sonda))
                for i, (x, pecas) in enumerate(zip(scores, polys)):
                    b = pertencimento(lim, rocha, sonda, float(x))
                    if any(b.values()):
                        conjunto.append({"rocha": rocha, "arquivo": arquivo, "sonda": sonda,
                                         "indice": i, "score": round(float(x), 5),
                                         "bracos": b, "pecas": pecas})
    return conjunto


def estrato(b: dict[str, bool]) -> str:
    return "".join("1" if b[k] else "0" for k in BRACOS)


def sortear_itens(conjunto: list[dict]) -> tuple[list[dict], dict[str, int]]:
    """Amostra estratificada pelo padrão de braços, em ordem intercalada.

    Alocação igual entre estratos (o que sobra de um estrato pequeno vai para os
    outros). Proporcional ao tamanho, o braço do autor, que marca dez a vinte
    vezes menos, quase não apareceria; com a raiz do tamanho, ficava com 54 de
    413 itens. Os pesos da análise (N_h / julgados_h) corrigem a
    sobre-representação dos estratos pequenos.

    A ordem dá a cada item a posição (k + u) / n_h dentro do seu estrato. Assim,
    em qualquer começo da lista, cada estrato aparece na proporção da sua
    alocação: se o avaliador parar no meio, o que ele julgou ainda é amostra.
    """
    rng = random.Random(f"{SEMENTE}-itens")
    por_estrato: dict[str, list[dict]] = {}
    for item in conjunto:
        por_estrato.setdefault(estrato(item["bracos"]), []).append(item)
    tamanhos = {h: len(v) for h, v in por_estrato.items()}
    alocacao, restante = {}, ITENS_ALVO
    for i, h in enumerate(sorted(tamanhos, key=tamanhos.get)):   # do menor ao maior
        cota = restante // (len(tamanhos) - i)
        alocacao[h] = min(tamanhos[h], cota)
        restante -= alocacao[h]
    escolhidos = []
    for h in sorted(por_estrato):
        grupo = rng.sample(por_estrato[h], alocacao[h])
        for k, item in enumerate(grupo):
            escolhidos.append(((k + rng.random()) / alocacao[h], h, item))
    escolhidos.sort(key=lambda t: t[0])
    return [dict(item, estrato=h) for _, h, item in escolhidos], tamanhos


def caixa(pecas: list) -> list[float]:
    pts = np.concatenate([np.asarray(p, dtype=np.float32) for p in pecas])
    return [round(float(v), 5) for v in (*pts.min(axis=0), *pts.max(axis=0))]


def montar_pacote(amostra: dict, itens: list[dict], tamanhos: dict[str, int],
                  por_litologia: dict[str, dict[str, int]]) -> Path:
    """Pacote do avaliador: sem nome de braço, de sonda, de litologia ou de score.

    As imagens vão com nome opaco (c01.jpg…) e inteiras: o recorte e o contorno
    são desenhados no navegador, então o pacote leva 33 imagens, e não 400.
    """
    ident = f"aria-auditoria-{SEMENTE}"
    if PACOTE.exists():
        shutil.rmtree(PACOTE)
    (PACOTE / "imgs").mkdir(parents=True)

    chapas = [(r, a) for r, lista in amostra["chapas"].items() for a in lista]
    rng = random.Random(f"{SEMENTE}-chapas")
    rng.shuffle(chapas)                      # a ordem dos nomes não revela a litologia
    nome_chapa = {}
    for n, (rocha, arquivo) in enumerate(chapas, 1):
        nome = f"c{n:02d}{Path(arquivo).suffix.lower()}"
        shutil.copyfile(DATASET_DIR / "test" / rocha / arquivo, PACOTE / "imgs" / nome)
        nome_chapa[(rocha, arquivo)] = f"imgs/{nome}"

    publicos, privados = [], []
    for n, item in enumerate(itens, 1):
        ident_item = f"m{n:03d}"
        publicos.append({
            "id": ident_item,
            "img": nome_chapa[(item["rocha"], item["arquivo"])],
            "caixa": caixa(item["pecas"]),
            "pecas": [[[round(float(x), 4), round(float(y), 4)] for x, y in p]
                      for p in item["pecas"]],
        })
        privados.append({"id": ident_item, **{k: item[k] for k in
                         ("rocha", "arquivo", "sonda", "indice", "score", "estrato", "bracos")}})

    js = "window.PACOTE = " + json.dumps(
        {"id": ident, "criado": datetime.now().isoformat(timespec="seconds"),
         "itens": publicos}, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (PACOTE / "itens.js").write_text(js, encoding="utf-8")
    shutil.copyfile(SAM_DIR / "auditoria_app.html", PACOTE / "index.html")

    (AUD / "itens.json").write_text(json.dumps(
        {"pacote": ident, "bracos": list(BRACOS), "chapas": len(chapas),
         "tamanho_estrato": tamanhos, "tamanho_estrato_por_litologia": por_litologia,
         "limiares": "auditoria/limiares.json", "itens": privados},
        indent=1, ensure_ascii=False), encoding="utf-8")

    return zipar(ident)


def zipar(ident: str) -> Path:
    zip_arq = AUD / f"pacote_{ident}.zip"
    with zipfile.ZipFile(zip_arq, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(PACOTE.rglob("*")):
            if f.is_file():
                z.write(f, Path("auditoria_aria") / f.relative_to(PACOTE))
    return zip_arq


def atualizar_app() -> None:
    """Troca só o aplicativo do pacote já montado e refaz o .zip."""
    if not (PACOTE / "itens.js").exists():
        print(f"Não há pacote montado em {PACOTE}: nada a atualizar.")
        return
    shutil.copyfile(SAM_DIR / "auditoria_app.html", PACOTE / "index.html")
    zip_arq = zipar(f"aria-auditoria-{SEMENTE}")
    print(f"aplicativo atualizado; itens.js e imagens intactos.\n"
          f"pacote: {zip_arq}  ({zip_arq.stat().st_size / 1e6:.1f} MB)")


def resumo(conjunto: list[dict], itens: list[dict], tamanhos: dict[str, int]) -> None:
    print(f"\nconjunto reunido: {len(conjunto)} detecções em "
          f"{len({(c['rocha'], c['arquivo']) for c in conjunto})} chapas")
    for k in BRACOS:
        print(f"  {k:12s} {sum(c['bracos'][k] for c in conjunto):6d} detecções")
    print("estratos (" + " ".join(BRACOS) + "):")
    alocados = {}
    for it in itens:
        alocados[it["estrato"]] = alocados.get(it["estrato"], 0) + 1
    for h in sorted(tamanhos):
        print(f"  {h}  N = {tamanhos[h]:6d}   sorteados {alocados.get(h, 0):4d}")
    print(f"itens no pacote: {len(itens)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ate", type=int, default=5, help="parar depois da etapa N (1 a 5)")
    ap.add_argument("--refazer-itens", action="store_true",
                    help="sortear os itens e montar o pacote de novo (invalida respostas já dadas)")
    ap.add_argument("--atualizar-app", action="store_true",
                    help="só recopiar o auditoria_app.html para o pacote e refazer o .zip")
    args = ap.parse_args()

    if args.atualizar_app:
        atualizar_app()
        return

    amostra = sortear_chapas()
    print(f"amostra: {sum(len(v) for v in amostra['chapas'].values())} chapas do test/ "
          f"em {len(amostra['chapas'])} litologias")
    if args.ate < 2:
        return
    if (AUD / "itens.json").exists() and not args.refazer_itens:
        # A trava vem ANTES da etapa 4, não só antes da 5: a etapa 4 regrava o
        # `limiares.json` (que vai para o git) com o cache das vagas DESTA
        # máquina. Rodado no outro PC, ou em outra versão do ultralytics, os
        # limiares mudariam por baixo de um pacote já sorteado com os antigos,
        # e o `auditoria_analisar.py` passaria a ler braços que não são os do
        # sorteio. Os ids do pacote (m001…) só valem para ESTE sorteio.
        print("\nitens.json já existe: o pacote já foi montado e pode ter respostas.\n"
              "Nada foi capturado nem recalculado — o limiares.json ficou como está.\n"
              "Para enviar de novo, use o .zip que já está em auditoria/. Só refaça\n"
              "(--refazer-itens) se nenhuma resposta tiver sido dada ainda.")
        return
    capturar(pendentes(amostra))
    if args.ate < 4:
        return
    lim = calcular_limiares()
    conferir_regra(lim)
    print("limiar do braço único: " + ", ".join(f"{s} {t}" for s, t in lim["unico"].items()))
    if args.ate < 5:
        return
    conjunto = reunir(amostra, lim)
    itens, tamanhos = sortear_itens(conjunto)
    por_litologia: dict[str, dict[str, int]] = {}
    for c in conjunto:
        h = estrato(c["bracos"])
        por_litologia.setdefault(c["rocha"], {}).setdefault(h, 0)
        por_litologia[c["rocha"]][h] += 1
    zip_arq = montar_pacote(amostra, itens, tamanhos, por_litologia)
    resumo(conjunto, itens, tamanhos)
    print(f"\npacote: {zip_arq}  ({zip_arq.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
