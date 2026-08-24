"""
rock_viewer.py — Visualizador de contact sheet para seleção de imagens representativas.

Gera uma grade HTML com todas as imagens de um tipo de rocha (train/val/test),
abre no navegador para visualização, e copia a imagem escolhida para selectRocks/.

USO:
    python rock_viewer.py              # abre a próxima rocha sem seleção
    python rock_viewer.py ice_leke
    python rock_viewer.py ice_leke --cols 6
"""

import argparse
import json
import shutil
import sys
from functools import lru_cache
import tempfile
import webbrowser
from pathlib import Path

DATASET_DIR = Path("../dataset")
SELECT_ROCKS_DIR = Path("selectRocks")
SPLITS = ("train", "val", "test")

# Imagem de calibracao SO pode sair do train/. O conjunto-ouro sai do test/ (decisoes.md D7):
# calibrar num arquivo de test/ seria ajustar o limiar em cima da propria prova. O val/ fica
# reservado para a validacao do Aluno. Ver decisoes.md D17.
SPLIT_CALIBRACAO = "train"
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}


# Faixas de volume de dados. A ordem de calibracao segue a faixa: A primeiro.
# Fonte: docs/decisoes.md D6 e D15, docs/dataset.md.
FAIXAS = (("A", 1000), ("B", 500), ("C", 200), ("D", 0))


@lru_cache(maxsize=None)
def count_images(rock_name: str) -> int:
    """Total de imagens da rocha somando train/val/test (define a faixa -- D6)."""
    total = 0
    for split in SPLITS:
        rock_dir = DATASET_DIR / split / rock_name
        if rock_dir.exists():
            total += sum(
                1 for p in rock_dir.iterdir()
                if p.is_file() and p.suffix.lower() in IMG_EXTS
            )
    return total


def faixa_of(rock_name: str) -> str:
    n = count_images(rock_name)
    for nome, minimo in FAIXAS:
        if n >= minimo:
            return nome
    return "D"


def find_all_rocks() -> list[str]:
    """Todas as rochas, ordenadas por VOLUME DE DADOS (maior primeiro).

    A ordem nao e alfabetica de proposito: ela e a prioridade de calibracao.
    A faixa A (>=1000 imagens) vem antes de tudo, porque e a faixa do primeiro
    marco entregavel do experimento -- ver docs/decisoes.md D6 e D15.
    """
    rocks: set[str] = set()
    for split in SPLITS:
        split_dir = DATASET_DIR / split
        if split_dir.exists():
            for d in split_dir.iterdir():
                if d.is_dir():
                    rocks.add(d.name)
    return sorted(rocks, key=lambda r: (-count_images(r), r))


def find_selected_rocks() -> set[str]:
    """Retorna nomes (sem extensão) das rochas já em selectRocks/."""
    if not SELECT_ROCKS_DIR.exists():
        return set()
    return {
        f.stem.lower()
        for f in SELECT_ROCKS_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in IMG_EXTS
    }


def find_next_rock() -> str | None:
    """Retorna a primeira rocha que ainda não tem imagem selecionada."""
    selected = find_selected_rocks()
    for rock in find_all_rocks():
        if rock.lower() not in selected:
            return rock
    return None


def collect_images(rock_name: str, todos_os_splits: bool = False) -> list[tuple[str, Path]]:
    """Coleta imagens da rocha, com label de split.

    Por padrao devolve so o train/ -- e de la que a imagem de calibracao pode sair (D17).
    Com todos_os_splits=True devolve tudo, para estudar a variabilidade da rocha; as imagens
    fora do train/ aparecem, mas nao podem ser selecionadas.
    """
    splits = SPLITS if todos_os_splits else (SPLIT_CALIBRACAO,)
    images = []
    for split in splits:
        rock_dir = DATASET_DIR / split / rock_name
        if rock_dir.exists():
            for p in sorted(rock_dir.iterdir()):
                if p.is_file() and p.suffix.lower() in IMG_EXTS:
                    images.append((split, p))
    return images


