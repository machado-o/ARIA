"""mapear — liga cada marca da revisão em PDF ao trecho do .tex de onde ela saiu.

O `revisao_pdf.html` grava o texto como ele aparece no PDF: sem comandos LaTeX,
com ligaduras, com a hifenização da quebra de linha e, às vezes, com espaços a
mais ou a menos. Este script reduz os dois lados (PDF e .tex) ao mesmo esqueleto
(só letras e números, minúsculos, sem espaço) e procura um no outro. Como a
monografia tem um parágrafo por linha, a resposta é `arquivo.tex:linha`.

Aceita as duas saídas do aplicativo:
  - o `.json` do botão "Exportar .json";
  - o texto do botão "Copiar para o Claude", salvo num arquivo .txt.

Uso, a partir da raiz do repositório:
    AI\\.venv\\Scripts\\python.exe revisao\\mapear.py revisao\\marcas\\revisao_main_....json
    AI\\.venv\\Scripts\\python.exe revisao\\mapear.py marcas.txt --tcc apresentações/Overleaf/TCC
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TCC_PADRAO = RAIZ / "apresentações" / "Overleaf" / "TCC"
PASTAS = ("textuais", "pre_textuais", "pos_textuais")

# Comandos cujo argumento não aparece no PDF como texto (ou aparece como número).
SEM_TEXTO = r"cite|citeonline|ref|eqref|autoref|label|includegraphics|input|graphicspath|hspace|vspace"


def esqueleto(s: str) -> str:
    """Só letras e números, minúsculos, sem acento nem espaço."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^0-9a-z]", "", s.lower())


def tex_para_texto(linha: str) -> str:
    """O que uma linha de LaTeX vira, aproximadamente, no PDF."""
    s = re.sub(r"(?<!\\)%.*", "", linha)                                  # comentário
    s = re.sub(rf"\\(?:{SEM_TEXTO})\*?(?:\[[^\]]*\])?\{{[^}}]*\}}", " ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", s)                  # \textit, \section...
    s = re.sub(r"\\(.)", r"\1", s)                                        # \% \_ \&
    return s


def carregar_tex(tcc: Path) -> list[tuple[str, int, str, str]]:
    """(arquivo relativo, nº da linha, linha original, esqueleto)."""
    linhas = []
    arquivos = [a for p in PASTAS for a in sorted((tcc / p).glob("*.tex"))]
    arquivos += sorted(tcc.glob("*.bib"))                 # a lista de referências mora aqui
    for arq in arquivos:
        rel = arq.relative_to(tcc).as_posix()
        for n, l in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
            esq = esqueleto(tex_para_texto(l))
            if len(esq) >= 8:
                linhas.append((rel, n, l, esq))
    return linhas


def ler_marcas(arq: Path) -> list[dict]:
    texto = arq.read_text(encoding="utf-8")
    try:
        return json.loads(texto)["marcas"]
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    # Formato do "Copiar para o Claude":  12. [MUDAR] p. 34: "trecho"  /  nota: ...
    marcas, atual = [], None
    for l in texto.splitlines():
        m = re.match(r'\s*\d+\.\s+\[([^\]]+)\]\s+p\.\s*(\d+):\s+"(.*)"\s*$', l)
        if m:
            atual = {"categoria": m[1].lower(), "pagina": int(m[2]), "texto": m[3], "comentario": ""}
            marcas.append(atual)
        elif atual and (n := re.match(r"\s*nota:\s?(.*)$", l)):
            atual["comentario"] = n[1]
        elif atual and atual["comentario"] and l.startswith("         "):
            atual["comentario"] += "\n" + l.strip()
    return marcas


def localizar(alvo: str, linhas) -> list[tuple[float, str, int]]:
    """Linhas candidatas, da melhor para a pior: (confiança 0–1, arquivo, linha)."""
    if not alvo:
        return []
    exatas = [(1.0, a, n) for a, n, _, esq in linhas if alvo in esq]
    if exatas:
        return exatas
    # Sem casamento exato (marca que atravessa parágrafos, fórmula, legenda de
    # figura...): a linha com o maior pedaço contínuo em comum.
    notas = []
    for a, n, _, esq in linhas:
        sm = SequenceMatcher(None, alvo, esq, autojunk=False)
        bloco = sm.find_longest_match(0, len(alvo), 0, len(esq)).size
        notas.append((bloco / len(alvo), a, n))
    notas.sort(reverse=True)
    return [x for x in notas[:3] if x[0] >= 0.25]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("marcas", type=Path, help=".json exportado ou .txt copiado do aplicativo")
    ap.add_argument("--tcc", type=Path, default=TCC_PADRAO)
    args = ap.parse_args()

    marcas = ler_marcas(args.marcas)
    linhas = carregar_tex(args.tcc)
    sem = 0
    for i, m in enumerate(sorted(marcas, key=lambda m: m.get("pagina", 0)), 1):
        achados = localizar(esqueleto(m["texto"]), linhas)
        trecho = m["texto"] if len(m["texto"]) <= 140 else m["texto"][:137] + "..."
        print(f'{i}. [{m["categoria"].upper()}] p. {m.get("pagina", "?")}: "{trecho}"')
        if m.get("comentario"):
            print(f'   nota: {m["comentario"]}')
        if not achados:
            sem += 1
            print("   -> não encontrado no .tex")
        elif achados[0][0] == 1.0:
            onde = ", ".join(f"{a}:{n}" for _, a, n in achados[:4])
            print(f"   -> {onde}" + ("  (trecho repetido)" if len(achados) > 1 else ""))
        else:
            print("   -> provável: " + ", ".join(f"{a}:{n} ({c:.0%})" for c, a, n in achados))
    print(f"\n{len(marcas)} marcas · {len(marcas) - sem} localizadas · {sem} não encontradas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
