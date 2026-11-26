# CLAUDE.md

Guia de entrada para o Claude Code neste repositório.
**Abrir a sessão lendo este arquivo + [`docs/decisoes.md`](docs/decisoes.md) (o resumo do topo
basta para começar) + [`docs/pendencias.md`](docs/pendencias.md) (a seção "Por onde retomar").**

---

**ARIA** (Análise e Reconhecimento Inteligente de Anomalias): pipeline de visão computacional para
marcação de anomalias superficiais em chapas de rochas ornamentais. TCC do Henrique (Bacharelado em
Sistemas de Informação, IFES Cachoeiro).

**O projeto é isolado** (**D1**): não há vínculo com nenhuma plataforma, produto ou empresa. Menção
a "Hartheus" em algum arquivo é texto desatualizado a corrigir.

Arquitetura: Xception (identifica a litologia) → SAM3 com sondas calibradas por litologia (gera os
polígonos, fora da linha) → YOLO11-seg (inferência rápida; trabalho futuro nesta versão, **D6**).

O TCC tem **um** experimento e **uma** hipótese (H1): quatro braços do Professor avaliados por
auditoria cega (**D4**, **D5**, **D7**).

---

## Mapa da documentação: onde está a verdade

Cada fato mora em **um** lugar só. Antes de escrever ou codar, consultar a fonte.

| Preciso de... | Fonte única |
|---|---|
| Decisões fechadas, hipótese, experimento, métricas | [`docs/decisoes.md`](docs/decisoes.md) |
| Como o sistema funciona (técnico) | [`docs/arquitetura.md`](docs/arquitetura.md) |
| Dataset, litologias, faixas, sondas, sequência e blocos | [`docs/dataset.md`](docs/dataset.md) |
| Estado de cada parte e ordem de execução | [`docs/roadmap.md`](docs/roadmap.md) |
| O que está em aberto | [`docs/pendencias.md`](docs/pendencias.md) |
| Como escrever o TCC (estilo, LaTeX, compilação) | [`docs/diretrizes-escrita.md`](docs/diretrizes-escrita.md) |
| Ideias, leituras e análises propostas (não é fonte de verdade) | [`docs/reflexao.md`](docs/reflexao.md) |

> ⚠️ **`apresentações/` não é fonte de verdade** (**D13**). A monografia
> (`apresentações/Overleaf/TCC/`) foi realinhada às decisões e é onde se escreve, mas fato se
> confere em `docs/`. O artigo da LatinoWare2026, o artigo e a apresentação de PD1 são saída
> antiga: nunca copiar um fato de lá.

---

## Como eu trabalho aqui

1. **Verificar antes de afirmar que funciona.** Rodar e observar a saída real antes de dizer
   "pronto".
2. **Decisão metodológica não se resolve sozinho no código.** Alinhar com `decisoes.md`; se for
   decisão nova, perguntar ao Henrique (com alternativas prontas) e registrar lá, com data.
3. **`AI/dataset/` é somente-leitura.** Nunca modificar, mover ou apagar nada de lá (a única
   exceção registrada é o rename da **D9**).
4. **Commit e push só quando o Henrique pedir.**
5. **Todo edit vem com resumo do que mudou.** Nunca edição silenciosa.
6. **Explicar em linguagem simples**, com exemplos e analogias. Texto denso e abstrato não ajuda.

---

## Setup

```bash
cd AI
python -m venv .venv
.venv\Scripts\pip install torch torchvision --index-url https://download.pytorch.org/whl/cuXXX
.venv\Scripts\pip install ultralytics openai-clip opencv-python-headless streamlit timm
```

- `cuXXX` depende do driver da máquina: ver em <https://pytorch.org/get-started/locally/> qual
  índice serve para o driver que o `nvidia-smi` reportar.
- `opencv-python-headless` porque nenhum script abre janela do OpenCV. `altair` e `pandas` vêm com
  o streamlit.
- O `.venv` vive em **`AI/.venv`**. A partir de `AI/SAM/`, o interpretador é
  `..\.venv\Scripts\python.exe`. Na outra máquina, se o venv ainda estiver em `AI/SAM/.venv`,
  recriar do zero: mover quebra os `.exe` de `Scripts/`.
- **Nenhum documento compartilhado guarda número de máquina** (GPU, driver, versões). O Henrique
  alterna entre dois PCs com hardware diferente de propósito, e esses números já foram escritos
  errados antes. Para saber onde você está:

```bash
cd AI
.venv\Scripts\python.exe ambiente.py   # máquina, GPU, driver, versões, pesos presentes, estado da D18
```

---

## Comandos

Os de `AI/SAM/` rodam com `..\.venv\Scripts\python.exe`:

```bash
rock_viewer.py                 # seleção de imagem: próxima litologia pendente
rock_viewer.py <rock_name>     # litologia específica (se já 4/4, abre em revisão)
-m streamlit run calibrator.py # calibrador (sondas + limiar)
inference.py                   # Professor: lê selectRocks/, grava em results/
verificar_d18.py               # prova que a varredura offline é exata (D18)
figuras_regra_autor.py         # regra × autor na mesma chapa, do cache, sem GPU
auditoria_analisar.py          # precisão e recall relativo por braço, IC 95%, kappa
auditoria_preparar.py --atualizar-app   # só troca o aplicativo do pacote e refaz o .zip
```

