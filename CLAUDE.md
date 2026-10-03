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

> ⚠️ **`apresentações/` (Overleaf do TCC, artigo LatinoWare2026, apresentação de PD1) NÃO é
> fonte de verdade** (**D13**). É saída escrita antes das decisões atuais e ainda não revisada.
> Nunca copiar um fato de lá — nem sobre metodologia, nem sobre números, nem sobre autoria.

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
cd AI
python -m venv .venv
.venv\Scripts\pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
.venv\Scripts\pip install ultralytics openai-clip opencv-python streamlit altair pandas timm
```

> O `.venv` vive em **`AI/.venv`**, um nível acima de `AI/SAM/`. Rodando os scripts a partir de
> `AI/SAM/`, o interpretador é `..\.venv\Scripts\python.exe`. O índice CUDA (`cuXXX`) depende do
> driver — a instalação de hoje é `torch 2.11.0+cu128` num driver 596.49 (RTX 5060 Ti); confira
> com `nvidia-smi` se mudar de máquina. Versão do ultralytics em uso: **8.4.61**.
>
> ⚠️ **Neste PC o venv ainda está no lugar antigo, `AI/SAM/.venv`** (de lá, `.venv\Scripts\`).
> Decidido em 02/10/2026 recriá-lo do zero em `AI/.venv` — mover quebra os `.exe` de `Scripts/`.

## Comandos

Todos rodam a partir de `AI/SAM/`, com o Python do venv em `AI/.venv` (`..\.venv\Scripts\`).

```bash
..\.venv\Scripts\python.exe rock_viewer.py                 # seleção de imagem: próxima litologia pendente
..\.venv\Scripts\python.exe rock_viewer.py <rock_name>     # litologia específica
..\.venv\Scripts\python.exe -m streamlit run calibrator.py # calibrador (sondas + limiar)
..\.venv\Scripts\python.exe inference.py                   # inferência SAM: lê selectRocks/, grava em results/
..\.venv\Scripts\python.exe verificar_d18.py                # prova que a varredura offline é exata (D18)
```

Classificador de litologia (**D19**), a partir de `AI/Xception/`:

```bash
..\.venv\Scripts\python.exe train.py                  # treino → ../models/xception_480.pt + runs/xception_480/
..\.venv\Scripts\python.exe evaluate.py --split val   # à vontade
..\.venv\Scripts\python.exe evaluate.py               # test/, UMA vez — o script recusa repetir
..\.venv\Scripts\python.exe roteador.py chapa.jpg     # litologia + confiança + top-3
```

> `runs/` (config, histórico, métricas em JSON) vai para o git; o `.pt` não. Para teste de
> fumaça, `--limite N` e `--dir-runs/--dir-modelos` apontando para fora do repo.

## Fluxo de dados

```
selectRocks/<rock>/descoberta.EXT      ← define QUAIS sondas entram   \
selectRocks/<rock>/limiar_sutil.EXT    ←                               } seleção MANUAL (D17)
selectRocks/<rock>/limiar_tipica.EXT   ←  definem o LIMIAR             /
selectRocks/<rock>/limiar_forte.EXT    ←                              /
selectRocks/<rock>/meta.json           ← de onde veio cada uma (reprodutibilidade)
        ↓
calibrator.py  →  SAM uma vez por (imagem, sonda) no piso de conf  (D18)
selectRocks/<rock>/_cache/<vaga>__<sonda>.npz   ← scores + polígonos (gitignored)
        ↓  varredura de limiar offline, sem GPU
rock_prompts.json                      ← { litologia: { sonda: limiar } }
selectRocks/<rock>/calibracao.json     ← limiar + contagem por vaga + CRITÉRIO escrito
        ↓
inference.py (SAM3SemanticPredictor)
        ↓
