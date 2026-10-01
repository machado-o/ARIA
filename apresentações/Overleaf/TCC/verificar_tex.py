"""verificar_tex — conferência estrutural do LaTeX, para quem não tem LaTeX instalado.

Não substitui a compilação no Overleaf. Pega a classe de erro que mais custa
tempo num ciclo de compilação remoto: \\cite sem entrada no .bib, \\ref sem
\\label, ambiente aberto e não fechado, chave desbalanceada e \\includegraphics
apontando para arquivo que não existe.

Uso:  python verificar_tex.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).parent
BIB = RAIZ / "bibliografia.bib"
FIGURAS = RAIZ / "figuras"

# Um % não escapado inicia comentário; \% não.
COMENTARIO = re.compile(r"(?<!\\)%.*$")


def sem_comentarios(texto: str) -> str:
    return "\n".join(COMENTARIO.sub("", linha) for linha in texto.splitlines())


def arquivos_tex() -> list[Path]:
    return sorted(p for p in RAIZ.rglob("*.tex") if ".git" not in p.parts)


def chaves(padrao: str, texto: str) -> list[str]:
    """Extrai as chaves de comandos como \\cite{a,b} — uma lista achatada."""
    achadas = []
    for grupo in re.findall(padrao, texto):
        achadas += [k.strip() for k in grupo.split(",") if k.strip()]
    return achadas


def main() -> int:
    problemas: list[str] = []
    avisos: list[str] = []

    corpos = {p: sem_comentarios(p.read_text(encoding="utf-8")) for p in arquivos_tex()}

    # ── 1. ambientes e chaves ────────────────────────────────────────────────
    for p, s in corpos.items():
        abre = re.findall(r"\\begin\{([a-zA-Z*]+)\}", s)
        fecha = re.findall(r"\\end\{([a-zA-Z*]+)\}", s)
        for amb in set(abre) | set(fecha):
            if abre.count(amb) != fecha.count(amb):
                problemas.append(
                    f"{p.name}: ambiente '{amb}' abre {abre.count(amb)}x e fecha {fecha.count(amb)}x"
                )
        saldo = len(re.findall(r"(?<!\\)\{", s)) - len(re.findall(r"(?<!\\)\}", s))
        if saldo:
            problemas.append(f"{p.name}: chaves desbalanceadas (saldo {saldo:+d})")

    # ── 2. citações ──────────────────────────────────────────────────────────
    if not BIB.exists():
        problemas.append("bibliografia.bib não existe")
        disponiveis: set[str] = set()
    else:
        disponiveis = set(re.findall(r"^@\w+\{([^,]+),", BIB.read_text(encoding="utf-8"),
                                     re.MULTILINE))
    usadas: dict[str, str] = {}
    for p, s in corpos.items():
        for k in chaves(r"\\cite(?:online)?\{([^}]*)\}", s):
            usadas.setdefault(k, p.name)
    for k, onde in sorted(usadas.items()):
        if k in disponiveis:
            continue
        (avisos if k.startswith("TODO") else problemas).append(
            f"{onde}: \\cite{{{k}}} " + ("é marcador TODO — preencher antes de submeter"
                                         if k.startswith("TODO") else "sem entrada no .bib")
        )
    nao_usadas = disponiveis - set(usadas)
    if nao_usadas:
        avisos.append(f"{len(nao_usadas)} entradas do .bib não citadas "
                      f"(o bibtex simplesmente as omite): {', '.join(sorted(nao_usadas))}")

    # ── 3. referências cruzadas ──────────────────────────────────────────────
    rotulos = {k for s in corpos.values() for k in chaves(r"\\label\{([^}]*)\}", s)}
    for p, s in corpos.items():
        for k in chaves(r"\\(?:auto|eq|page)?ref\{([^}]*)\}", s):
            if k not in rotulos:
                problemas.append(f"{p.name}: \\ref{{{k}}} sem \\label correspondente")
    duplicados = [r for r in rotulos
                  if sum(s.count("\\label{" + r + "}") for s in corpos.values()) > 1]
    for r in duplicados:
        problemas.append(f"\\label{{{r}}} declarado mais de uma vez")

    # ── 4. figuras referenciadas ─────────────────────────────────────────────
    for p, s in corpos.items():
        for arq in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]*)\}", s):
            nome = Path(arq)
            achou = (FIGURAS / arq).exists() or any(
                (FIGURAS / f"{nome.stem}{ext}").exists()
                for ext in (".png", ".jpg", ".jpeg", ".pdf", ".eps")
            )
            if not achou:
                problemas.append(f"{p.name}: \\includegraphics{{{arq}}} — arquivo ausente "
                                 "em figuras/ (isto INTERROMPE a compilação)")

    # ── 5. \input existentes ─────────────────────────────────────────────────
    for p, s in corpos.items():
        for alvo in re.findall(r"\\input\{([^}]*)\}", s):
            cam = RAIZ / (alvo if alvo.endswith(".tex") else alvo + ".tex")
            if not cam.exists():
                problemas.append(f"{p.name}: \\input{{{alvo}}} — arquivo não existe")

    # ── saída ────────────────────────────────────────────────────────────────
    print(f"{len(corpos)} arquivos .tex · {len(disponiveis)} entradas no .bib · "
          f"{len(usadas)} chaves citadas · {len(rotulos)} rótulos\n")
    for a in avisos:
        print(f"  aviso   {a}")
    for e in problemas:
        print(f"  PROBLEMA {e}")
    if problemas:
        print(f"\n{len(problemas)} problema(s). Corrigir antes de compilar.")
        return 1
    print("\nNenhum problema estrutural. (Isto NÃO é uma compilação — "
          "o veredito final é o Overleaf.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
