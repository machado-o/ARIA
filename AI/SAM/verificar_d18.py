"""verificar_d18 — prova empírica de que a varredura offline é exata (D18).

A **D18** afirma que rodar o SAM3 uma vez com `conf` no piso e filtrar os scores
offline é **exatamente equivalente** a rodar o SAM de novo em cada limiar. Até
aqui isso estava verificado apenas por leitura do fonte do ultralytics
(`SAM3SemanticPredictor.postprocess`). Este script verifica no modelo que roda
nesta máquina, e é ele que sustenta a afirmação no texto do TCC.

O teste: para cada limiar da amostra, compara
  (a) o que o SAM devolve rodando com `conf = t`
  (b) `sam_cache.filtrar(cache_do_piso, t)`
em número de detecções, scores e vértices dos polígonos.

**Quando passa, o resultado é gravado em `d18_verificado.json`**, indexado pela
versão do ultralytics e versionado no git. É assim que a verificação atravessa as
duas máquinas do autor: a equivalência depende da versão do ultralytics, não da
máquina, então basta ter sido verificada **uma vez** em cada versão, em qualquer
PC. O `ambiente.py` lê esse arquivo e diz se a versão instalada aqui já está
coberta — ninguém precisa lembrar.

Uso:
    ..\\.venv\\Scripts\\python.exe verificar_d18.py
    ..\\.venv\\Scripts\\python.exe verificar_d18.py --rocha siena_white --vaga descoberta
"""

# Monkey-patch CLIP antes de qualquer import do SAM — ver inference.py.
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
import sys
from pathlib import Path

import numpy as np

import sam_cache

REGISTRO = Path("d18_verificado.json")

SELECT_ROCKS = Path("selectRocks")
SONDAS_PADRAO = ("crack", "vein", "Stain", "Dark patches")
LIMIARES = (0.005, 0.02, 0.05, 0.08, 0.12, 0.2, 0.35, 0.5)

OVERRIDES = dict(task="segment", mode="predict", model="../models/sam3.pt",
                 imgsz=644, half=False, save=False)


def rodar_no_limiar(predictor, sonda: str, conf: float):
    """O braço (a): o SAM rodando de verdade com este `conf`."""
    predictor.args.conf = conf
    r = predictor(text=[sonda])[0]
    if r.masks is None:
        return np.zeros(0, dtype=np.float32), []
    return (r.boxes.conf.cpu().numpy().astype(np.float32),
            [np.asarray(p, dtype=np.float32) for p in r.masks.xyn])


def comparar(a, b) -> tuple[bool, str]:
    (sa, pa), (sb, pb) = a, b
    if len(sa) != len(sb):
        return False, f"nº de detecções difere: {len(sa)} != {len(sb)}"
    if len(sa) and not np.array_equal(sa, sb):
        return False, f"scores diferem (máx |Δ| = {np.abs(sa - sb).max():.3e})"
    for i, (x, y) in enumerate(zip(pa, pb)):
        if x.shape != y.shape:
            return False, f"polígono {i}: forma {x.shape} != {y.shape}"
        if x.size and not np.array_equal(x, y):
            return False, f"polígono {i}: vértices diferem"
    return True, "idêntico"


def registrar(comparacoes: int, imagem: Path, args) -> None:
    """Anota no `d18_verificado.json` que esta versão do ultralytics foi verificada.

    Indexado pela versão do ultralytics porque é dela que a equivalência depende
    (o filtro `pred_scores > conf` vive no `postprocess` dela). O arquivo vai para
    o git: verificar numa máquina vale para a outra, desde que a versão seja a
    mesma. Guarda também em que máquina rodou — não porque importe para a prova,
    mas para dar para rastrear depois.
    """
    import json
    import platform
    from datetime import datetime

    import torch
    import ultralytics

    registro = {}
    if REGISTRO.exists():
        registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
    registro[ultralytics.__version__] = {
        "resultado": "equivalente",
        "comparacoes": comparacoes,
        "sondas": list(args.sondas),
        "limiares": list(LIMIARES),
        "imagem": str(imagem).replace("\\", "/"),
        "conf_piso": float(sam_cache.CONF_PISO),
        "verificado_em": datetime.now().isoformat(timespec="seconds"),
        "maquina": platform.node(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "torch": torch.__version__,
        "python": platform.python_version(),
    }
    REGISTRO.write_text(
        json.dumps(dict(sorted(registro.items())), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8")
    print(f"       registrado em {REGISTRO} para o ultralytics {ultralytics.__version__}.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rocha", default=None, help="litologia (padrão: a primeira com vagas)")
    ap.add_argument("--vaga", default="descoberta")
    ap.add_argument("--sondas", nargs="*", default=list(SONDAS_PADRAO))
    args = ap.parse_args()

    rocha = args.rocha
    if rocha is None:
        candidatas = sorted(d.name for d in SELECT_ROCKS.iterdir() if d.is_dir())
        if not candidatas:
            print("[ERRO] selectRocks/ está vazio — rode rock_viewer.py primeiro.")
            return 2
        rocha = candidatas[0]

    imagens = [p for p in (SELECT_ROCKS / rocha).iterdir()
               if p.is_file() and p.stem == args.vaga
               and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}]
    if not imagens:
        print(f"[ERRO] vaga '{args.vaga}' não existe em {rocha}.")
        return 2
    imagem = imagens[0]

    from ultralytics.models.sam import SAM3SemanticPredictor
    from ultralytics.utils import LOGGER
    import logging
    LOGGER.setLevel(logging.WARNING)          # a linha "168 cracks" por chamada polui

    predictor = SAM3SemanticPredictor(overrides=OVERRIDES)
    predictor.set_image(str(imagem))

    print(f"\nD18 — varredura offline × execução real")
    print(f"imagem : {imagem}")
    print(f"piso   : conf = {sam_cache.CONF_PISO}\n")

    falhas = 0
    for sonda in args.sondas:
        scores0, polys0 = sam_cache.capturar(predictor, imagem, sonda)
        print(f"  {sonda}  ({len(scores0)} detecções no piso)")
        for t in LIMIARES:
            real = rodar_no_limiar(predictor, sonda, t)
            offline = sam_cache.filtrar(scores0, polys0, t)
            ok, detalhe = comparar(real, offline)
            marca = "ok " if ok else "FALHA"
            print(f"    conf={t:<6} n={len(real[0]):<4} {marca} {'' if ok else detalhe}")
            falhas += 0 if ok else 1

    print()
    if falhas:
        print(f"[FALHOU] {falhas} limiar(es) divergiram — a D18 NÃO se sustenta "
              "nesta versão do ultralytics. Não usar o cache para calibrar.")
        return 1
    n = len(args.sondas) * len(LIMIARES)
    print(f"[OK] {n} comparações, nenhuma divergência: "
          "filtrar o cache do piso é idêntico a rodar o SAM em cada limiar (D18).")
    registrar(n, imagem, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
