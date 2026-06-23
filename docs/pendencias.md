# Pendências — ARIA

> Caixa de entrada de coisas a fazer/corrigir que **não** são marcos grandes do
> desenvolvimento (esses ficam no `roadmap.md`). Itens soltos de escrita, template, docs e
> código. Marcar `[x]` ao concluir; remover quando virar irrelevante.
>
> Abra a sessão lendo `CLAUDE.md` + este arquivo.
>
> Última atualização: 2026-06-23

---

## 📰 Artigo SBC (entrega PD1) — `Overleaf/artigo/`

Entrega do Projeto de Diplomação I: artigo científico completo no template SBC (10–12
páginas). Estrutura criada portando o conteúdo de `Overleaf/TCC/textuais/Texto Inicial.tex`.
O `Overleaf/` agora tem duas pastas: **`TCC/`** (monografia) e **`artigo/`** (SBC).

- [ ] **Re-apontar o "main document" no Overleaf** para `artigo/main.tex` após dar `pull`
  (a reestruturação de pastas foi feita no Git local).
- [ ] **Compilar no Overleaf** — não há LaTeX local; validar que `subfig`, `sbc-template` e a
  bibliografia fecham sem erro.
- [ ] **Nome completo do autor** — `main.tex` tem `Henrique \textsc{[Sobrenome --- TODO]}`.
- [ ] **E-mail institucional** (hoje o pessoal como placeholder).
- [X] **Diagrama da arquitetura** — feito em TikZ (vetorial) em `\label{fig:arquitetura}`.
- [X] **Bibliografia:** `referencias.bib` consolidada com as refs reais dos `.bib` anteriores do
  grupo (`Bibliografia.bib`, `ifacconf.bib`) + canônicas (SAM, CLIP, KD, pseudo-label). Todas as
  chaves citadas batem com o `.bib`; placeholders TODO eliminados.
- [ ] **Apagar os `.bib` temporários da raiz** (`Bibliografia.bib`, `ifacconf.bib`) após confirmar
  que tudo necessário foi migrado para `Overleaf/artigo/referencias.bib`.

## ✍️ Escrita / `.tex` — alinhar com as decisões

Correções no `Overleaf/textuais/Texto Inicial.tex` (rascunho real do TCC), pendentes desde o
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

- [ ] (sem itens soltos no momento — marcos de desenvolvimento estão no `roadmap.md`)

## 📁 Docs

- [ ] 🔔 **Atualizar o `Hartheus.md`** (ex-`PROJETO.md`) com os arquivos do Hartheus que o Henrique
  vai passar. O contexto mudou: a branch **`feat/matheus` não existe mais**. Ao atualizar, purgar as
  referências restantes a `feat/matheus` no `Hartheus.md` (seções de branches/comparação).
  → **Claude: lembrar o Henrique de te passar os arquivos ao retomar a sessão.**
- [ ] (manter este arquivo e os `.md` de contexto sem informação duplicada — princípio DRY)
