"""inference.py — o Professor: roda o SAM3 e grava as máscaras e os polígonos.

Processa as imagens de `selectRocks/` e escreve em `results/`. **Isto é o fluxo
de calibração, não o de produção de dataset** — o script de lote sobre o dataset
inteiro ainda não existe (`docs/roadmap.md` → Fase 3.0).

**Só roda sobre litologia calibrada.** O limiar sai do `calibracao.json`, que é o
arquivo que tem limiar *e* critério escrito (D17). Antes, este script tinha três
redes de segurança encadeadas — arquivo ausente virava config vazia, rocha sem
config caía na entrada `"default"`, e a ausência dela caía em três limiares
chumbados no código — então ele **nunca se recusava a rodar**: produzia `.txt` de
rótulo com números inventados, idênticos por fora aos de uma rocha calibrada.
Isso é o oposto da tese do trabalho (D3): o critério tem de ser auditável, e um
`.txt` que não se sabe de onde veio não é auditável.

Hoje: litologia sem calibração é **recusada e listada**, antes de o modelo ser
carregado. Cada pasta de resultado recebe um `procedencia.json` dizendo de onde
saiu cada limiar. Com `--provisorio` dá para rodar a partir do `rock_prompts.json`
(que é provisório — D15) para explorar; o `procedencia.json` grava que foi
provisório, e aí o resultado nunca se confunde com o calibrado.

Uso (de AI/SAM/):
    python inference.py                 # só as litologias calibradas
    python inference.py --provisorio    # aceita rock_prompts.json, e registra isso
"""

import argparse
import json

# Remendo de compatibilidade: o SAM3 do ultralytics faz `self.tokenizer =
# SimpleTokenizer()` e depois o chama como função, mas SimpleTokenizer não tem
# __call__. Delegamos para clip.tokenize. SEM ISTO O MODELO FALHA EM SILÊNCIO —
# sem exceção e sem saída. Tem de vir antes de qualquer import do ultralytics.
try:
    import clip as _clip
    import clip.simple_tokenizer as _clip_st
    if '__call__' not in _clip_st.SimpleTokenizer.__dict__:
        _clip_st.SimpleTokenizer.__call__ = (
            lambda self, texts, context_length=77, truncate=False:
            _clip.tokenize(texts, context_length=context_length, truncate=truncate)
        )
except ImportError:
    pass

from datetime import datetime
from pathlib import Path

import cv2  # pyright: ignore[reportMissingImports]

from ultralytics.models.sam import (  # pyright: ignore[reportMissingImports]
    SAM3SemanticPredictor,
)
from ultralytics.utils.plotting import (  # pyright: ignore[reportMissingImports]
    Annotator,
)

import rock_viewer as protocolo
import sam_cache
import sondas

SAM_DIR = Path(__file__).parent.resolve()
SELECT_ROCKS_DIR = SAM_DIR / "selectRocks"
RESULTS_DIR = SAM_DIR / "results"
PROMPTS_CONFIG_PATH = SAM_DIR / "rock_prompts.json"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

DESENHAR_CAIXAS = False     # as caixas poluem a sobreposição; as máscaras bastam

OVERRIDES = dict(
    task="segment",
    mode="predict",
    model=str(SAM_DIR / ".." / "models" / "sam3.pt"),
    imgsz=644,
    half=False,
    save=False,
)


# ─────────────────────────────────────────────────────────────────────────────
# De onde vem o limiar
# ─────────────────────────────────────────────────────────────────────────────

def ler_prompts_provisorios(caminho: Path) -> dict[str, dict[str, float]]:
    """O `rock_prompts.json`, sem as chaves de comentário e sem o `default`.

    O `default` fica de fora de propósito: usá-lo era justamente o jeito de uma
    rocha sem configuração própria receber limiar de outra sem ninguém notar.
    """
    if not caminho.exists():
        return {}
    with caminho.open(encoding="utf-8") as f:
        dados = json.load(f)
    return {k: v for k, v in dados.items()
            if not k.startswith("_") and k != "default"}


