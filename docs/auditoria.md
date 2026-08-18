# Auditoria do Repositório — ARIA

> Levantamento geral feito em **2026-08-18** (Claude Code), do bug de código à nomenclatura de
> pastas. Nada foi corrigido ainda — isto é só a lista de achados, para revisar com calma em
> outra sessão.
>
> **Formato de revisão combinado:** ao resolver, ir **um item por vez**. Claude explica o item
> (o que é, onde está, por que importa) e o Henrique classifica: **problema** (corrigir) ou
> **decisão não documentada** (na verdade está certo, só falta registrar em `decisoes.md`/outro
> `.md`). Marcar `[x]` ao resolver, com uma linha dizendo qual foi a decisão.

---

## A. Bug de código real — `AI/SAM/`

- [ ] **A1 — `class_id = -1` gravado para `giallo_maracana`.**
  `rock_prompts.json:164` tem `"scratch": 0.06` para `giallo_maracana`. `CLASS_ID_MAP` em
  `inference.py:43-49` e `calibrator.py:65-67` só mapeia `vein, crack, Stain, Dark patches,
  light spot` — sem `scratch`. `write_polygons()` faz `CLASS_ID_MAP.get(prompt, -1)`: sem match,
  cai em `-1` **silenciosamente**, sem warning, sem exceção. O `.txt` gerado para essa rocha tem
  uma linha com `class_id -1`, formato inválido para treino YOLO.

- [ ] **A2 — Causa raiz: `calibrator.py` oferece prompts que o pipeline não reconhece.**
  A `PROMPT_LIBRARY` do calibrador (`calibrator.py:40-55`) tem **21 prompts** em 4 categorias
  (`fracture, fissure, scratch, chip, pit, cavity, spall, mineral vein, crystal, mineral
  inclusion, quartz vein, discoloration, rust stain, iron stain, oxidation, white spot` + 4
  contextuais). O `CLASS_ID_MAP` só conhece 5 (decisão **D6** em `decisoes.md`). Qualquer um dos
  outros 16, se ativado e salvo, repete o bug A1. A ferramenta convida ao erro.

---

## B. Inconsistência acadêmica crítica — já diagnosticada, não corrigida

`docs/revisao-artigo.md` (2026-07-01) já levantou e priorizou estes dois pontos como os de maior
retorno. Confirmei em 2026-08-18 que **nenhum foi aplicado**.

- [ ] **B1 — Orientador errado no artigo SBC.** Decisão registrada em `revisao-artigo.md` (A.1):
  Rafael Silva Guimarães = orientador do TCC; Everson Scherrer Borges = professor do PD1; o
  artigo deveria listar Rafael. `apresentacao/roteiro.md` e `pd1.html` já foram corrigidos. Mas
  `Overleaf/artigo/main.tex:17` (bloco de autor) e `:22` (`eversonborges@gmail.com`) ainda têm
  Everson.

- [ ] **B2 — Artigo ainda chama SAM3 de "SAM".** Marcado ⚠️ "mais atacável por um revisor" em
  `revisao-artigo.md` (F2.1). `grep -c "SAM3" Overleaf/artigo/main.tex` = **0**. O texto todo diz
  "SAM" e cita `sam_kirillov2023` (SAM v1, 2023) — modelo diferente do que roda de fato (SAM3 via
  Ultralytics, conforme `arquitetura.md`). Mesmo problema nos slides 5, 6, 7, 10 da apresentação
  (item A.2 do `revisao-artigo.md`, não verificado a fundo nesta auditoria).

- [ ] **B3 — Caixa inconsistente de "stain"/"Stain" no artigo.** Já era F1.9 em
  `revisao-artigo.md`. Confirmado via grep: minúsculo e maiúsculo convivendo no mesmo `main.tex`.

---

## C. `CLAUDE.md` erra sobre o próprio repositório

- [ ] **C1 — Afirma que `rock_prompts.json` e `selectRocks/` são gitignored — não são.**
  `.gitignore` só tem `results/`. `git check-ignore` confirma: `rock_prompts.json` e as 13
  imagens de `selectRocks/` estão **versionadas**. Isso é lido como fonte de verdade em toda
  sessão — instrução errada aqui se propaga.

