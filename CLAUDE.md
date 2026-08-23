# CLAUDE.md

Guia de entrada para o Claude Code neste repositório.
**Abrir a sessão lendo este arquivo + [`docs/decisoes.md`](docs/decisoes.md) + [`docs/pendencias.md`](docs/pendencias.md).**

---

**ARIA** (Análise e Reconhecimento Inteligente de Anomalias) — pipeline hierárquico de visão
computacional para marcação automatizada de anomalias superficiais em chapas de rochas
ornamentais. TCC de Henrique (Bacharelado em Sistemas de Informação, IFES Cachoeiro).

**O projeto é isolado** (**D1**): não há vínculo com nenhuma plataforma, produto ou empresa.
Se encontrar menções a "Hartheus" em algum arquivo, é texto desatualizado a corrigir.

Arquitetura: Xception (identifica a litologia) → SAM3 com sondas calibradas por litologia (gera
os polígonos, offline) → YOLO11-seg (inferência rápida em produção).

---

## Mapa da documentação — onde está a verdade

Cada fato mora em **um** lugar só (DRY). Antes de escrever ou codar, consultar a fonte.

| Preciso de... | Fonte única |
|---|---|
| **Decisões fechadas, hipóteses, experimentos, métricas** | [`docs/decisoes.md`](docs/decisoes.md) |
| Como o sistema funciona (técnico) | [`docs/arquitetura.md`](docs/arquitetura.md) |
| Dataset, litologias, faixas de volume, sondas | [`docs/dataset.md`](docs/dataset.md) |
| Estado vivo + ordem de execução | [`docs/roadmap.md`](docs/roadmap.md) |
| Pendências soltas e bloqueadores | [`docs/pendencias.md`](docs/pendencias.md) |
| Como escrever o TCC (cláusulas, estilo, LaTeX) | [`docs/diretrizes-escrita.md`](docs/diretrizes-escrita.md) |

> ⚠️ **`Overleaf/`, `LatinoWare2026/` e `apresentacao/` NÃO são fonte de verdade** (**D13**).
> São saída escrita antes das decisões atuais e ainda não revisada. Nunca copiar um fato de lá —
> nem sobre metodologia, nem sobre números, nem sobre autoria.

---

## Como eu trabalho aqui

1. **Verificar antes de afirmar que funciona.** Rodar e observar a saída real antes de dizer
   "pronto". Evidência antes de afirmação.
2. **Decisão metodológica não se resolve sozinho no código.** Alinhar com `decisoes.md`; se for
   decisão nova, perguntar ao Henrique e registrar lá.
3. **`AI/dataset/` é somente-leitura.** Nunca modificar, mover ou apagar nada de lá.
4. **Commit e push só quando o Henrique pedir.**
5. **Todo edit vem com resumo do que mudou** — nunca edição silenciosa.

---

## Setup

```bash
cd AI/SAM
python -m venv .venv
.venv\Scripts\pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
.venv\Scripts\pip install ultralytics openai-clip opencv-python streamlit
```

## Comandos

Todos rodam a partir de `AI/SAM/`.

```bash
python rock_viewer.py                 # seleção de imagem: próxima litologia pendente
python rock_viewer.py <rock_name>     # litologia específica
python inference.py                   # inferência SAM: lê selectRocks/, grava em results/
.venv\Scripts\python.exe -m streamlit run calibrator.py   # calibrador interativo
```

## Fluxo de dados

```
selectRocks/<rock>.EXT          ← imagem representativa por litologia (seleção MANUAL)
rock_prompts.json               ← { litologia: { sonda: limiar } }
        ↓
inference.py (SAM3SemanticPredictor)
        ↓
results/<rock>/<stem>/<stem>_<sonda>_<conf>.jpg   ← máscara por sonda
results/<rock>/<stem>/<stem>_combined.jpg          ← sobreposição
results/<rock>/<stem>/<stem>.txt                   ← polígonos YOLO
```

> **Isto é o fluxo de calibração, não de produção de dataset.** `inference.py` processa **uma
> imagem por litologia**. O script de lote sobre o dataset (`sam_batch.py`) ainda não existe —
> ver `docs/roadmap.md` → Fase 3.0.

---

## Gotchas críticos

- **Monkey-patch CLIP** (topo de `inference.py` e `calibrator.py`): o Ultralytics SAM3 chama
  `SimpleTokenizer()` como função, mas ele não tem `__call__`. O patch injeta `__call__`
  delegando para `clip.tokenize`. **Não remover** — sem ele o modelo falha **silenciosamente**,
  sem exceção e sem saída.
- **Path do modelo:** hardcoded como `../models/sam3.pt`, relativo a `AI/SAM/`.
- **Seleção de imagem é sempre manual** — usar o próprio SAM para escolher a imagem de
  calibração é raciocínio circular.
- **Casing de path é uma armadilha real.** A pasta é `AI/dataset/` (minúscula), mas o
  `.gitignore`, o `calibrator.py:35` e o `rock_viewer.py:21` dizem `Dataset`. No Windows passa
  por acaso; **no Linux quebra** — e o `.gitignore` deixa de proteger as 34.630 imagens.
- **Versionado:** `rock_prompts.json` e `selectRocks/` **estão no git**. Só `results/` (e o
  `AI/Dataset/` miscased) são ignorados. `samples/` é a demo commitada (só `ice_leke`).
- **Sonda fora do `CLASS_ID_MAP` não vira rótulo.** `inference.py` valida toda a configuração e
  aborta **antes de carregar o modelo**; o `calibrator.py` mostra a máscara mas não grava. Para
  usar uma sonda nova, registre-a no `CLASS_ID_MAP` dos dois arquivos (**D8**).
- **`rock_prompts.json` e `selectRocks/` são PROVISÓRIOS** (**D15**) — não tratar como calibração
  feita. O `rock_viewer.py` ordena as litologias por volume de dados (faixa A primeiro), não em
  ordem alfabética: a ordem **é** a prioridade de trabalho.