- `figuras_regra_autor.py` grava em `apresentações/jacitec/` (figuras + `regra_x_autor.csv`) e
  precisa do `_cache/`. Na máquina sem cache, capturar cada litologia no calibrador antes.
- Auditoria: o avaliador recebe o `auditoria/pacote_*.zip`, abre o `index.html` e devolve o `.json`
  exportado, que vai para `auditoria/respostas/`. O pacote não leva braço, sonda, litologia nem
  score. **Não rodar o `auditoria_preparar.py` sem `--atualizar-app`** (ver *Auditoria*, abaixo).

Classificador (**D19**), a partir de `AI/Xception/`:

```bash
..\.venv\Scripts\python.exe train.py                  # treino → ../models/xception_480.pt + runs/
..\.venv\Scripts\python.exe evaluate.py --split val   # à vontade
..\.venv\Scripts\python.exe evaluate.py               # test/, UMA vez — o script recusa repetir
..\.venv\Scripts\python.exe roteador.py chapa.jpg     # litologia + confiança + top-3
```

`runs/` (config, histórico, métricas em JSON) vai para o git; o `.pt` não. Para teste de fumaça,
`--limite N` e `--dir-runs/--dir-modelos` apontando para fora do repositório.

---

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
rock_prompts.json                      ← { litologia: { sonda: limiar } }  — resumo; só calibradas
selectRocks/<rock>/calibracao.json     ← limiar + contagem por vaga + CRITÉRIO escrito
        ↓  o limiar do inference.py sai do calibracao.json, não do rock_prompts.json
inference.py (SAM3SemanticPredictor)
        ↓