- [ ] **C2 — "Typo conhecido `whte_liberdade`" não existe mais no arquivo rastreado.**
  `rock_prompts.json` já tem `white_liberdade` (correto). A nota provavelmente descrevia uma
  cópia local antiga.

---

## D. Lacuna no mapa de documentação do `CLAUDE.md`

- [ ] **D1 — Três coisas existem no repo e não aparecem na tabela "Mapa da documentação":**
  - `docs/revisao-artigo.md` (tem itens ⚠️ críticos ainda abertos — deveria estar no mapa)
  - `apresentacao/` (roteiro + HTML da apresentação do PD1)
  - `LatinoWare2026/` (submissão paralela para o Latin.Science 2026, com README de contexto
    próprio)

---

## E. Estrutura / nomenclatura de pastas

- [ ] **E1 — Convenção de nomes inconsistente no topo do repo.** `AI` (sigla maiúscula), `docs`
  (minúsculo), `Overleaf` (PascalCase), `apresentacao` (minúsculo, sem acento), `LatinoWare2026`
  (CamelCase colado com ano). Sem padrão único.

- [ ] **E2 — Pasta de template cru versionada com sufixo de download duplicado.**
  `LatinoWare2026/Exemplo_do_IEEE_adaptado_para_o_Latin_Science_2026 (1)/` — o `" (1)"` é marca
  clássica de download repetido do navegador, nunca renomeada. O próprio `LatinoWare2026/README.md`
  já descreve essa pasta como "template original baixado do site" (arquivo de referência, não de
  trabalho) — candidata a rename ou remoção.

- [ ] **E3 — Zip binário redundante versionado.** `LatinoWare2026/artigo-overleaf.zip` (5,8 MB,
  commitado em 2026-08-18) duplica o conteúdo já extraído em `LatinoWare2026/artigo/`. Zip
  versionado não tem diff útil e infla o histórico do repo.

- [ ] **E4 — Três pastas "artigo" diferentes, sem sinalização no nome.**
  `Overleaf/artigo/` (SBC/PD1), `LatinoWare2026/artigo/` (IEEE/Latin Science),
  `LatinoWare2026/Exemplo.../ (1)` (template cru). A distinção está documentada em prosa nos
  READMEs, mas nada no nome da pasta indica isso — fácil de abrir a errada.

---

## F. Itens já conhecidos no projeto — cross-check de que seguem abertos

Não são achados novos desta auditoria; já estavam em `pendencias.md` ou `revisao-artigo.md`.
Confirmei que continuam sem correção em 2026-08-18:

- [ ] **F1 — Typo "Convulacionais"** no título (`Overleaf/TCC/macros.tex:3`) → deveria ser
  "Convolucionais".
- [ ] **F2 — Título usa "avarias"**, mas `diretrizes-escrita.md` §7.1 define "anomalia" como
  termo canônico do projeto.
- [ ] **F3 — `Overleaf/TCC/bibliografia.bib` vazio** (0 linhas); só `bibliografiaTeste.bib`
  (genérica, 63 linhas) tem conteúdo.
- [ ] **F4 — Ficha catalográfica desalinhada consigo mesma.** `macros.tex:43` cita "Borges,
  Everson Scherrer" na catalogação, enquanto o campo `\orientador` (linha 17, mesmo arquivo) já
  usa Rafael Silva Guimarães.
- [ ] **F5 — `Hartheus.md` ainda descreve a branch `feat/matheus`**, que `pendencias.md` diz
  explicitamente que não existe mais, pedindo para purgar as referências.

---

## Prioridade sugerida

Risco real de prejudicar entrega (vs. só organização):

1. **A1/A2** — dado de treino corrompido (`class_id -1`).
2. **B1** — nome errado de orientador no artigo que vai pra banca.
3. **B2** — SAM vs SAM3, ponto mais atacável por revisor.
4. Resto (C–F) — consistência e organização, sem risco de quebrar nada.
