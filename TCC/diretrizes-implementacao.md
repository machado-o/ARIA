# Diretrizes de Implementação — ARIA

> Contrato de comportamento para mexer no **código** do pipeline (SAM/YOLO/Python).
> Complementa o `CLAUDE.md` (que tem os fatos do codebase); aqui ficam as **cláusulas de como
> trabalhar**. Em conflito, o que o Henrique disser na conversa vence.
>
> Última atualização: 2026-06-10

---

## 1. Ambiente

1.1. Todos os scripts rodam a partir de `AI/SAM/`. Os paths internos assumem isso
(ex.: `../models/sam3.pt`, `../Dataset`).

1.2. Usar o venv do projeto (`AI/SAM/.venv`). Não instalar global.

---

## 2. Gotchas invioláveis

2.1. **Não remover** o monkey-patch do CLIP no topo do `inference.py` (linhas 4–13). Sem ele o
SAM3 falha **silenciosamente** (sem exceção, sem saída).

2.2. Path do modelo SAM hardcoded em `OVERRIDES` como `../models/sam3.pt` (relativo a
`AI/SAM/`). Não mexer sem motivo.

---

## 3. O que NÃO commitar (gitignored)

3.1. `rock_prompts.json` — cada dev mantém a própria cópia local.

3.2. `results/` e `selectRocks/` — saídas/seleções locais. `samples/` é a pasta de demonstração
commitada (só `ice_leke`).

---

## 4. Branches (não misturar código)

4.1. Esta é a branch **`ARIA`**: diretório `AI/`, entry point `inference.py` (script batch),
sem API HTTP.

4.2. A `feat/matheus` é uma abordagem **diferente** (diretório `ai/`, `api.py` FastAPI,
active-learning loop). Os fluxos de inferência são fundamentalmente distintos — **não importar
código entre branches.** Ver `PROJETO.md`.

---

## 5. Disciplina de trabalho

5.1. **Verificar antes de afirmar que funciona** — rodar o script/teste e observar a saída real
antes de dizer "pronto"/"corrigido". Evidência antes de afirmação.

5.2. **Seleção de imagem representativa é sempre manual** (`rock_viewer.py`). Usar o próprio SAM
para escolher a imagem de calibração é raciocínio circular.

5.3. Mudanças de arquitetura ou de decisão metodológica não se resolvem no código sozinho —
alinhar com `decisoes.md` e, se for nova decisão, perguntar ao Henrique.

---

## 6. Onde está a verdade (técnica)

| Preciso de... | Olhar em |
|---|---|
| Fatos rápidos do codebase, comandos, gotchas | `../CLAUDE.md` |
| Arquitetura detalhada do pipeline | `arquitetura.md` |
| Dataset, classes, formato de anotação | `dataset.md` |
| Decisões fechadas (rotulagem, baseline...) | `decisoes.md` |
| Próximos passos do desenvolvimento | `../ROADMAP.md` |
