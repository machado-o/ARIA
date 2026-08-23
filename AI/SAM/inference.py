import json
# Compatibility patch: ultralytics SAM3 sets self.tokenizer = SimpleTokenizer() and calls it
# as a function, but SimpleTokenizer has no __call__. Delegate to clip.tokenize instead.
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

import cv2 # pyright: ignore[reportMissingImports]
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ultralytics.models.sam import ( # pyright: ignore[reportMissingImports]
    SAM3SemanticPredictor,
)
from ultralytics.utils.plotting import ( # pyright: ignore[reportMissingImports]
    Annotator,
)

DATASET_DIR = Path("selectRocks")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PROMPTS_CONFIG_PATH = Path("rock_prompts.json")

draw_boxes_individual = False
draw_boxes_combined = False

CLASS_COLORS: Dict[str, Tuple[int, int, int]] = {
    "vein": (255, 0, 0),
    "crack": (0, 0, 255),
    "Stain": (0, 165, 255),
    "Dark patches": (0, 0, 0),
    "light spot": (255, 255, 0),
    "scratch": (255, 0, 255),
}

# Registro de sondas conhecidas. Uma sonda fora deste mapa nao pode virar rotulo --
# ver validate_prompts() abaixo e docs/decisoes.md D8.
CLASS_ID_MAP: Dict[str, int] = {
    "vein": 0,
    "crack": 1,
    "Stain": 2,
    "Dark patches": 3,
    "light spot": 4,
    "scratch": 5,
}


def validate_prompts(rock_prompts: Dict[str, Dict[str, float]]) -> None:
    # Aborta antes de tocar a GPU se alguma rocha usa sonda fora do CLASS_ID_MAP.
    # Antes, uma sonda nao registrada caia em class_id=-1 e gerava um .txt invalido
    # para treino -- em silencio, sem excecao e sem aviso.
    offenders: Dict[str, List[str]] = {}
    for rock, prompts in rock_prompts.items():
        unknown = [p for p in prompts if p not in CLASS_ID_MAP]
        if unknown:
            offenders[rock] = unknown
    if offenders:
        lines = "\n".join(f"  - {rock}: {', '.join(ps)}" for rock, ps in offenders.items())
        raise SystemExit(
            "[ERRO] Sondas nao registradas em CLASS_ID_MAP:\n"
            f"{lines}\n"
            f"Sondas conhecidas: {', '.join(CLASS_ID_MAP)}\n"
            "Registre a sonda no CLASS_ID_MAP (inference.py e calibrator.py) ou remova-a "
            "de rock_prompts.json. Ver docs/decisoes.md D8."
        )

def load_rock_prompts(config_path: Path) -> Dict[str, Dict[str, float]]:
    """Load per-rock prompt configurations from JSON. Falls back to empty dict on error."""
    if not config_path.exists():
        print(f"[WARN] {config_path} not found — using hardcoded defaults for all rocks.")
        return {}
    with config_path.open(encoding="utf-8") as f:
        data = json.load(f)
    # strip comment keys
    return {k: v for k, v in data.items() if not k.startswith("_")}


def get_prompts_for_rock(
    rock_name: str, rock_prompts: Dict[str, Dict[str, float]]
) -> Dict[str, float]:
    """Return the prompt→confidence dict for a rock, falling back to 'default'."""
    if rock_name in rock_prompts:
        return rock_prompts[rock_name]
    if "default" in rock_prompts:
        print(f"[INFO] No specific config for '{rock_name}' — using default prompts.")
        return rock_prompts["default"]
    # last-resort hardcoded fallback
    return {"crack": 0.1, "vein": 0.007, "Stain": 0.3}


OVERRIDES = dict(
    task="segment",
    mode="predict",
    model="../models/sam3.pt",
    imgsz=644,
    half=False,
    save=False,
)

def collect_images(root_dir: Path) -> List[Path]:
    """Collect image paths from the dataset directory."""
    return sorted(
        p
        for p in root_dir.rglob("*")
        if p.is_file()
        and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
    )


def get_rock_name(image_path: Path, dataset_root: Path) -> str:
    """Return the rock name: file stem for flat selectRocks layout, parent folder for nested."""
    return image_path.stem if image_path.parent == dataset_root else image_path.parent.name


def write_polygons(
    txt_path: Path, polygons: List[List[Tuple[float, float]]], class_id: int
) -> None:
    """Save polygon coordinates to a text file."""
    with txt_path.open("a", encoding="utf-8") as f:
        for poly in polygons:
            if len(poly) > 2:
                pts = " ".join([f"{x:.6f} {y:.6f}" for x, y in poly])
                f.write(f"{class_id} {pts}\n")

def process_image(
    predictor: SAM3SemanticPredictor,
    image_path: Path,
    outputs_dir: Path,
    inputs: Dict[str, float],
) -> None:
    """Run prediction for one image and save outputs to disk."""
    rock_name = get_rock_name(image_path, DATASET_DIR)
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

        # Individual output image (1 prompt per file)
        out_individual = image_dir / f"{image_name}_{prompt}_{conf}.jpg"
        cv2.imwrite(str(out_individual), result.plot(boxes=draw_boxes_individual))

        if result.masks is None:
            continue

        write_polygons(txt_path, result.masks.xyn, CLASS_ID_MAP[prompt])

        color = CLASS_COLORS.get(prompt, (255, 255, 255))
        masks = result.masks.data.cpu().numpy()
        annotator_final.masks(masks, [color] * len(masks))

        if draw_boxes_combined and result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()
            for i, box in enumerate(boxes):
                score = scores[i] if i < len(scores) else conf
                annotator_final.box_label(box, f"{prompt} {score:.2f}", color=color)

    combined = annotator_final.result()
    cv2.imwrite(str(image_dir / f"{image_name}_combined.jpg"), combined)

def main() -> None:
    images = collect_images(DATASET_DIR)
    if not images:
        raise SystemExit(
            f"Nenhuma imagem encontrada em '{DATASET_DIR}'. Verifique a pasta Dataset."
        )

    rock_prompts = load_rock_prompts(PROMPTS_CONFIG_PATH)
    validate_prompts(rock_prompts)
    predictor = SAM3SemanticPredictor(overrides=OVERRIDES)

    for img in images:
        rock_name = get_rock_name(img, DATASET_DIR)
        inputs = get_prompts_for_rock(rock_name, rock_prompts)
        process_image(predictor, img, RESULTS_DIR, inputs)

    print("\nProcessamento concluído! Verifique a pasta 'results'.")

if __name__ == "__main__":
    main()