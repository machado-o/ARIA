# CLAUDE.md

Guia de entrada para o Claude Code neste repositório. **Leia este arquivo + [`PENDENCIAS.md`](PENDENCIAS.md) ao iniciar a sessão.**

---

**ARIA** (Análise e Reconhecimento Inteligente de Anomalias) — pipeline hierárquico de IA para controle de qualidade de chapas de rochas ornamentais. TCC de Henrique (Bacharelado em Sistemas de Informação, IFES Cachoeiro). **ARIA é o método/pipeline; Hartheus é a plataforma web** onde ARIA se destina a ser o núcleo de IA (ver `decisoes.md` D1 e `PROJETO.md`).

Arquitetura: Xception (classifica tipo litológico) → SAM3 com prompts calibrados por tipo (gera anotações) → YOLO11-seg × 45 modelos especialistas (inferência rápida em produção). Esta branch cobre a fase do **SAM3 como professor**: gerar anotações poligonais que depois treinam o YOLO.

A escrita do TCC acontece **direto aqui** (LaTeX em `Overleaf/`, sincronizado com o Overleaf via Git) — não mais via Claude App.

---

## Mapa da documentação — onde está a verdade

Cada fato mora em **um** lugar só (princípio DRY). Antes de escrever/codar, consultar a fonte:

| Preciso de... | Fonte única |
|---|---|
| Decisões metodológicas fechadas (rotulagem, baseline, AL, identidade...) | [`TCC/decisoes.md`](TCC/decisoes.md) |
| Como o sistema funciona (técnico) | [`TCC/arquitetura.md`](TCC/arquitetura.md) |
| Dataset, 45 classes, anomalias, calibração | [`TCC/dataset.md`](TCC/dataset.md) |
| Argumento acadêmico, hipótese, métricas, capítulos | [`TCC/pontos_tcc.md`](TCC/pontos_tcc.md) |
| **Como escrever o TCC** (cláusulas, estilo, fluxo) | [`TCC/diretrizes-escrita.md`](TCC/diretrizes-escrita.md) |
| **Como mexer no código** (cláusulas, gotchas, disciplina) | [`TCC/diretrizes-implementacao.md`](TCC/diretrizes-implementacao.md) |
| Estado vivo + próximos passos | [`ROADMAP.md`](ROADMAP.md) |
| Pendências soltas (corrigir/escrever) | [`PENDENCIAS.md`](PENDENCIAS.md) |
| Contexto da plataforma Hartheus e branches | [`PROJETO.md`](PROJETO.md) |

---

## Setup do ambiente

```bash
cd AI/SAM
python -m venv .venv
.venv\Scripts\pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
.venv\Scripts\pip install ultralytics openai-clip opencv-python streamlit
```

## Comandos

Todos os scripts rodam a partir de `AI/SAM/`.

```bash
python rock_viewer.py                 # seleção de imagem: próxima rocha pendente (modo loop)
python rock_viewer.py <rock_name>     # rocha específica
python inference.py                   # inferência SAM: lê selectRocks/, grava em results/
.venv\Scripts\python.exe -m streamlit run calibrator.py   # calibrador interativo
```

## Fluxo de dados

```
selectRocks/<rock>.EXT          ← imagem representativa por tipo (entrada, manual)
rock_prompts.json               ← { rock_name: { prompt: confidence } }  (gitignored)
        ↓
inference.py (SAM3SemanticPredictor)
        ↓
results/<rock>/<stem>/<stem>_<prompt>_<conf>.jpg    ← máscara individual por prompt
results/<rock>/<stem>/<stem>_combined.jpg           ← masks sobrepostas
results/<rock>/<stem>/<stem>.txt                    ← polígonos YOLO (input do treino)
```

Detalhe do schema de `rock_prompts.json`, grupos de calibração por cor e estratégia de prompts → `TCC/arquitetura.md`. Class IDs colapsam para `class_id=0` antes do treino → `TCC/decisoes.md` D2.

---

## Gotchas críticos (não esquecer)

- **Monkey-patch CLIP (`inference.py` linhas 4–13):** Ultralytics SAM3 chama `SimpleTokenizer()` como função, mas ele não tem `__call__`. O patch injeta `__call__` delegando para `clip.tokenize`. **Não remover** — sem ele o modelo falha **silenciosamente** (sem exceção, sem saída).
- **Path do modelo:** hardcoded em `OVERRIDES` como `../models/sam3.pt` (relativo a `AI/SAM/`).
- **Seleção de imagem é sempre manual** — usar o próprio SAM para escolher a imagem de calibração é raciocínio circular.
- **Gitignored:** `rock_prompts.json`, `results/`, `selectRocks/`. `samples/` é a demo commitada (só `ice_leke`). Sem `rock_prompts.json`, `inference.py` usa fallback hardcoded (`crack: 0.1, vein: 0.007, Stain: 0.3`).
- **Typo conhecido no `rock_prompts.json`:** `"whte_liberdade"` (falta o 'i') → `white_liberdade` cai no `default`. Corrigir na cópia local.
- **Não misturar código entre branches** `ARIA` (`AI/`, batch) e `feat/matheus` (`ai/`, FastAPI) — ver `PROJETO.md`.