def resolver_config(rocha: str, provisorios: dict, aceitar_provisorio: bool) -> dict:
    """Decide com que limiares (e com que procedência) esta litologia roda.

    Devolve um dicionário com `ok`, `motivo` e, quando `ok`, `sondas` e os
    campos que vão para o `procedencia.json`.
    """
    calib = protocolo.ler_calibracao(rocha)

    if calib and not protocolo.calibracao_desatualizada(rocha, calib):
        return {
            "ok": True,
            "provisorio": False,
            "origem": protocolo.CALIB_NAME,
            "sondas": {s: d["limiar_trabalho"] for s, d in calib["sondas"].items()},
            "calibrado_em": calib.get("calibrado_em"),
            "criterio": calib.get("criterio"),
            "ultralytics_da_calibracao": calib.get("ultralytics"),
        }

    if calib:
        motivo = ("calibração DESATUALIZADA — uma vaga foi substituída depois de "
                  f"{calib.get('calibrado_em', '?')} (vagas: "
                  f"{', '.join(protocolo.vagas_trocadas_depois(rocha, calib))})")
    else:
        motivo = f"sem {protocolo.CALIB_NAME} — não calibrada (D15)"

    if aceitar_provisorio and rocha in provisorios:
        return {
            "ok": True,
            "provisorio": True,
            "origem": "rock_prompts.json (PROVISÓRIO, D15)",
            "sondas": dict(provisorios[rocha]),
            "motivo_do_provisorio": motivo,
        }

    if aceitar_provisorio:
        motivo += "; e também não está no rock_prompts.json"
    return {"ok": False, "motivo": motivo}


def validar_sondas(planos: dict[str, dict]) -> None:
    """Aborta se alguma sonda não está no cadastro — antes de tocar na GPU.

    Sonda sem id de classe caía em `class_id=-1` e gerava `.txt` inválido para
    treino, em silêncio (D8).
    """
    culpadas = {
        rocha: fora
        for rocha, plano in planos.items()
        if (fora := sondas.nao_registradas(plano["sondas"]))
    }
    if culpadas:
        linhas = "\n".join(f"  - {r}: {', '.join(ss)}" for r, ss in culpadas.items())
        raise SystemExit(
            f"[ERRO] Sondas que não estão no cadastro de `sondas.py`:\n{linhas}\n"
            f"Sondas conhecidas: {sondas.conhecidas()}\n"
            "Registre a sonda em sondas.py (um lugar só) ou remova-a da "
            "configuração. Ver docs/decisoes.md D8."
        )


def gravar_procedencia(destino: Path, rocha: str, plano: dict) -> None:
    """Deixa ao lado dos .txt a resposta para 'de onde veio este limiar?'."""
    import ultralytics

    dados = {k: v for k, v in plano.items() if k != "ok"}
    dados.update({
        "rock": rocha,
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "ultralytics": ultralytics.__version__,
        "class_id_por_sonda": {s: sondas.CLASS_ID_MAP[s] for s in plano["sondas"]},
    })
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "procedencia.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Imagens
# ─────────────────────────────────────────────────────────────────────────────

def collect_images(root_dir: Path) -> list[Path]:
    """Todas as imagens sob a pasta, em ordem estável."""
    return sorted(
        p for p in root_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMG_EXTS
    )


def get_rock_name(image_path: Path, dataset_root: Path) -> str:
    """A litologia: o nome do arquivo no layout plano, a pasta-mãe no aninhado."""
    return image_path.stem if image_path.parent == dataset_root else image_path.parent.name


def write_polygons(txt_path: Path, deteccoes, class_id: int) -> None:
    """Acrescenta os polígonos ao .txt no formato YOLO-seg, uma linha por peça.

    `deteccoes` é a saída de `sam_cache.pecas_por_deteccao`: cada detecção do
    SAM é a lista dos seus contornos soltos, e cada contorno vira uma linha
    própria. Não se usa `masks.xyn`, que os fundia numa poligonal só com pontes
    de ida e volta entre eles.
    """
    with txt_path.open("a", encoding="utf-8") as f:
        for pecas in deteccoes:
            for poly in pecas:
                if len(poly) > 2:
                    pts = " ".join([f"{x:.6f} {y:.6f}" for x, y in poly])
                    f.write(f"{class_id} {pts}\n")


