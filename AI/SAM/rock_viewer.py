"""rock_viewer — seleção manual das imagens de calibração.

Protocolo D17 (docs/decisoes.md): cada litologia tem 4 vagas com papéis distintos.

    selectRocks/<litologia>/
    ├── descoberta.JPG      define QUAIS sondas entram
    ├── limiar_sutil.JPG    \
    ├── limiar_tipica.JPG    } definem o LIMIAR de confiança
    └── limiar_forte.JPG    /
    └── meta.json           de onde veio cada uma (reprodutibilidade)

A seleção é sempre manual: usar o próprio SAM para escolher a imagem de
calibração seria raciocínio circular.

As litologias são entregues em ordem de VOLUME DE DADOS (faixa A primeiro),
não em ordem alfabética — a ordem é a prioridade de trabalho (D6, D15).

Uso:
    python rock_viewer.py                 # próxima vaga pendente, em ordem de faixa
    python rock_viewer.py <litologia>     # completa as vagas de uma litologia
    python rock_viewer.py --cols 6        # grade mais larga
    python rock_viewer.py --all           # mostra val/ e test/ para estudo (não selecionáveis)
"""

import argparse
import json
import shutil
import sys
import tempfile
import webbrowser
from datetime import datetime
from functools import lru_cache
from pathlib import Path

# O console do Windows abre em cp1252 e o script morre com UnicodeEncodeError no
# primeiro "->" ou "check" das dicas de vaga. Forca UTF-8 na saida; se o terminal
# nao aceitar, degrada o caractere em vez de derrubar a selecao no meio.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

DATASET_DIR = Path("../dataset")
SELECT_ROCKS_DIR = Path("selectRocks")
SPLITS = ("train", "val", "test")
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

# Imagem de calibração SÓ pode sair do train/. O conjunto-ouro sai do test/ (D7):
# calibrar num arquivo de test/ seria ajustar o limiar em cima da própria prova.
# O val/ fica reservado para a validação do Aluno. Ver docs/decisoes.md D17.
SPLIT_CALIBRACAO = "train"

META_NAME = "meta.json"

# Faixas de volume de dados — a ordem de trabalho segue a faixa (D6).
FAIXAS = (("A", 1000), ("B", 500), ("C", 200), ("D", 0))

# As 4 vagas, na ordem em que são preenchidas.
# (chave, rótulo, o que procurar, cor de destaque)
PAPEIS = (
    (
        "descoberta",
        "Descoberta",
        "A chapa com o MAIOR número de tipos diferentes de feição. "
        "Esta imagem decide QUAIS sondas entram para esta litologia — "
        "o que não aparecer aqui, você não vai descobrir.",
        "#a78bfa",
    ),
    (
        "limiar_sutil",
        "Limiar · sutil",
        "Feições fracas, de baixo contraste, daquelas que quase passam batido. "
        "É o caso difícil: define até onde o limiar precisa descer.",
        "#60a5fa",
    ),
    (
        "limiar_tipica",
        "Limiar · típica",
        "A chapa mais comum desta rocha — o que você mais vê. "
        "Nem a mais limpa, nem a mais problemática. É o caso médio.",
        "#4ade80",
    ),
    (
        "limiar_forte",
        "Limiar · forte",
        "Feições marcantes, de alto contraste. "
        "Define até onde o limiar pode subir sem perder o óbvio.",
        "#fbbf24",
    ),
)
PAPEL_INFO = {chave: (rotulo, dica, cor) for chave, rotulo, dica, cor in PAPEIS}
PAPEL_CHAVES = tuple(chave for chave, *_ in PAPEIS)


# ─────────────────────────────────────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def count_images(rock_name: str) -> int:
    """Total de imagens da litologia somando train/val/test (define a faixa — D6)."""
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
    """Litologias ordenadas por VOLUME DE DADOS (maior primeiro).

    A ordem não é alfabética de propósito: ela é a prioridade de calibração.
    A faixa A (>=1000 imagens) vem antes de tudo, porque é a faixa do primeiro
    marco entregável do experimento — ver docs/decisoes.md D6 e D15.
    """
    rocks: set[str] = set()
    for split in SPLITS:
        split_dir = DATASET_DIR / split
        if split_dir.exists():
            for d in split_dir.iterdir():
                if d.is_dir():
                    rocks.add(d.name)
    return sorted(rocks, key=lambda r: (-count_images(r), r))


