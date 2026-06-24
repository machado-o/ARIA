# Pendências — ARIA

> Caixa de entrada de coisas a fazer/corrigir que **não** são marcos grandes do
> desenvolvimento (esses ficam no `roadmap.md`). Itens soltos de escrita, template, docs e
> código. Marcar `[x]` ao concluir; remover quando virar irrelevante.
>
> Abra a sessão lendo `CLAUDE.md` + este arquivo.
>
> Última atualização: 2026-06-24

---

## 📰 Artigo SBC (entrega PD1) — `Overleaf/artigo/`

Entrega do Projeto de Diplomação I: artigo científico completo no template SBC (10–12
páginas). Estrutura, status e gotchas do template → **[`artigo-sbc.md`](artigo-sbc.md)**.
O `Overleaf/` tem duas pastas: **`TCC/`** (monografia) e **`artigo/`** (SBC). O artigo está
completo, em conformidade com o SBC e compilando (~11 páginas); segue só refino de texto.

- [x] **Main document re-apontado / sync resolvido** — conflito Overleaf↔GitHub resolvido; projeto
  compila a partir de `artigo/main.tex`.
- [x] **Compila no Overleaf** (~11 páginas); `subfig`, `sbc-template` e bibliografia fecham.
- [x] **Autoria** — Henrique Machado de Oliveira; orientador Everson Scherrer Borges; e-mails
  pessoais dos dois no cabeçalho (decisão: sem institucional).
- [x] **Diagrama da arquitetura** — feito em TikZ (vetorial) em `\label{fig:arquitetura}`.
- [x] **Bibliografia** (`referencias.bib`) — consolidada das `.bib` do grupo + canônicas; 32 refs,
  todas citadas (1:1). `.bib` temporários da raiz já apagados.
- [ ] **Refino de texto** — leitura parágrafo a parágrafo com o Henrique (em andamento).

## ✍️ Escrita / `.tex` — alinhar com as decisões

Correções no `Overleaf/TCC/textuais/Texto Inicial.tex` (rascunho real do TCC), pendentes desde o
diagnóstico de 2026-06-10:

- [X] **Remover o Aprendizado Ativo do corpo do texto** (ref. teórico + passo 5 da metodologia).
  Removido. ⚠️ **Falta** adicioná-lo à seção de Trabalhos Futuros (que ainda é stub em
  `conclusao.tex`). Ver `decisoes.md` D8.
- [X] **Remover a menção a Docker** — removido das Ferramentas. Ver `decisoes.md`.
- [X] **Alinhar nomes ARIA × Hartheus** — "sistema Hartheus" → "sistema ARIA"; Hartheus
  apresentado como a plataforma no Tema Delimitado. Ver `decisoes.md` D1.
- [X] **Inserir o experimento central 45 × 1** — nova subseção "Protocolo Experimental" na
  metodologia. Ver `decisoes.md` D3.
- [X] **Documentar a rotulagem binária** (`class_id=0`) — adicionada ao passo de calibração do
  Professor. Ver `decisoes.md` D2.
- [X] **Trocar "Label Studio"** por validação qualitativa por especialistas. Ver `decisoes.md` D5.

> Pendente relacionado: escrever a seção de **Trabalhos Futuros** (em `conclusao.tex`) contemplando
> Aprendizado Ativo (D8), rotulagem multiclasse (D9) e integração com a plataforma Hartheus.

## 📄 Template / LaTeX da monografia (`Overleaf/TCC/`)

- [ ] Corrigir typo do título: **"Convulacionais" → "Convolucionais"**.
- [ ] Decidir/fixar o título definitivo (há 4 alternativas comentadas em `macros.tex`).
- [ ] Ficha catalográfica com dados-dummy do template (tags de Criptografia/IoT; cita "Borges,
  Everson Scherrer" como orientador). Orientador real: **Rafael Silva Guimarães**.
- [ ] Preencher `palavraschave` / `keywords` (hoje "Palavra Chave 1...").
- [ ] Escrever o **resumo** real (PT) e o **abstract** (EN) — hoje são o texto-instrução do
  template.
- [ ] Substituir os stubs `introducao.tex`, `ref_teorico.tex`, `conclusao.tex` (boilerplate do
  template) pelo conteúdo real — ou consolidar a estrutura a partir do `Texto Inicial.tex`.
- [ ] Deletar `Overleaf/textuais/testes.tex` (demo do template) quando não for mais útil.
- [ ] Inserir a figura da arquitetura do pipeline (placeholder em `\label{fig:arquitetura_hartheus}`).

## 📚 Bibliografia da monografia (`Overleaf/TCC/`)

> O artigo SBC já tem sua bibliografia pronta (`Overleaf/artigo/referencias.bib`). Os itens abaixo
> são da **monografia**.

- [ ] `Overleaf/TCC/bibliografia.bib` está **vazio**; só `bibliografiaTeste.bib` tem entradas (genéricas).
- [ ] Adicionar referências do domínio: **SAM, YOLO, Xception, CLIP, Teacher-Student/Knowledge
  Distillation, Indústria 4.0, TAM, Difusão de Inovações, inspeção visual automatizada (AVI)**.

## 🧩 Código

- [ ] (sem itens soltos no momento — marcos de desenvolvimento estão no `roadmap.md`)

## 📁 Docs

- [ ] 🔔 **Atualizar o `Hartheus.md`** (ex-`PROJETO.md`) com os arquivos do Hartheus que o Henrique
  vai passar. O contexto mudou: a branch **`feat/matheus` não existe mais**. Ao atualizar, purgar as
  referências restantes a `feat/matheus` no `Hartheus.md` (seções de branches/comparação).
  → **Claude: lembrar o Henrique de te passar os arquivos ao retomar a sessão.**
- [ ] (manter este arquivo e os `.md` de contexto sem informação duplicada — princípio DRY)
