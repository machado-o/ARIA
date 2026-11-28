"""marcar — transforma achados de revisão (trecho + nota) em marcas importáveis no revisao_pdf.html.

É o caminho inverso do mapear.py: o Claude escreve os achados num .json e este script
acha cada trecho no PDF compilado e grava as marcas com a posição na página.

Uso, a partir da raiz (precisa do PyMuPDF, fora do venv; ver docs/pendencias.md):
    python revisao/marcar.py achados.json main.pdf revisao/marcas/saida.json ["[Claude · sessão] "]
achados.json: [{"cat": "mover", "busca": "trecho exato do PDF", "nota": "...",
                "ocorrencia": 0, "pagina_min": 1}]   # os dois últimos são opcionais
"""
import json, sys, time, random, string
from datetime import datetime, timezone
import fitz  # PyMuPDF

CATS_EXTRA = [{"id": "mover", "nome": "Mover", "cor": "#ec4899",
               "descricao": "mudar de lugar; a nota diz para onde"}]

import re, unicodedata
def norm(s):
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r"[^0-9a-z]", "", "".join(c for c in s if not unicodedata.combining(c)).lower())

achados = json.load(open(sys.argv[1], encoding="utf-8"))
doc = fitz.open(sys.argv[2])
marcas, faltou = [], []
for k, a in enumerate(achados):
    hits = []  # (página, [rects]) — uma lista por ocorrência
    for pno in range(doc.page_count):
        pg = doc[pno]
        # search_for devolve um quad por linha; agrupa quads consecutivos numa ocorrência
        qs = pg.search_for(a["busca"], quads=True)
        if not qs:
            continue
        # cada ocorrência começa num quad cujo texto é o início da busca; heurística: separa
        # quando a linha seguinte não está logo abaixo ou à direita
        inicio = norm(a["busca"])[:10]
        grupo = [qs[0]]
        for q in qs[1:]:
            ant = grupo[-1].rect
            r = q.rect
            abaixo = (r.y0 > ant.y0 + 1 and r.y0 - ant.y1 < ant.height * 1.5)
            ao_lado = abs(r.y0 - ant.y0) < 1 and abs(r.x0 - ant.x1) < ant.height
            comeca = norm(pg.get_textbox(r + (-1, -1, 1, 1))).startswith(inicio)
            if (abaixo or ao_lado) and not comeca:
                grupo.append(q)
            else:
                hits.append((pno, grupo)); grupo = [q]
        hits.append((pno, grupo))
    hits = [h for h in hits if h[0] + 1 >= a.get("pagina_min", 1)]
    occ = a.get("ocorrencia", 0)
    if len(hits) <= occ:
        faltou.append((k, a["busca"], len(hits)))
        continue
    pno, grupo = hits[occ]
    W, H = doc[pno].rect.width, doc[pno].rect.height
    f = lambda v: round(v, 4)
    linhas = []  # junta os pedaços da mesma linha (a ligadura fi/fl parte a busca)
    for q in grupo:
        r = fitz.Rect(q.rect)
        if linhas and abs(r.y0 - linhas[-1].y0) < 1:
            linhas[-1] |= r
        else:
            linhas.append(r)
    rects = [{"p": pno + 1, "x": f(r.x0 / W), "y": f(r.y0 / H),
              "w": f(r.width / W), "h": f(r.height / H)} for r in linhas]
    sufixo = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    marcas.append({
        "id": f"cl{int(time.time()*1000):x}{k:02d}{sufixo}",
        "pagina": pno + 1,
        "categoria": a["cat"],
        "texto": a["busca"],
        "comentario": (sys.argv[4] if len(sys.argv) > 4 else "[Claude · estrutura] ") + a["nota"],
        "rects": rects,
        "criada_em": datetime.now(timezone.utc).isoformat(),
        "n_ocorrencias": len(hits),
    })

saida = {"formato": "aria-revisao/1", "pdf": "main.pdf", "impressao": "",
         "exportado_em": datetime.now(timezone.utc).isoformat(),
         "categorias": CATS_EXTRA, "marcas": marcas}
json.dump(saida, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for m in marcas:
    print(f'ok p.{m["pagina"]:>3} [{m["categoria"]}] ({m["n_ocorrencias"]}x) {m["texto"][:60]}')
for k, b, n in faltou:
    print(f"FALTOU #{k} ({n} achados): {b}")
