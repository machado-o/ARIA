# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

**ARIA** (Análise e Reconhecimento Inteligente de Anomalias) — pipeline hierárquico de IA para controle de qualidade de chapas de rochas ornamentais. TCC de Henrique (Bacharelado em Sistemas de Informação, IFES Cachoeiro). Esta branch cobre a fase do SAM3 como professor: gerar anotações poligonais de alta qualidade que depois treinam o YOLO.

Arquitetura completa: Xception (classifica tipo litológico) → SAM3 com prompts calibrados por tipo (gera anotações) → YOLO11-seg × 45 modelos especialistas (inferência rápida em produção).

Ver [`PROJETO.md`](PROJETO.md) para o contexto da plataforma Hartheus. Ver [`ROADMAP.md`](ROADMAP.md) para os próximos passos. Ver `TCC/` para o contexto acadêmico.

---

## Setup do ambiente

```bash
cd AI/SAM
python -m venv .venv
.venv\Scripts\pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
.venv\Scripts\pip install ultralytics openai-clip opencv-python streamlit
```

---

## Comandos

Todos os scripts rodam a partir de `AI/SAM/`.

```bash
# Seleção de imagem representativa
python rock_viewer.py                 # próxima rocha pendente em modo loop
python rock_viewer.py <rock_name>     # rocha específica
python rock_viewer.py --cols 6        # grade mais larga (padrão: 8)

# Inferência SAM
python inference.py                   # lê selectRocks/, grava em results/

# Docker — inferência em container com GPU
cd docker
docker compose up --build ai          # build + run
docker compose up ai                  # run sem rebuild
docker compose down
```

---

## Arquitetura

### Fluxo de dados

```
selectRocks/<rock>.EXT          ← imagem representativa por tipo (entrada)
rock_prompts.json               ← { rock_name: { prompt: confidence } }
        ↓
inference.py (SAM3SemanticPredictor)
        ↓
results/<rock>/<stem>/<stem>_<prompt>_<conf>.jpg    ← máscara individual por prompt
results/<rock>/<stem>/<stem>_combined.jpg           ← todas as masks sobrepostas
results/<rock>/<stem>/<stem>.txt                    ← polígonos YOLO (input do treino)
```

### `rock_prompts.json` — schema e lógica de fallback

```json
{
  "default": { "crack": 0.1, "vein": 0.007, "Stain": 0.3 },
  "ice_leke": { "crack": 0.1, "vein": 0.007, "Stain": 0.3, "Dark patches": 0.08 }
}
```

- Chave = nome exato da pasta em `selectRocks/` (sem extensão, case-sensitive)
- Valor = `{ "prompt_label": confidence_threshold }`
- Rochas sem entrada própria caem no `"default"` automaticamente
- Chaves prefixadas com `_` são ignoradas pelo parser (ex.: `"_comment"`)
- O arquivo é **gitignored** — cada dev mantém sua própria cópia local

**Grupos de calibração por cor/textura:**

- Brancas/claras: incluem `"Dark patches"` (conf ~0.08)
- Escuras (nevada_black, sao_gabriel_black): usam `"light spot"` em vez de `"Dark patches"` (conf mais baixo: 0.05–0.01)
- Verdes/quartzitos: sem `"Dark patches"`, crack 0.06–0.08
- Vermelhas (xango_red, tabaco_red): incluem `"light spot"`

**Class IDs no `.txt` de saída:** `vein=0, crack=1, Stain=2, Dark patches=3, light spot=4` — mas todos colapsados para `class_id=0` antes do treinamento YOLO (decisão metodológica do TCC; multi-classe é extensão futura).

### `rock_viewer.py` — modo loop vs. modo direto

- **Modo loop** (sem argumento): itera automaticamente pelas rochas que ainda não têm arquivo em `selectRocks/`. Ao fim de cada rocha pergunta se continua.
- **Modo direto** (`rock_name`): abre uma rocha específica, independente de já ter seleção.
- Arquivo salvo como `selectRocks/<rock_name><.EXT_MAIÚSCULO>` — ex.: `ice_leke.JPG`.
- Roda a partir de `AI/SAM/`; os paths internos assumem `../Dataset` relativo.

### `inference.py` — gotchas obrigatórios

**Monkey-patch CLIP (linhas 4–13):** Ultralytics SAM3 instancia `SimpleTokenizer` e o chama como função (`self.tokenizer(texts)`), mas `SimpleTokenizer` não tem `__call__`. O patch injeta `__call__` delegando para `clip.tokenize`. **Não remover este bloco** — sem ele o modelo falha silenciosamente (sem exceção, sem saída).

**Path do modelo:** hardcoded em `OVERRIDES` como `"../models/sam3.pt"` (relativo a `AI/SAM/`). A env var `MODEL_PATH` do compose existe mas não é lida por ninguém — o path é sempre o hardcoded.

### Docker

O compose monta apenas dois diretórios (não o `AI/` inteiro para evitar `.venv/` no mount):

- `../AI/SAM:/app/SAM` — scripts, selectRocks/, results/, rock_prompts.json
- `../AI/models:/app/models:ro` — pesos do modelo (read-only)

Base image: `python:3.11-slim` + PyTorch cu128 wheel (bundle o CUDA runtime — não precisa de imagem base CUDA). Suporta sm_50 a sm_120 (Maxwell → Blackwell).

---

## Gotchas

- **Typo no rock_prompts.json:** a entrada `"whte_liberdade"` (falta o 'i') não é reconhecida — a rocha `white_liberdade` cai no `default`. Corrigir para `"white_liberdade"` na cópia local.
- **Seleção de imagem é sempre manual** — usar o próprio SAM para escolher a imagem de calibração é raciocínio circular.
- **`rock_prompts.json` não commitado** — ao clonar o repo do zero, o arquivo não existe. `inference.py` avisa e usa o fallback hardcoded (`crack: 0.1, vein: 0.007, Stain: 0.3`).
- **`results/` e `selectRocks/` não commitados** — gitignored. `samples/` é a pasta de demonstração commitada (só ice_leke).