def collect_images(rock_name: str, todos_os_splits: bool = False) -> list[tuple[str, Path]]:
    """Imagens da litologia, com label de split.

    Por padrão devolve só o train/ — é de lá que a imagem de calibração pode sair (D17).
    Com todos_os_splits=True devolve tudo, para estudar a variabilidade da rocha; as
    imagens fora do train/ aparecem, mas não podem ser selecionadas.
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


# ─────────────────────────────────────────────────────────────────────────────
# Vagas (slots)
# ─────────────────────────────────────────────────────────────────────────────

def rock_slot_dir(rock_name: str) -> Path:
    return SELECT_ROCKS_DIR / rock_name


def slot_path(rock_name: str, papel: str) -> Path | None:
    """Arquivo já gravado nesta vaga, se houver (qualquer extensão de imagem)."""
    d = rock_slot_dir(rock_name)
    if not d.exists():
        return None
    for p in sorted(d.iterdir()):
        if p.is_file() and p.stem == papel and p.suffix.lower() in IMG_EXTS:
            return p
    return None


def slots_preenchidos(rock_name: str) -> dict[str, Path]:
    return {
        papel: p
        for papel in PAPEL_CHAVES
        if (p := slot_path(rock_name, papel)) is not None
    }


def proximo_papel(rock_name: str) -> str | None:
    """Primeira vaga ainda vazia desta litologia, na ordem dos papéis."""
    preenchidos = slots_preenchidos(rock_name)
    for papel in PAPEL_CHAVES:
        if papel not in preenchidos:
            return papel
    return None


def find_next_rock() -> str | None:
    """Primeira litologia com vaga pendente, em ordem de faixa."""
    for rock in find_all_rocks():
        if proximo_papel(rock) is not None:
            return rock
    return None


def contar_progresso() -> tuple[int, int]:
    """(vagas preenchidas, vagas totais) em todo o dataset."""
    rocks = find_all_rocks()
    feitas = sum(len(slots_preenchidos(r)) for r in rocks)
    return feitas, len(rocks) * len(PAPEL_CHAVES)


def ler_meta(rock_name: str) -> dict:
    f = rock_slot_dir(rock_name) / META_NAME
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"rock": rock_name, "slots": {}}


def gravar_meta(rock_name: str, papel: str, split: str, origem: Path, destino: Path) -> None:
    """Registra de onde veio cada imagem — material de reprodutibilidade para o TCC."""
    meta = ler_meta(rock_name)
    meta["rock"] = rock_name
    meta["faixa"] = faixa_of(rock_name)
    meta["total_imagens_litologia"] = count_images(rock_name)
    meta.setdefault("slots", {})[papel] = {
        "arquivo": destino.name,
        "origem": f"{split}/{origem.name}",
        "selecionado_em": datetime.now().isoformat(timespec="seconds"),
    }
    d = rock_slot_dir(rock_name)
    d.mkdir(parents=True, exist_ok=True)
    (d / META_NAME).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ─────────────────────────────────────────────────────────────────────────────
# HTML
# ─────────────────────────────────────────────────────────────────────────────

_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>__ROCK__ · __PAPEL_ROTULO__</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:      #0d0f12;
    --surface: #16191f;
    --line:    #262b34;
    --text:    #e6e9ef;
    --muted:   #8b93a3;
    --accent:  __COR__;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font: 14px/1.5 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    padding-bottom: 40px;
  }

  header {
    position: sticky; top: 0; z-index: 100;
    background: rgba(13, 15, 18, 0.92);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--line);
  }

  .bar {
    display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap;
    padding: 14px 22px 10px;
  }
  .rock {
    font-size: 1.15rem; font-weight: 650; letter-spacing: -0.01em;
    font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
  }
  .chip {
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em;
    padding: 3px 9px; border-radius: 999px;
    background: var(--surface); border: 1px solid var(--line); color: var(--muted);
  }
  .chip.faixa { color: var(--accent); border-color: color-mix(in srgb, var(--accent) 40%, var(--line)); }
  .spacer { flex: 1; }
  .count { color: var(--muted); font-size: 0.82rem; }

  /* vagas */
  .slots { display: flex; gap: 8px; padding: 0 22px 12px; flex-wrap: wrap; }
  .slot {
    display: flex; align-items: center; gap: 7px;
    padding: 5px 11px 5px 7px; border-radius: 8px;
    background: var(--surface); border: 1px solid var(--line);
    font-size: 0.78rem; color: var(--muted);
  }
  .slot .dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--line); flex: none;
  }
  .slot.feito .dot  { background: #3fb950; }
  .slot.feito       { color: #7d8590; }
  .slot.atual {
    border-color: var(--accent); color: var(--text);
    box-shadow: 0 0 0 1px var(--accent) inset;
  }
  .slot.atual .dot  { background: var(--accent); animation: pulse 1.8s ease-in-out infinite; }
  @keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: 0.35 } }
  .slot img { width: 22px; height: 22px; object-fit: cover; border-radius: 4px; }

  /* instrução do papel */
  .brief {
    margin: 0 22px 14px; padding: 13px 16px;
    border-left: 3px solid var(--accent); border-radius: 0 8px 8px 0;
    background: color-mix(in srgb, var(--accent) 7%, var(--surface));
  }
  .brief h2 {
    font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.1em;
    color: var(--accent); margin-bottom: 5px; font-weight: 600;
  }
  .brief p { color: var(--text); max-width: 78ch; }
  .brief .hint { color: var(--muted); font-size: 0.82rem; margin-top: 7px; }

  /* grade */
  .grid {
    display: grid;
    grid-template-columns: repeat(__COLS__, minmax(0, 1fr));
    gap: 8px; padding: 0 16px;
  }
  .card {
    position: relative; background: var(--surface);
    border: 1px solid var(--line); border-radius: 9px;
    overflow: hidden; cursor: pointer;
    transition: border-color .14s, transform .1s;
  }
  .card:hover { border-color: var(--accent); transform: translateY(-2px); }
  .card.sel   { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent); }
  .card img   { display: block; width: 100%; aspect-ratio: 1; object-fit: cover; }
  .card .n {
    position: absolute; top: 6px; left: 6px;
    background: rgba(0,0,0,.72); color: #fff;
    font: 600 0.7rem ui-monospace, monospace;
    padding: 2px 6px; border-radius: 5px;
  }
  .card .lbl {
    padding: 5px 7px; font: 0.68rem ui-monospace, monospace;
    color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .card.bloq { opacity: .38; cursor: not-allowed; }
  .card.bloq:hover { border-color: #f85149; transform: none; }
  .card.bloq .lbl { color: #f85149; }

  /* lightbox */
  #lb {
    position: fixed; inset: 0; z-index: 500; display: none;
    background: rgba(6,7,9,.96); align-items: center; justify-content: center;
    flex-direction: column; gap: 14px; padding: 26px;
  }
  #lb.on { display: flex; }
  #lb img { max-width: 92vw; max-height: 78vh; object-fit: contain; border-radius: 8px; }
  #lb .meta { color: var(--muted); font: 0.85rem ui-monospace, monospace; }
  #lb .nav { display: flex; gap: 10px; align-items: center; }
  #lb button {
    background: var(--surface); color: var(--text);
    border: 1px solid var(--line); border-radius: 7px;
    padding: 7px 15px; cursor: pointer; font-size: 0.85rem;
  }
  #lb button:hover { border-color: var(--accent); }
  #lb button.go { background: var(--accent); color: #0d0f12; font-weight: 650; border-color: var(--accent); }

  kbd {
    background: var(--surface); border: 1px solid var(--line);
    border-bottom-width: 2px; border-radius: 4px;
    padding: 1px 5px; font: 0.75rem ui-monospace, monospace; color: var(--muted);
  }
</style>
</head>
<body>

<header>
  <div class="bar">
    <span class="rock">__ROCK__</span>
    <span class="chip faixa">faixa __FAIXA__</span>
    <span class="chip">__TOTAL_IMGS__ imagens</span>
    <span class="spacer"></span>
    <span class="count">__ESCOPO__ · __N_IMGS__ selecionáveis</span>
  </div>
  <div class="slots">__SLOTS__</div>
  <div class="brief">
    <h2>Vaga __IDX_PAPEL__ de 4 · __PAPEL_ROTULO__</h2>
    <p>__PAPEL_DICA__</p>
    <p class="hint">Clique para ampliar · <kbd>←</kbd> <kbd>→</kbd> navegam · <kbd>Esc</kbd> fecha ·
       o número escolhido vai no terminal.</p>
  </div>
</header>

<div class="grid">__CARDS__</div>

<div id="lb" onclick="if(event.target.id==='lb')fechar()">
  <img id="lbimg" alt="">
  <div class="meta" id="lbmeta"></div>
  <div class="nav">
    <button onclick="mover(-1)">← anterior</button>
    <button class="go" onclick="marcar()">marcar esta (#<span id="lbn"></span>)</button>
    <button onclick="mover(1)">próxima →</button>
  </div>
</div>

<script>
const SRCS   = __SRCS__;
const LABELS = __LABELS__;
const BLOQ   = __BLOQ__;
let idx = 0, sel = null;

function abrir(i) {
  idx = i;
  document.getElementById('lbimg').src = SRCS[i];
  document.getElementById('lbmeta').textContent = '#' + i + '  ' + LABELS[i]
    + (BLOQ[i] ? '   ⛔ fora do train/ — não pode ser calibração' : '');
  document.getElementById('lbn').textContent = i;
  document.getElementById('lb').classList.add('on');
}
function fechar() { document.getElementById('lb').classList.remove('on'); }
function mover(d) {
  let n = idx + d;
  if (n >= 0 && n < SRCS.length) abrir(n);
}
function marcar() {
  if (BLOQ[idx]) { alert('Esta imagem está fora do train/ e não pode ser usada na calibração (D17).'); return; }
  document.querySelectorAll('.card').forEach(c => c.classList.remove('sel'));
  document.querySelectorAll('.card')[idx].classList.add('sel');
  sel = idx;
  fechar();
  document.querySelectorAll('.card')[idx].scrollIntoView({ block: 'center', behavior: 'smooth' });
}
document.addEventListener('keydown', e => {
  if (!document.getElementById('lb').classList.contains('on')) return;
  if (e.key === 'Escape')     fechar();
  if (e.key === 'ArrowLeft')  mover(-1);
  if (e.key === 'ArrowRight') mover(1);
  if (e.key === 'Enter')      marcar();
});
</script>
</body>
</html>
"""


