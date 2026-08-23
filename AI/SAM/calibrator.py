# Monkey-patch CLIP before any SAM import — see inference.py for explanation.
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

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="ARIA Calibrator",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
SAM_DIR         = Path(__file__).parent
SELECT_ROCKS    = SAM_DIR / "selectRocks"
RESULTS_DIR     = SAM_DIR / "results"
PROMPTS_CONFIG  = SAM_DIR / "rock_prompts.json"
DATASET_DIR     = SAM_DIR / "../dataset"
IMG_EXTS        = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
SPLITS          = ("train", "val", "test")

# ── Prompt library ────────────────────────────────────────────────────────────
PROMPT_LIBRARY: dict[str, list[str]] = {
    "Anomalias físicas": [
        "crack", "fracture", "fissure", "scratch", "chip", "pit", "cavity", "spall",
    ],
    "Mineralogia": [
        "vein", "mineral vein", "crystal", "mineral inclusion", "quartz vein",
    ],
    "Manchas / coloração": [
        "Stain", "Dark patches", "light spot", "discoloration",
        "rust stain", "iron stain", "oxidation", "white spot",
    ],
    "Contextuais": [
        "crack on stone surface", "mineral vein in granite",
        "surface defect on rock", "dark stain on marble",
    ],
}
ALL_LIBRARY_PROMPTS = [p for ps in PROMPT_LIBRARY.values() for p in ps]

CLASS_COLORS: dict[str, tuple[int, int, int]] = {
    "vein": (255, 0, 0),
    "crack": (0, 0, 255),
    "Stain": (0, 165, 255),
    "Dark patches": (30, 30, 30),
    "light spot": (255, 255, 0),
    "scratch": (255, 0, 255),
}
# Registro de sondas conhecidas. Uma sonda fora deste mapa NAO pode virar rotulo:
# gravar um class_id invalido corrompe o .txt de treino em silencio. Ver decisoes.md D8.
CLASS_ID_MAP: dict[str, int] = {
    "vein": 0, "crack": 1, "Stain": 2, "Dark patches": 3, "light spot": 4,
    "scratch": 5,
}

def _bgr_to_hex(bgr: tuple[int, int, int]) -> str:
    b, g, r = bgr
    return f"#{r:02x}{g:02x}{b:02x}"

def _hex_to_bgr(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b, g, r)

OVERRIDES = dict(
    task="segment", mode="predict",
    model=str(SAM_DIR / "../models/sam3.pt"),
    imgsz=644, half=False, save=False,
)