def process_image(
    predictor: SAM3SemanticPredictor,
    image_path: Path,
    outputs_dir: Path,
    inputs: dict[str, float],
) -> None:
    """Roda a predição de uma imagem e grava as saídas em disco."""
    rock_name = get_rock_name(image_path, SELECT_ROCKS_DIR)
    rock_dir = outputs_dir / rock_name
    rock_dir.mkdir(parents=True, exist_ok=True)

    image_name = image_path.stem
    image_dir = rock_dir / image_name
    image_dir.mkdir(parents=True, exist_ok=True)

    txt_path = image_dir / f"{image_name}.txt"
    txt_path.write_text("")  # reset

    predictor.set_image(str(image_path))
    im_final = cv2.imread(str(image_path))
    annotator_final = Annotator(im_final, line_width=2, pil=False)

    for prompt, conf in inputs.items():
        print(
            f"Processando '{image_path.name}' ({rock_name}) - prompt='{prompt}' conf={conf}"
        )

        predictor.args.conf = conf
        result = predictor(text=[prompt])[0]

        # Saída individual (uma sonda por arquivo)
        out_individual = image_dir / f"{image_name}_{prompt}_{conf}.jpg"
        cv2.imwrite(str(out_individual), result.plot(boxes=DESENHAR_CAIXAS))

        if result.masks is None:
            continue

        write_polygons(txt_path, sam_cache.pecas_por_deteccao(result),
                       sondas.CLASS_ID_MAP[prompt])

        color = sondas.cor(prompt)
        masks = result.masks.data.cpu().numpy()
        annotator_final.masks(masks, [color] * len(masks))

    combined = annotator_final.result()
    cv2.imwrite(str(image_dir / f"{image_name}_combined.jpg"), combined)


# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument(
        "--provisorio", action="store_true",
        help="aceita os limiares do rock_prompts.json para as litologias sem "
             "calibração (D15). A procedência fica registrada no resultado.",
    )
    args = p.parse_args()

    images = collect_images(SELECT_ROCKS_DIR)
    if not images:
        raise SystemExit(f"Nenhuma imagem encontrada em '{SELECT_ROCKS_DIR}'.")

    por_rocha: dict[str, list[Path]] = {}
    for img in images:
        por_rocha.setdefault(get_rock_name(img, SELECT_ROCKS_DIR), []).append(img)

    provisorios = ler_prompts_provisorios(PROMPTS_CONFIG_PATH)
    decisoes = {r: resolver_config(r, provisorios, args.provisorio) for r in por_rocha}
    planos = {r: d for r, d in decisoes.items() if d["ok"]}
    recusadas = {r: d["motivo"] for r, d in decisoes.items() if not d["ok"]}

    print(f"\n{len(por_rocha)} litologia(s) em {SELECT_ROCKS_DIR.name}/:")
    for rocha in sorted(planos):
        marca = "PROVISÓRIO" if planos[rocha]["provisorio"] else "calibrada"
        print(f"  [{marca:>10}] {rocha}  ({len(por_rocha[rocha])} imagem(ns)) "
              f"← {planos[rocha]['origem']}")
    for rocha in sorted(recusadas):
        print(f"  [  recusada] {rocha}: {recusadas[rocha]}")

    if not planos:
        raise SystemExit(
            "\nNenhuma litologia calibrada para processar. O limiar vem do "
            f"`{protocolo.CALIB_NAME}`, que o calibrador grava junto com o "
            "critério escrito:\n"
            "  python -m streamlit run calibrator.py\n"
            "Para explorar com os limiares provisórios do rock_prompts.json "
            "(D15), rode com --provisorio."
        )

    validar_sondas(planos)

    predictor = SAM3SemanticPredictor(overrides=OVERRIDES)

    for rocha, plano in planos.items():
        gravar_procedencia(RESULTS_DIR / rocha, rocha, plano)
        for img in por_rocha[rocha]:
            process_image(predictor, img, RESULTS_DIR, plano["sondas"])

    print(f"\nProcessamento concluído! Verifique a pasta '{RESULTS_DIR.name}'.")
    if any(p["provisorio"] for p in planos.values()):
        print("ATENÇÃO: há resultado PROVISÓRIO nesta rodada — veja o "
              "procedencia.json de cada litologia antes de usar os .txt.")


if __name__ == "__main__":
    main()