def build_html(
    rock_name: str,
    images: list[tuple[str, Path]],
    cols: int,
    papel: str,
    preenchidos: dict[str, Path],
    todos_os_splits: bool,
) -> str:
    rotulo, dica, cor = PAPEL_INFO[papel]

    cards, srcs, labels, bloq = [], [], [], []
    for i, (split, path) in enumerate(images):
        uri = "file:///" + path.resolve().as_posix()
        travada = split != SPLIT_CALIBRACAO
        srcs.append(uri)
        labels.append(f"{split}/{path.name}")
        bloq.append(travada)
        cards.append(
            f'<div class="card{" bloq" if travada else ""}" onclick="abrir({i})">'
            f'<div class="n">{i}</div>'
            f'<img src="{uri}" loading="lazy" alt="">'
            f'<div class="lbl">{split}/{path.name}</div>'
            f"</div>"
        )

    slots_html = []
    for j, chave in enumerate(PAPEL_CHAVES):
        rot = PAPEL_INFO[chave][0]
        if chave == papel:
            classe = "slot atual"
            thumb = ""
        elif chave in preenchidos:
            classe = "slot feito"
            thumb = f'<img src="file:///{preenchidos[chave].resolve().as_posix()}" alt="">'
        else:
            classe = "slot"
            thumb = ""
        slots_html.append(f'<div class="{classe}"><span class="dot"></span>{thumb}{rot}</div>')

    n_selecionaveis = sum(1 for s, _ in images if s == SPLIT_CALIBRACAO)
    escopo = "train + val + test (estudo)" if todos_os_splits else "somente train/"

    subs = {
        "__ROCK__": rock_name,
        "__FAIXA__": faixa_of(rock_name),
        "__TOTAL_IMGS__": f"{count_images(rock_name):,}".replace(",", "."),
        "__ESCOPO__": escopo,
        "__N_IMGS__": str(n_selecionaveis),
        "__COLS__": str(cols),
        "__COR__": cor,
        "__PAPEL_ROTULO__": rotulo,
        "__PAPEL_DICA__": dica,
        "__IDX_PAPEL__": str(PAPEL_CHAVES.index(papel) + 1),
        "__SLOTS__": "\n".join(slots_html),
        "__CARDS__": "\n".join(cards),
        "__SRCS__": json.dumps(srcs),
        "__LABELS__": json.dumps(labels),
        "__BLOQ__": json.dumps(bloq),
    }
    html = _TEMPLATE
    for k, v in subs.items():
        html = html.replace(k, v)
    return html