# ── Cached SAM predictor ──────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Carregando modelo SAM3… (só na primeira vez)")
def _load_predictor():
    from ultralytics.models.sam import SAM3SemanticPredictor  # noqa
    return SAM3SemanticPredictor(overrides=OVERRIDES)

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_prompts() -> dict:
    if not PROMPTS_CONFIG.exists():
        return {"default": {"crack": 0.1, "vein": 0.007, "Stain": 0.3}}
    with PROMPTS_CONFIG.open(encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def save_prompts(data: dict) -> None:
    raw: dict = {}
    if PROMPTS_CONFIG.exists():
        with PROMPTS_CONFIG.open(encoding="utf-8") as f:
            raw = json.load(f)
    comments = {k: v for k, v in raw.items() if k.startswith("_")}
    with PROMPTS_CONFIG.open("w", encoding="utf-8") as f:
        json.dump({**comments, **data}, f, ensure_ascii=False, indent=2)


def find_all_rocks() -> list[str]:
    rocks: set[str] = set()
    for split in SPLITS:
        d = DATASET_DIR / split
        if d.exists():
            for sub in d.iterdir():
                if sub.is_dir():
                    rocks.add(sub.name)
    return sorted(rocks)


def get_select_image(rock: str) -> Optional[Path]:
    if not SELECT_ROCKS.exists():
        return None
    for f in SELECT_ROCKS.iterdir():
        if f.stem.lower() == rock.lower() and f.suffix.lower() in IMG_EXTS:
            return f
    return None


def rock_status(rock: str) -> str:
    """'no_image' | 'pending' | 'calibrated'"""
    if get_select_image(rock) is None:
        return "no_image"
    d = RESULTS_DIR / rock
    if d.exists() and any(d.rglob("*_combined.jpg")):
        return "calibrated"
    return "pending"


def results_from_disk(rock: str) -> dict[str, Path]:
    """Load result images from results/ for a rock that was already processed."""
    out: dict[str, Path] = {}
    base = RESULTS_DIR / rock
    if not base.exists():
        return out
    for subdir in base.iterdir():
        if not subdir.is_dir():
            continue
        stem = subdir.name
        combined = subdir / f"{stem}_combined.jpg"
        if combined.exists():
            out["_combined"] = combined
        for img in sorted(subdir.glob("*.jpg")):
            if img.name == f"{stem}_combined.jpg":
                continue
            name = img.stem
            if name.startswith(stem + "_"):
                rest = name[len(stem) + 1:]
                # rest = "{prompt}_{conf}" where conf has no underscores
                parts = rest.rsplit("_", 1)
                if len(parts) == 2:
                    out[parts[0]] = img  # key = prompt label
    return out

# ── Session state ─────────────────────────────────────────────────────────────
def _init_state() -> None:
    defaults: dict = {
        "current_rock":  None,   # str | None
        "history":       {},     # {rock: [{ts, config}]}
        "last_results":  {},     # {rock: {label: Path}}
        "run_requested": None,   # dict[str, float] | None
        "custom_prompts": [],    # list[str]
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


def switch_rock(rock: str) -> None:
    prompts = load_prompts()
    config: dict[str, float] = prompts.get(rock, prompts.get("default", {}))
    st.session_state.current_rock = rock
    for prompt in ALL_LIBRARY_PROMPTS:
        _init_prompt_state(rock, prompt, config.get(prompt), prompt in config)
    for cp in st.session_state.custom_prompts:
        _init_prompt_state(rock, f"custom_{cp}", config.get(cp), cp in config, is_custom=True)


def _init_prompt_state(rock: str, key_suffix: str, conf: Optional[float],
                       enabled: bool, is_custom: bool = False) -> None:
    cb  = f"cb_{rock}_{key_suffix}"
    sl  = f"sl_{rock}_{key_suffix}"
    ni  = f"ni_{rock}_{key_suffix}"
    ck  = f"ck_{rock}_{key_suffix}"
    st.session_state[cb] = enabled
    val = float(conf) if conf is not None else 0.1
    st.session_state[sl] = val
    st.session_state[ni] = val
    if ck not in st.session_state:
        default_bgr = CLASS_COLORS.get(key_suffix, (180, 180, 180))
        st.session_state[ck] = _bgr_to_hex(default_bgr)


# ── Callback factories ────────────────────────────────────────────────────────
def _sync_sl_to_ni(sl_key: str, ni_key: str):
    def _cb():
        st.session_state[ni_key] = st.session_state[sl_key]
    return _cb

def _sync_ni_to_sl(sl_key: str, ni_key: str):
    def _cb():
        st.session_state[sl_key] = st.session_state[ni_key]
    return _cb

# ── Inference ─────────────────────────────────────────────────────────────────
def run_sam(rock: str, active: dict[str, float], colors: dict[str, tuple[int, int, int]]) -> dict[str, Path]:
    from ultralytics.utils.plotting import Annotator  # noqa

    img_path = get_select_image(rock)
    if img_path is None:
        st.error("Sem imagem em selectRocks/ para esta rocha.")
        return {}

    predictor = _load_predictor()
    rock_dir = RESULTS_DIR / rock / img_path.stem
    rock_dir.mkdir(parents=True, exist_ok=True)

    txt = rock_dir / f"{img_path.stem}.txt"
    txt.write_text("")

    predictor.set_image(str(img_path))
    im = cv2.imread(str(img_path))
    annotator = Annotator(im, line_width=2, pil=False)

    results: dict[str, Path] = {}
    items = list(active.items())
    bar = st.progress(0.0, text="Iniciando SAM…")

    for i, (prompt, conf) in enumerate(items):
        bar.progress(i / len(items), text=f"Processando `{prompt}`…")
        predictor.args.conf = conf
        result = predictor(text=[prompt])[0]

        out = rock_dir / f"{img_path.stem}_{prompt}_{conf}.jpg"
        cv2.imwrite(str(out), result.plot(boxes=False))
        results[prompt] = out

        if result.masks is not None:
            color = colors.get(prompt, (180, 180, 180))
            masks = result.masks.data.cpu().numpy()
            annotator.masks(masks, [color] * len(masks))
            cid = CLASS_ID_MAP.get(prompt)
            if cid is None:
                # Sonda exploratoria: a mascara aparece no preview, mas NAO entra no .txt.
                # Para promove-la a rotulo, registre-a no CLASS_ID_MAP (aqui e em inference.py).
                st.warning(
                    f"Sonda `{prompt}` nao esta no CLASS_ID_MAP: a mascara e exibida, mas os "
                    "poligonos nao foram gravados no .txt (evitando class_id invalido). "
                    "Registre a sonda no CLASS_ID_MAP para inclui-la no treino."
                )
            else:
                with txt.open("a") as f:
                    for poly in result.masks.xyn:
                        if len(poly) > 2:
                            pts = " ".join(f"{x:.6f} {y:.6f}" for x, y in poly)
                            f.write(f"{cid} {pts}\n")

    combined = rock_dir / f"{img_path.stem}_combined.jpg"
    cv2.imwrite(str(combined), annotator.result())
    results["_combined"] = combined

    bar.progress(1.0, text="✓ Concluído!")
    time.sleep(0.5)
    bar.empty()
    return results

# ── Prompt controls (sidebar) ─────────────────────────────────────────────────
def _render_prompt_row(rock: str, prompt: str, key_suffix: str,
                       label: str) -> Optional[tuple[float, str]]:
    """Renders checkbox + slider + number_input + color_picker for one prompt. Returns (conf, hex_color) or None."""
    cb  = f"cb_{rock}_{key_suffix}"
    sl  = f"sl_{rock}_{key_suffix}"
    ni  = f"ni_{rock}_{key_suffix}"
    ck  = f"ck_{rock}_{key_suffix}"

    if cb not in st.session_state:
        st.session_state[cb] = False
    if sl not in st.session_state:
        st.session_state[sl] = 0.1
    if ni not in st.session_state:
        st.session_state[ni] = 0.1
    if ck not in st.session_state:
        st.session_state[ck] = _bgr_to_hex(CLASS_COLORS.get(key_suffix, (180, 180, 180)))

    enabled = st.checkbox(label, key=cb)
    if not enabled:
        return None

    st.slider(
        "", min_value=0.001, max_value=0.500, step=0.001, format="%.3f",
        key=sl, label_visibility="collapsed",
        on_change=_sync_sl_to_ni(sl, ni),
    )
    col_lbl, col_ni = st.columns([1, 1])
    col_lbl.caption("conf:")
    col_ni.number_input(
        "", min_value=0.001, max_value=0.500, step=0.001, format="%.3f",
        key=ni, label_visibility="collapsed",
        on_change=_sync_ni_to_sl(sl, ni),
    )
    c_lbl, c_picker = st.columns([1, 3])
    c_lbl.caption("cor:")
    c_picker.color_picker("", key=ck, label_visibility="collapsed")
    return float(st.session_state[sl]), st.session_state[ck]

# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🪨 ARIA Calibrator")

        all_rocks = find_all_rocks()
        statuses  = {r: rock_status(r) for r in all_rocks}

        n_cal  = sum(1 for s in statuses.values() if s == "calibrated")
        n_pend = sum(1 for s in statuses.values() if s == "pending")
        n_none = sum(1 for s in statuses.values() if s == "no_image")
        st.caption(f"✅ {n_cal} calibradas · ⏳ {n_pend} pendentes · ⚠️ {n_none} sem imagem")

        st.divider()
        st.markdown("**Rochas**")

        # Scrollable rock list
        with st.container(height=300, border=False):
            for rock in all_rocks:
                icon  = {"calibrated": "✅", "pending": "⏳", "no_image": "⚠️"}[statuses[rock]]
                is_cur = st.session_state.current_rock == rock
                if st.button(
                    f"{icon} {rock}", key=f"btn_{rock}",
                    use_container_width=True,
                    type="primary" if is_cur else "secondary",
                ):
                    if not is_cur:
                        switch_rock(rock)
                        st.rerun()

        rock = st.session_state.current_rock
        if rock is None:
            return

        st.divider()
        st.markdown(f"**Prompts — `{rock}`**")

        active: dict[str, float] = {}
        active_colors: dict[str, tuple[int, int, int]] = {}

        for category, prompts in PROMPT_LIBRARY.items():
            with st.expander(category, expanded=False):
                for prompt in prompts:
                    result = _render_prompt_row(rock, prompt, prompt, f"**{prompt}**")
                    if result is not None:
                        conf, hex_color = result
                        active[prompt] = conf
                        active_colors[prompt] = _hex_to_bgr(hex_color)

        # Custom prompts previously added
        if st.session_state.custom_prompts:
            with st.expander("Personalizados", expanded=True):
                for cp in st.session_state.custom_prompts:
                    result = _render_prompt_row(rock, cp, f"custom_{cp}", f"*{cp}*")
                    if result is not None:
                        conf, hex_color = result
                        active[cp] = conf
                        active_colors[cp] = _hex_to_bgr(hex_color)

        # Add new custom prompt
        st.markdown("**+ Novo prompt**")
        new_p = st.text_input(
            "", placeholder="ex: crack on granite surface",
            key="new_custom_input", label_visibility="collapsed",
        )
        if new_p:
            col_conf, col_add = st.columns([2, 1])
            new_conf = col_conf.number_input(
                "conf", min_value=0.001, max_value=0.500,
                value=0.1, step=0.001, format="%.3f", key="new_custom_conf",
            )
            if col_add.button("Adicionar", use_container_width=True, key="btn_add_custom"):
                if new_p not in st.session_state.custom_prompts:
                    st.session_state.custom_prompts.append(new_p)
                    _init_prompt_state(rock, f"custom_{new_p}", new_conf, True, is_custom=True)
                st.rerun()

        st.divider()

        c1, c2 = st.columns(2)

        # ── Rodar SAM ──────────────────────────────────────────
        if c1.button("▶ Rodar SAM", type="primary", use_container_width=True):
            if not active:
                st.warning("Selecione pelo menos um prompt.")
            elif get_select_image(rock) is None:
                st.error("Sem imagem em selectRocks/.")
            else:
                hist = st.session_state.history.setdefault(rock, [])
                hist.append({"ts": datetime.now().strftime("%H:%M:%S"), "config": dict(active)})
                st.session_state.run_requested = {"prompts": dict(active), "colors": dict(active_colors)}
                st.rerun()

        # ── Salvar ─────────────────────────────────────────────
        if c2.button("💾 Salvar", use_container_width=True):
            if active:
                data = load_prompts()
                data[rock] = active
                save_prompts(data)
                st.success("✓ Salvo em rock_prompts.json")
                # Suggest next pending rock
                pending = [r for r, s in statuses.items() if s == "pending" and r != rock]
                if pending:
                    st.info(f"Próxima: **{pending[0]}**")
                    if st.button(f"→ {pending[0]}", key="btn_next_rock"):
                        switch_rock(pending[0])
                        st.rerun()
            else:
                st.warning("Nenhum prompt ativo para salvar.")

# ── Main area ─────────────────────────────────────────────────────────────────
def render_main() -> None:
    rock = st.session_state.current_rock

    if rock is None:
        st.markdown("""
        ## 🪨 ARIA Calibrator

        Selecione uma rocha na barra lateral para iniciar a calibração de prompts.

        ---

        | Ícone | Status |
        |:---:|---|
        | ✅ | SAM já rodou — resultados em `results/` |
        | ⏳ | Imagem selecionada, aguardando calibração |
        | ⚠️ | Sem imagem — rode `rock_viewer.py` primeiro |

        **Fluxo de calibração:**
        1. Selecione a rocha na sidebar
        2. Ative os prompts desejados e ajuste os valores de confiança
        3. Clique **▶ Rodar SAM** para gerar as máscaras
        4. Avalie os resultados na área principal
        5. Ajuste e rode novamente até ficar satisfeito
        6. Clique **💾 Salvar** para gravar no `rock_prompts.json`
        """)
        return

    # ── Handle SAM run (triggered by sidebar button on previous rerun) ────────
    if st.session_state.run_requested is not None:
        payload = st.session_state.run_requested
        st.session_state.run_requested = None
        results = run_sam(rock, payload["prompts"], payload["colors"])
        st.session_state.last_results[rock] = results
        st.rerun()

    # ── Header ────────────────────────────────────────────────────────────────
    s = rock_status(rock)
    badge = {"calibrated": "✅ Calibrada", "pending": "⏳ Pendente", "no_image": "⚠️ Sem imagem"}[s]
    st.markdown(f"## `{rock}` &nbsp; {badge}")
    st.divider()

    img_path = get_select_image(rock)
    results  = st.session_state.last_results.get(rock) or results_from_disk(rock)

    # ── Top row: original + combined ─────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Original**")
        if img_path:
            st.image(str(img_path), use_container_width=True)
        else:
            st.info("Sem imagem em `selectRocks/`.\nRode `rock_viewer.py` para selecionar.")

    with col2:
        st.markdown("**Combined** (todas as masks)")
        if "_combined" in results:
            st.image(str(results["_combined"]), use_container_width=True)
        elif s == "no_image":
            st.info("Selecione uma imagem primeiro.")
        else:
            st.info("Clique **▶ Rodar SAM** para gerar o resultado.")

    # ── Individual prompt results ─────────────────────────────────────────────
    prompt_results = {k: v for k, v in results.items() if k != "_combined"}
    if prompt_results:
        st.divider()
        st.markdown("**Resultados por prompt**")
        n = len(prompt_results)
        ncols = min(n, 4)
        cols  = st.columns(ncols)
        for i, (label, img_r) in enumerate(prompt_results.items()):
            with cols[i % ncols]:
                st.caption(f"`{label}`")
                st.image(str(img_r), use_container_width=True)

    # ── History ───────────────────────────────────────────────────────────────
    history = st.session_state.history.get(rock, [])
    if history:
        st.divider()
        with st.expander(f"Histórico desta sessão — {len(history)} runs"):
            for entry in reversed(history):
                parts = "  ·  ".join(f"{p}: {c:.3f}" for p, c in entry["config"].items())
                st.text(f"{entry['ts']}    {parts}")

# ── Entry point ───────────────────────────────────────────────────────────────
render_sidebar()
render_main()