def build_html(rock_name: str, images: list[tuple[str, Path]], cols: int) -> str:
    cards = []
    img_srcs = []
    img_labels = []
    for i, (split, path) in enumerate(images):
        abs_path = path.resolve().as_posix()
        img_srcs.append(f"file:///{abs_path}")
        img_labels.append(f"{split}/{path.name}")
        cards.append(
            f'<div class="card split-{split}" onclick="openLightbox({i})">'
            f'<div class="num">#{i}</div>'
            f'<img src="file:///{abs_path}" loading="lazy" alt="{path.name}">'
            f'<div class="label">{split}/{path.name}</div>'
            f'</div>'
        )

    cards_html = "\n".join(cards)
    srcs_js = json.dumps(img_srcs)
    labels_js = json.dumps(img_labels)

    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>rock_viewer — {rock_name}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #111; color: #eee; font-family: monospace; }}

  header {{
    position: sticky; top: 0; z-index: 100;
    background: #1a1a1a; border-bottom: 1px solid #333;
    padding: 10px 20px;
    display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  }}
  header h1 {{ font-size: 1rem; color: #aaa; }}
  header strong {{ color: #fff; font-size: 1.1rem; }}
  #badge {{ background: #333; padding: 2px 8px; border-radius: 4px; font-size: 0.85rem; }}

  #selected-bar {{
    background: #0d3a0d; border: 1px solid #2a6a2a; border-radius: 6px;
    padding: 6px 14px; font-size: 0.9rem; display: none;
  }}
  #selected-bar.active {{ display: block; color: #8bc34a; }}

  .grid {{
    display: grid;
    grid-template-columns: repeat({cols}, 1fr);
    gap: 6px;
    padding: 12px;
  }}

  .card {{
    background: #1e1e1e;
    border: 2px solid transparent;
    border-radius: 6px;
    cursor: pointer;
    overflow: hidden;
    transition: border-color 0.15s, transform 0.1s;
  }}
  .card:hover {{ border-color: #555; transform: scale(1.01); }}
  .card.selected {{ border-color: #4caf50 !important; }}

  .card .num {{
    background: #111;
    color: #888;
    font-size: 0.75rem;
    padding: 3px 6px;
  }}
  .card.selected .num {{ color: #4caf50; font-weight: bold; }}

  .card img {{
    width: 100%;
    display: block;
    object-fit: cover;
    aspect-ratio: 1;
  }}

  .card .label {{
    font-size: 0.65rem;
    color: #666;
    padding: 3px 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .card.selected .label {{ color: #8bc34a; }}

  .split-train {{ border-color: #1a3a5c; }}
  .split-val   {{ border-color: #3a2a0a; }}
  .split-test  {{ border-color: #3a0a0a; }}

  .split-train .num::after {{ content: " [train]"; color: #4a9edd; }}
  .split-val   .num::after {{ content: " [val]";   color: #e0a050; }}
  .split-test  .num::after {{ content: " [test]";  color: #cc6666; }}

  /* ── Lightbox ── */
  #lightbox {{
    display: none;
    position: fixed; inset: 0; z-index: 200;
    background: rgba(0,0,0,0.92);
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }}
  #lightbox.open {{ display: flex; }}

  #lb-img {{
    max-width: 92vw;
    max-height: 82vh;
    object-fit: contain;
    border-radius: 4px;
    box-shadow: 0 0 40px rgba(0,0,0,0.8);
    user-select: none;
  }}

  #lb-footer {{
    margin-top: 12px;
    display: flex;
    align-items: center;
    gap: 14px;
  }}

  #lb-label {{
    font-size: 0.85rem;
    color: #aaa;
    min-width: 200px;
    text-align: center;
  }}

  .lb-btn {{
    background: #2a2a2a;
    border: 1px solid #444;
    color: #eee;
    font-family: monospace;
    font-size: 0.85rem;
    padding: 6px 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
  }}
  .lb-btn:hover {{ background: #3a3a3a; border-color: #666; }}
  .lb-btn:active {{ background: #1a1a1a; }}

  #lb-select-btn {{
    background: #1a4a1a;
    border-color: #2a7a2a;
    color: #8bc34a;
    font-weight: bold;
  }}
  #lb-select-btn:hover {{ background: #2a5a2a; border-color: #4a9a4a; }}
  #lb-select-btn.done {{ background: #0d3a0d; border-color: #4caf50; color: #4caf50; }}

  #lb-nav-prev, #lb-nav-next {{
    font-size: 1.4rem;
    padding: 6px 18px;
  }}

  #lb-close {{
    position: fixed;
    top: 16px; right: 20px;
    font-size: 1.5rem;
    background: none;
    border: none;
    color: #888;
    cursor: pointer;
    line-height: 1;
  }}
  #lb-close:hover {{ color: #eee; }}

  #lb-counter {{
    font-size: 0.75rem;
    color: #555;
    min-width: 70px;
    text-align: center;
  }}
</style>
</head>
<body>

<header>
  <h1>rock_viewer /</h1>
  <strong>{rock_name}</strong>
  <span id="badge">{len(images)} imagens</span>
  <div id="selected-bar">
    Selecionado: <span id="sel-text">—</span>
    &nbsp;|&nbsp; Cole o número no terminal e pressione Enter
  </div>
</header>

<div class="grid">
{cards_html}
</div>

<!-- Lightbox -->
<div id="lightbox">
  <button id="lb-close" onclick="closeLightbox()">✕</button>
  <img id="lb-img" src="" alt="">
  <div id="lb-footer">
    <button class="lb-btn" id="lb-nav-prev" onclick="lbNav(-1)">&#8592;</button>
    <span id="lb-counter"></span>
    <button class="lb-btn" id="lb-select-btn" onclick="lbSelect()">Selecionar esta</button>
    <span id="lb-label"></span>
    <button class="lb-btn" id="lb-nav-next" onclick="lbNav(+1)">&#8594;</button>
  </div>
</div>

<script>
  const SRCS   = {srcs_js};
  const LABELS = {labels_js};
  const TOTAL  = SRCS.length;

  let selected = null;
  let lbIndex  = null;

  // ── Grid selection ──────────────────────────────────────────
  function markSelected(i) {{
    if (selected !== null) {{
      document.querySelectorAll('.card')[selected].classList.remove('selected');
    }}
    selected = i;
    const card = document.querySelectorAll('.card')[i];
    card.classList.add('selected');
    card.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    document.getElementById('sel-text').textContent = '#' + i + '  ' + LABELS[i];
    document.getElementById('selected-bar').classList.add('active');
  }}

  // ── Lightbox ─────────────────────────────────────────────────
  function openLightbox(i) {{
    lbIndex = i;
    lbRender();
    document.getElementById('lightbox').classList.add('open');
    document.body.style.overflow = 'hidden';
  }}

  function closeLightbox() {{
    document.getElementById('lightbox').classList.remove('open');
    document.body.style.overflow = '';
  }}

  function lbRender() {{
    document.getElementById('lb-img').src = SRCS[lbIndex];
    document.getElementById('lb-label').textContent = LABELS[lbIndex];
    document.getElementById('lb-counter').textContent = (lbIndex + 1) + ' / ' + TOTAL;

    const btn = document.getElementById('lb-select-btn');
    if (lbIndex === selected) {{
      btn.textContent = '✓ Selecionada';
      btn.classList.add('done');
    }} else {{
      btn.textContent = 'Selecionar esta';
      btn.classList.remove('done');
    }}
  }}

  function lbNav(dir) {{
    lbIndex = (lbIndex + dir + TOTAL) % TOTAL;
    lbRender();
  }}

  function lbSelect() {{
    markSelected(lbIndex);
    lbRender();
  }}

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {{
    if (!document.getElementById('lightbox').classList.contains('open')) return;
    if (e.key === 'Escape')      closeLightbox();
    if (e.key === 'ArrowLeft')   lbNav(-1);
    if (e.key === 'ArrowRight')  lbNav(+1);
    if (e.key === 'Enter')       lbSelect();
  }});

  // Click outside image closes lightbox
  document.getElementById('lightbox').addEventListener('click', (e) => {{
    if (e.target === document.getElementById('lightbox')) closeLightbox();
  }});
</script>
</body>
</html>
"""


def count_pending() -> int:
    selected = find_selected_rocks()
    return sum(1 for r in find_all_rocks() if r.lower() not in selected)


def select_for_rock(rock_name: str, cols: int, todos_os_splits: bool = False) -> bool:
    """Abre o visualizador para uma rocha e aguarda seleção. Retorna True se selecionou."""
    images = collect_images(rock_name, todos_os_splits=todos_os_splits)
    if not images:
        print(f"[ERRO] Nenhuma imagem encontrada para '{rock_name}' em {DATASET_DIR}/")
        return False

    escopo = "train/val/test" if todos_os_splits else f"{SPLIT_CALIBRACAO}/"
    print(
        f"Rocha: {rock_name}  |  faixa {faixa_of(rock_name)}  |  "
        f"{len(images)} imagens ({escopo})"
    )
    if todos_os_splits:
        print(
            f"  [--all] Mostrando os 3 splits para estudo. Só imagens de "
            f"{SPLIT_CALIBRACAO}/ podem ser selecionadas (D17)."
        )

    html = build_html(rock_name, images, cols=cols)
    tmp = tempfile.NamedTemporaryFile(
        suffix=".html", delete=False, mode="w", encoding="utf-8",
        prefix=f"rock_viewer_{rock_name}_"
    )
    tmp.write(html)
    tmp.flush()
    tmp_path = Path(tmp.name)
    tmp.close()

    print(f"Abrindo visualizador no navegador... ({tmp_path.name})")
    webbrowser.open(tmp_path.as_uri())

    print("\nVeja a grade no navegador.")
    print("  - Clique em qualquer imagem para abrir em tela cheia")
    print("  - Use ← → (ou botões) para navegar, Enter para selecionar, Esc para fechar")
    print("\nDigite o número (#) da imagem escolhida e pressione Enter.")
    print("(Deixe em branco e Enter para pular esta rocha)\n")

    selected = False
    while True:
        raw = input("Número da imagem: ").strip()
        if raw == "":
            print("Pulado.")
            break

        try:
            idx = int(raw)
        except ValueError:
            print("  Digite apenas o número.")
            continue

        if idx < 0 or idx >= len(images):
            print(f"  Número inválido. Escolha entre 0 e {len(images) - 1}.")
            continue

        split, chosen = images[idx]

        if split != SPLIT_CALIBRACAO:
            print(
                f"  [BLOQUEADO] {split}/{chosen.name} não pode ser imagem de calibração.\n"
                f"  O conjunto-ouro sai do test/ e o val/ valida o Aluno — calibrar fora do\n"
                f"  {SPLIT_CALIBRACAO}/ contamina a avaliação. Ver docs/decisoes.md D17.\n"
                f"  Escolha uma imagem marcada como {SPLIT_CALIBRACAO}."
            )
            continue

        print(f"\n  Escolhido: {split}/{chosen.name}")

        SELECT_ROCKS_DIR.mkdir(exist_ok=True)
        dest = SELECT_ROCKS_DIR / f"{rock_name}{chosen.suffix.upper()}"

        if dest.exists():
            confirm = input(f"  [AVISO] Já existe {dest.name} em selectRocks/. Sobrescrever? (s/n): ").strip().lower()
            if confirm != "s":
                print("  Não sobrescrito.")
                continue

        shutil.copy2(chosen, dest)
        print(f"  [OK] Copiado para selectRocks/{dest.name}")
        selected = True
        break

    try:
        tmp_path.unlink()
    except Exception:
        pass

    return selected


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Visualizador de contact sheet para seleção de imagens de rocha."
    )
    parser.add_argument(
        "rock", nargs="?", default=None,
        help="Nome da rocha (ex: ice_leke). Omita para iterar pelas pendentes."
    )
    parser.add_argument(
        "--cols", type=int, default=8,
        help="Colunas na grade (padrão: 8)"
    )
    parser.add_argument(
        "--all", dest="todos_os_splits", action="store_true",
        help="Mostra val/ e test/ além do train/, para estudar a variabilidade da rocha. "
             "Só imagens de train/ continuam selecionáveis (docs/decisoes.md D17)."
    )
    args = parser.parse_args()

    if args.rock is not None:
        select_for_rock(args.rock, args.cols, args.todos_os_splits)
        return

    # Modo loop — itera pelas rochas pendentes
    all_rocks = find_all_rocks()
    total = len(all_rocks)

    while True:
        pending = count_pending()
        if pending == 0:
            print("\n[OK] Todas as rochas já foram selecionadas.")
            break

        rock_name = find_next_rock()
        done = total - pending
        faixa = faixa_of(rock_name)
        pend_faixa = sum(
            1 for r in find_all_rocks()
            if faixa_of(r) == faixa and r.lower() not in find_selected_rocks()
        )
        print(
            f"\n── {done}/{total} selecionadas  |  próxima: {rock_name} "
            f"(faixa {faixa}, {count_images(rock_name)} imgs)  |  "
            f"{pend_faixa} pendentes na faixa {faixa} ──"
        )

        select_for_rock(rock_name, args.cols, args.todos_os_splits)

        remaining = count_pending()
        if remaining == 0:
            print("\n[OK] Todas as rochas selecionadas!")
            break

        cont = input(f"\n  {remaining} pendentes. Continuar? [Enter] ou [q] para sair: ").strip().lower()
        if cont == "q":
            print(f"  Saindo. {remaining} rochas ainda pendentes.")
            break


if __name__ == "__main__":
    main()