# ─────────────────────────────────────────────────────────────────────────────
# Seleção
# ─────────────────────────────────────────────────────────────────────────────

def preencher_vaga(
    rock_name: str, papel: str, cols: int, todos_os_splits: bool = False
) -> bool:
    """Abre o visualizador para uma vaga e aguarda a escolha. True se preencheu."""
    images = collect_images(rock_name, todos_os_splits=todos_os_splits)
    if not images:
        print(f"[ERRO] Nenhuma imagem para '{rock_name}' em {DATASET_DIR}/")
        return False

    rotulo, dica, _ = PAPEL_INFO[papel]
    n = PAPEL_CHAVES.index(papel) + 1
    preenchidos = slots_preenchidos(rock_name)

    print(f"\n  {rock_name}  ·  faixa {faixa_of(rock_name)}  ·  vaga {n}/4 — {rotulo}")
    print(f"  → {dica}")
    if preenchidos:
        ja = ", ".join(PAPEL_INFO[k][0] for k in PAPEL_CHAVES if k in preenchidos)
        print(f"  (já preenchidas: {ja})")
    if todos_os_splits:
        print(f"  [--all] val/ e test/ aparecem para estudo, mas não são selecionáveis (D17).")

    html = build_html(rock_name, images, cols, papel, preenchidos, todos_os_splits)
    tmp = tempfile.NamedTemporaryFile(
        suffix=".html", delete=False, mode="w", encoding="utf-8",
        prefix=f"rock_viewer_{rock_name}_{papel}_",
    )
    tmp.write(html)
    tmp.flush()
    tmp_path = Path(tmp.name)
    tmp.close()
    webbrowser.open(tmp_path.as_uri())

    while True:
        raw = input(f"  número da imagem [{rotulo}] (Enter pula): ").strip()
        if raw == "":
            print("  pulada.")
            return False
        try:
            idx = int(raw)
        except ValueError:
            print("  digite apenas o número.")
            continue
        if not 0 <= idx < len(images):
            print(f"  fora do intervalo (0 a {len(images) - 1}).")
            continue

        split, chosen = images[idx]
        if split != SPLIT_CALIBRACAO:
            print(
                f"  [BLOQUEADO] {split}/{chosen.name} não serve como imagem de calibração.\n"
                f"  O conjunto-ouro sai do test/ e o val/ valida o Aluno — calibrar fora do\n"
                f"  {SPLIT_CALIBRACAO}/ contamina a avaliação (docs/decisoes.md D17)."
            )
            continue

        destino_dir = rock_slot_dir(rock_name)
        destino_dir.mkdir(parents=True, exist_ok=True)
        destino = destino_dir / f"{papel}{chosen.suffix.upper()}"

        anterior = slot_path(rock_name, papel)
        if anterior is not None and anterior != destino:
            anterior.unlink()

        shutil.copy2(chosen, destino)
        gravar_meta(rock_name, papel, split, chosen, destino)
        print(f"  ✓ {split}/{chosen.name}  →  {destino.relative_to(SELECT_ROCKS_DIR.parent)}")
        return True