results/<rock>/procedencia.json                    ← de onde veio cada limiar desta rodada
results/<rock>/<stem>/<stem>_<sonda>_<conf>.jpg   ← máscara por sonda
results/<rock>/<stem>/<stem>_combined.jpg          ← sobreposição
results/<rock>/<stem>/<stem>.txt                   ← polígonos YOLO
```

Isto é o fluxo de **calibração**, não de produção de dataset: o `inference.py` processa as imagens
de `selectRocks/`. O script de lote (`sam_batch.py`) não existe e é trabalho futuro (**D6**).

Estado da seleção e da calibração: `docs/roadmap.md` (hoje, a faixa A inteira: 11 de 45).

---

## Gotchas críticos

### Bibliotecas e ambiente

- **Monkey-patch do CLIP** (topo de `inference.py` e `calibrator.py`): o SAM3 do Ultralytics chama
  `SimpleTokenizer()` como função, mas ele não tem `__call__`. O patch injeta `__call__` delegando
  para `clip.tokenize`. **Não remover**: sem ele o modelo falha em silêncio, sem exceção e sem
  saída.
- **`cv2.imread` não abre caminho com acento no Windows**, e o caminho deste projeto tem acento.
  Importar o ultralytics troca o `cv2.imread` por uma versão que aceita Unicode: quem importa
  ultralytics antes nunca vê o bug; quem não importa recebe `None` em silêncio. Em código sem
  ultralytics, usar `np.fromfile` + `cv2.imdecode` (ver `calibrator.abrir_imagem`).
- **Não usar `masks.xyn`; usar `sam_cache.pecas_por_deteccao`** (**D21**). O `masks.xyn` funde os
  contornos soltos de uma detecção numa poligonal só, ligada por pontes que viravam retas na
  preview e no `.txt`. Hoje uma detecção é uma **lista de peças** (no cache, `polys[i]`; no `.txt`,
  uma linha por peça). "Marcação", na regra e no `calibracao.json`, continua sendo **detecção**.
  Cache `.npz` de antes da mudança é tratado como ausente (`sam_cache.cache_atual`) e recapturado.
- **A D18 vale por versão do ultralytics, não por máquina.** O `verificar_d18.py`, ao passar, anota
  a versão em `AI/SAM/d18_verificado.json` (no git). Verificar numa máquina vale para a outra na
  mesma versão. Quem responde "a versão daqui está coberta?" é o `ambiente.py`. Cada
  `calibracao.json` grava a versão usada.
- **No Bash, não chamar `python` puro**: no Windows ele pode abrir o atalho da Microsoft Store e
  travar. Usar sempre o caminho do venv.

### Caminhos

- **Caminhos são ancorados no arquivo, não no CWD.** Os scripts de `AI/SAM/` montam `selectRocks/`,
  `../dataset/` e `../models/sam3.pt` a partir de `Path(__file__).parent` e rodam de qualquer pasta.
- **Casing:** a pasta é `AI/dataset/` (minúscula). No Windows o erro passa por acaso; no Linux
  quebra, e aí o `.gitignore` deixa de proteger as 34.630 imagens. Ele lista as **duas** grafias
  de propósito. Caminho novo, sempre em minúscula.

### Seleção e calibração

- **Seleção de imagem é sempre manual.** Usar o próprio SAM para escolher a imagem de calibração
  é raciocínio circular. Só do `train/` (**D17**).
- **`rock_viewer.py` é interativo e só funciona no terminal do Henrique.** A guia do navegador abre
  antes do `input()`; rodado pelo Claude (sem stdin), abre a guia e morre com `EOFError`. Não
  tentar de novo (cada tentativa abre outra guia). Pedir para ele rodar com
  `! ..\.venv\Scripts\python.exe rock_viewer.py`.
- **`rock_viewer.py` ordena por volume de dados** (faixa A primeiro): a ordem é a prioridade.
- **Litologia 4/4 abre em modo revisão.** Mostra as 4 escolhas no topo (Enter sai sem mudar nada) e
  oferece substituir uma vaga. Com `calibracao.json`, a troca exige digitar `SUBSTITUIR` e fica
  registrada em `substituicoes` do `meta.json`. Imagem nova na vaga **apaga o
  `_cache/<vaga>__*.npz`** dela, porque o cache é indexado pela vaga, não pela imagem (reescolher
  a mesma imagem não apaga nada). Vaga trocada depois do `calibrado_em` faz a litologia aparecer
  no calibrador como **⊘ desatualizada**.
- **A captura não mexe em limiar salvo.** Só a sonda sem limiar no `calibracao.json` parte da regra
  (`semear_da_regra`). Até 10/10/2026, capturar uma sonda nova trocava todos os limiares salvos
  pelos da regra; na outra máquina, sem cache, a primeira captura teria apagado todos.
- **O calibrador abre o slider no limiar da regra.** O autor parte sempre dali (ancoragem; ver
  `reflexao.md`, seção 3).
- **Sonda fora do cadastro não vira rótulo.** O cadastro (id e cor) mora só em `AI/SAM/sondas.py`
  (**D8**). O id é posicional e vai para o `.txt`: sonda nova entra no fim, nunca renumerar. O
  `inference.py` valida a configuração e aborta antes de carregar o modelo; o calibrador deixa
  explorar a sonda, mas não a salva.
- **`rock_prompts.json` só tem litologia calibrada: quem não está nele não foi calibrado.** Quem
  escreve nele é o calibrador. Os valores provisórios antigos (e a entrada `"default"`) foram
  apagados em 09/10/2026 e estão no histórico do git.
- **O `inference.py` só roda sobre litologia calibrada.** O limiar sai do `calibracao.json`; rocha
  sem calibração, ou desatualizada, é recusada e listada antes de o modelo carregar. Para explorar
  com o `rock_prompts.json` existe `--provisorio`, e o `results/<rock>/procedencia.json` grava isso.
  Até 09/10/2026 o script nunca se recusava a rodar e gerava `.txt` com limiares inventados.
- **O calibrador é dono do limiar; o `inference.py` é dono das máscaras finais.** O calibrador não
  escreve em `results/` nem gera `.txt`.
- **Versionado:** `rock_prompts.json` e `selectRocks/` estão no git. `results/`, `_cache/` e o
  `AI/Dataset/` com maiúscula são ignorados. `samples/` é a demo antiga (só `ice_leke`).

### Auditoria

- **O pacote foi sorteado uma vez só (19/11/2026) e não se refaz.** Os ids das marcações (`m001`…)
  valem para aquele sorteio, cuja ligação com os braços está em `auditoria/itens.json`. Rodar o
  `auditoria_preparar.py` de novo, principalmente na outra máquina (onde o SAM dá scores um pouco
  diferentes), sortearia outros itens. Por isso o script para antes de capturar qualquer coisa se o
  `itens.json` existe (`--refazer-itens` só antes de qualquer resposta). Para reenviar, usar o
  `.zip` já gerado. Se só o `auditoria_app.html` mudou, `--atualizar-app` recopia o aplicativo e
  refaz o `.zip` sem tocar no sorteio.
- **O Henrique também é avaliador:** ele não abre `itens.json` nem `limiares.json` antes de julgar,
  e nenhuma figura com chapa do `test/` é mostrada a ele antes disso. O Claude também não expõe o
  conteúdo desses arquivos.
- **De onde vieram os arquivos neste PC (desde 22/11/2026):** o `.zip` e as capturas das 33 chapas
  (`auditoria/<rocha>/_cache/`) vieram da outra máquina (ultralytics 8.4.52), e o cache das vagas de
  lá, de onde saiu o `limiares.json`, está em `auditoria/_vagas_maquina2/`, **não** em
  `selectRocks/*/_cache/` (que aqui é a versão das calibrações). Para analisar, só o
  `auditoria_analisar.py`, que não lê cache.

### Mais de uma máquina

O Henrique alterna entre dois PCs. O que precisa existir nos dois vai para o **git**; `_cache/`,
`results/`, o `.venv`, o `sam3.pt`, o `xception_480.pt` e o pacote da auditoria não vão, e cada
máquina tem os seus. Dar commit e push antes de trocar de PC ou de editar no Overleaf: em 06/11 isso
não foi feito e o texto do TCC divergiu entre as máquinas.