results/<rock>/<stem>/<stem>_<sonda>_<conf>.jpg   ← máscara por sonda
results/<rock>/<stem>/<stem>_combined.jpg          ← sobreposição
results/<rock>/<stem>/<stem>.txt                   ← polígonos YOLO
```

> **Isto é o fluxo de calibração, não de produção de dataset.** `inference.py` processa as
> imagens de `selectRocks/`, não o dataset. O script de lote (`sam_batch.py`) ainda não existe —
> ver `docs/roadmap.md` → Fase 3.0.
>
> `inference.py` já aceita o layout em pasta sem alteração: `get_rock_name()` devolve o nome da
> pasta quando a imagem está aninhada (verificado).

---

## Gotchas críticos

- **Monkey-patch CLIP** (topo de `inference.py` e `calibrator.py`): o Ultralytics SAM3 chama
  `SimpleTokenizer()` como função, mas ele não tem `__call__`. O patch injeta `__call__`
  delegando para `clip.tokenize`. **Não remover** — sem ele o modelo falha **silenciosamente**,
  sem exceção e sem saída.
- **Path do modelo:** hardcoded como `../models/sam3.pt`, relativo a `AI/SAM/`.
- **Seleção de imagem é sempre manual** — usar o próprio SAM para escolher a imagem de
  calibração é raciocínio circular.
- **Casing de path é uma armadilha real.** A pasta é `AI/dataset/` (minúscula). Os scripts e o
  `.gitignore` já foram corrigidos (Fase 0), e o `.gitignore` lista as **duas** grafias de
  propósito. No Windows o erro passa por acaso; **no Linux quebra** — e aí o `.gitignore` deixa
  de proteger as 34.630 imagens. Ao escrever caminho novo, sempre minúscula.
- **Versionado:** `rock_prompts.json` e `selectRocks/` **estão no git**. Só `results/` (e o
  `AI/Dataset/` miscased) são ignorados. `samples/` é a demo commitada (só `ice_leke`).
- **Sonda fora do `CLASS_ID_MAP` não vira rótulo.** `inference.py` valida toda a configuração e
  aborta **antes de carregar o modelo**; o `calibrator.py` deixa explorar a sonda mas não a salva
  em `rock_prompts.json`. Para usar uma sonda nova, registre-a no `CLASS_ID_MAP` dos dois
  arquivos (**D8**).
- **`rock_prompts.json` é PROVISÓRIO** (**D15**) — não tratar como calibração feita. Calibração
  feita é a que tem **`calibracao.json`** ao lado das vagas (limiar + critério escrito); é isso
  que o calibrador usa para dizer "calibrada". Estado: **16 de 180 vagas** — `siena_white` 4/4
  (08/09/2026), `nevada_black` 4/4 (02/10/2026), `ubatuba_green` e `ipanema_beige` 4/4
  (03/10/2026), restam 28 vagas na faixa A (`shadow_white` pulada por ora). **1 de 45 litologias calibrada** — `siena_white`
  (01/10/2026).
- **Mais de uma máquina.** O Henrique alterna entre este PC e outro. O que precisa existir nos
  dois vai para o **git**; `_cache/`, `results/`, o `.venv` e o `sam3.pt` não vão, e cada máquina
  tem os seus. **A versão do ultralytics pode diferir entre elas** — cada `calibracao.json` grava
  a versão usada (a `siena_white` foi calibrada na **8.4.52**; este PC tem a 8.4.61). A
  equivalência da **D18** é verificada por versão: ao calibrar numa versão nova, rodar
  `verificar_d18.py` nela antes.
- **`cv2.imread` não abre caminho com acento no Windows** — e o caminho deste projeto tem cedilha
  (`…Software de Segmentação de Rochas…`). A armadilha é que **importar o ultralytics
  monkey-patcha `cv2.imread`** por uma versão que aceita Unicode: quem importa ultralytics antes
  nunca vê o bug, quem não importa recebe `None` silencioso. Em código que não depende do
  ultralytics, use `np.fromfile` + `cv2.imdecode` (ver `calibrator.abrir_imagem`).
- **`masks.xyn` funde contornos disjuntos numa só poligonal** (`masks2segments(strategy="all")`),
  ligando-os por pontes de ida e volta. É o que vai para o `.txt` de treino. Medido em
  `siena_white/descoberta` (crack @0,08): 45 das 76 detecções têm mais de um contorno; a área
  agregada infla só 2,4% (IoU 0,93 contra a máscara), mas uma detecção com 18 contornos chegou a
  **2,5×**. Tratar no pós-processamento do Professor — `docs/roadmap.md` → Fase 3.0.
- **`rock_viewer.py` ordena por volume de dados** (faixa A primeiro), não em ordem alfabética: a
  ordem **é** a prioridade de trabalho. Cada litologia tem 4 vagas nomeadas pelo papel.
- **`sam_cache.py`** implementa a varredura offline de limiar (**D18**): roda o SAM uma vez com
  `conf` no piso, guarda scores + polígonos, e filtra sem GPU. Equivalência provada no fonte do
  ultralytics **e verificada empiricamente** — `python verificar_d18.py` compara a filtragem do
  cache com o SAM rodando de novo em cada limiar.
- **O calibrador é o dono do limiar; o `inference.py` é o dono das máscaras finais.** O
  `calibrator.py` não escreve em `results/` nem gera `.txt` — ele decide sondas e limiar e grava
  `rock_prompts.json` + `calibracao.json`.
