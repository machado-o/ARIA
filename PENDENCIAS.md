# Pendências — ARIA

> Caixa de entrada de coisas a fazer/corrigir que **não** são marcos grandes do
> desenvolvimento (esses ficam no `ROADMAP.md`). Itens soltos de escrita, template, docs e
> código. Marcar `[x]` ao concluir; remover quando virar irrelevante.
>
> Abra a sessão lendo `CLAUDE.md` + este arquivo.
>
> Última atualização: 2026-06-10

---

## ✍️ Escrita / `.tex` — alinhar com as decisões

Correções no `Overleaf/textuais/Texto Inicial.tex` (rascunho real do TCC), pendentes desde o
diagnóstico de 2026-06-10:

- [ ] **Remover o Aprendizado Ativo do corpo do texto** (ref. teórico + passo 5 da metodologia)
  e movê-lo para Trabalhos Futuros. Ver `decisoes.md` D8.
- [ ] **Remover a menção a Docker** ("contêineres Docker para isolar os ambientes") — a infra
  Docker foi removida do projeto.
- [ ] **Alinhar nomes ARIA × Hartheus** — trocar "sistema Hartheus" por "ARIA" onde for o
  pipeline; introduzir o Hartheus como a plataforma num parágrafo. Ver `decisoes.md` D1.
- [ ] **Inserir o experimento central 45 × 1** (especialistas vs. generalista) na metodologia —
  hoje ausente. Ver `decisoes.md` D3.
- [ ] **Documentar a rotulagem binária** (`class_id=0`) como decisão deliberada na metodologia.
  Ver `decisoes.md` D2.
- [ ] **Trocar "Label Studio / verificação por amostragem"** por validação qualitativa por
  especialistas. Ver `decisoes.md` D5.

## 📄 Template / LaTeX (`macros.tex`, `main.tex`)

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

## 📚 Bibliografia

- [ ] `bibliografia.bib` está **vazio**; só `bibliografiaTeste.bib` tem entradas (genéricas).
- [ ] Adicionar referências do domínio: **SAM, YOLO, Xception, CLIP, Teacher-Student/Knowledge
  Distillation, Indústria 4.0, TAM, Difusão de Inovações, inspeção visual automatizada (AVI)**.

## 🧩 Código

- [ ] (sem itens soltos no momento — marcos de desenvolvimento estão no `ROADMAP.md`)

## 📁 Docs

- [ ] (manter este arquivo e os `.md` de contexto sem informação duplicada — princípio DRY)