def completar_rocha(rock_name: str, cols: int, todos_os_splits: bool) -> bool:
    """Preenche todas as vagas pendentes de uma litologia. False se o usuário parou."""
    while (papel := proximo_papel(rock_name)) is not None:
        if not preencher_vaga(rock_name, papel, cols, todos_os_splits):
            return False
    print(f"\n  ✓ {rock_name} completa — 4/4 vagas.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seleção manual das 4 imagens de calibração por litologia (D17)."
    )
    parser.add_argument(
        "rock", nargs="?", default=None,
        help="Litologia (ex: siena_white). Omita para seguir a ordem de faixa.",
    )
    parser.add_argument("--cols", type=int, default=8, help="Colunas na grade (padrão: 8)")
    parser.add_argument(
        "--all", dest="todos_os_splits", action="store_true",
        help="Mostra val/ e test/ além do train/, para estudar a variabilidade. "
             "Só imagens de train/ continuam selecionáveis (docs/decisoes.md D17).",
    )
    args = parser.parse_args()

    if not DATASET_DIR.exists():
        raise SystemExit(f"[ERRO] Dataset não encontrado em {DATASET_DIR.resolve()}")

    if args.rock is not None:
        if proximo_papel(args.rock) is None:
            print(f"{args.rock} já tem as 4 vagas preenchidas.")
            return
        completar_rocha(args.rock, args.cols, args.todos_os_splits)
        return

    while True:
        feitas, total = contar_progresso()
        rock_name = find_next_rock()
        if rock_name is None:
            print(f"\n[OK] Todas as {total} vagas preenchidas.")
            break

        faixa = faixa_of(rock_name)
        pend_faixa = sum(
            1 for r in find_all_rocks()
            if faixa_of(r) == faixa and proximo_papel(r) is not None
        )
        print(
            f"\n── {feitas}/{total} vagas  ·  próxima: {rock_name} "
            f"(faixa {faixa})  ·  {pend_faixa} litologias pendentes na faixa {faixa} ──"
        )

        if not completar_rocha(rock_name, args.cols, args.todos_os_splits):
            feitas, total = contar_progresso()
            print(f"\n  Saindo. {total - feitas} vagas pendentes.")
            break

        if input("\n  [Enter] próxima litologia · [q] sair: ").strip().lower() == "q":
            feitas, total = contar_progresso()
            print(f"  Saindo. {total - feitas} vagas pendentes.")
            break


if __name__ == "__main__":
    main()
