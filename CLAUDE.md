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
.venv\Scripts\pip install torch torchvision --index-url https://download.pytorch.org/whl/cuXXX
.venv\Scripts\pip install ultralytics openai-clip opencv-python-headless streamlit timm
```

> `cuXXX` **depende do driver desta máquina** — veja em <https://pytorch.org/get-started/locally/>
> qual índice serve para o driver que o `nvidia-smi` reportar. `opencv-python-headless` em vez de
> `opencv-python` porque nenhum script abre janela do OpenCV. `altair` e `pandas` não precisam ser
> pedidos: vêm com o streamlit.

> O `.venv` vive em **`AI/.venv`**, um nível acima de `AI/SAM/`. Rodando os scripts a partir de
> `AI/SAM/`, o interpretador é `..\.venv\Scripts\python.exe`. O índice CUDA (`cuXXX`) depende do
> driver, e o Henrique alterna entre **dois PCs com hardware diferente** — então GPU, driver,
> torch, Python e ultralytics **são diferentes de propósito**, e não há nada a "acertar".
>
> **Regra: nenhum documento compartilhado guarda número de máquina.** Até 09/10/2026 este
> parágrafo dizia RTX 5060 Ti / driver 596.49 / torch 2.11.0+cu128 / ultralytics 8.4.61 /
> Python 3.14.2 — números da **outra** máquina, escritos como se fossem deste PC. Para saber onde
> você está:
>
> ```bash
> cd AI
> .venv\Scripts\python.exe ambiente.py
> ```
>
> Ele mostra máquina, GPU, driver, versões, quais pesos existem **nesta** máquina (`sam3.pt`,
> `xception_480.pt` — nenhum vai para o git) e se a **D18** já foi verificada na versão do
> ultralytics daqui.
>
> Neste PC o venv foi recriado em `AI/.venv` em 03/10/2026, com o mesmo `pip freeze` do antigo
> `AI/SAM/.venv` (apagado). Na outra máquina, se o venv ainda estiver em `AI/SAM/.venv`, recriar
> do zero — mover quebra os `.exe` de `Scripts/`.

## Comandos

Onde estou e o que esta máquina pode rodar, a partir de `AI/`:

```bash
.venv\Scripts\python.exe ambiente.py        # máquina, GPU, versões, pesos, estado da D18
```

Os demais rodam a partir de `AI/SAM/`, com o Python do venv em `AI/.venv` (`..\.venv\Scripts\`).

```bash
..\.venv\Scripts\python.exe rock_viewer.py                 # seleção de imagem: próxima litologia pendente
..\.venv\Scripts\python.exe rock_viewer.py <rock_name>     # litologia específica (se já 4/4, abre em REVISÃO)
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
rock_prompts.json                      ← { litologia: { sonda: limiar } }  — PROVISÓRIO (D15)
selectRocks/<rock>/calibracao.json     ← limiar + contagem por vaga + CRITÉRIO escrito
        ↓  o limiar do inference.py sai do calibracao.json, não do rock_prompts.json
inference.py (SAM3SemanticPredictor)
        ↓
results/<rock>/procedencia.json                    ← de onde veio cada limiar desta rodada
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
- **Caminhos são ancorados no arquivo, não no CWD.** Os scripts de `AI/SAM/` montam
  `selectRocks/`, `../dataset/` e `../models/sam3.pt` a partir de `Path(__file__).parent` —
  rodam de qualquer pasta. Até 10/10/2026 o `rock_viewer.py` e o `verificar_d18.py` usavam
  caminho relativo ao CWD e morriam com "Dataset não encontrado" fora de `AI/SAM/`.
- **`rock_viewer.py` é interativo: só funciona no terminal do Henrique.** A guia do navegador
  abre **antes** do `input()`; rodado pelo Claude (sem stdin), ele abre a guia e morre com
  `EOFError`. Não tentar de novo — cada tentativa abre outra guia. Pedir para ele rodar com
  `! ..\.venv\Scripts\python.exe rock_viewer.py`.
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
  em `rock_prompts.json`. O cadastro (id **e** cor) mora num lugar só, `AI/SAM/sondas.py`:
  registre a sonda nova lá e só lá (**D8**). O id é posicional e vai para o `.txt` — sonda nova
  entra no fim, nunca renumere uma já usada.
- **O `inference.py` só roda sobre litologia calibrada.** O limiar sai do `calibracao.json`;
  litologia sem calibração (ou com calibração desatualizada) é **recusada e listada**, antes de o
  modelo carregar. Até 09/10/2026 ele tinha três redes de segurança encadeadas — arquivo ausente
  virava config vazia, rocha sem config caía na entrada `"default"` do `rock_prompts.json`, e a
  ausência dela caía em três limiares chumbados no código — então **nunca se recusava a rodar**:
  gerava `.txt` com números inventados, idênticos por fora aos de uma rocha calibrada. Para
  explorar com os limiares provisórios existe `--provisorio`, e aí o
  `results/<rock>/procedencia.json` grava que foi provisório. Esse arquivo é a resposta para "de
  onde veio este limiar?" — ele sai em toda rodada, junto das máscaras.
- **`rock_prompts.json` agora só tem litologia calibrada.** Em 09/10/2026 os 45 valores
  provisórios (e a entrada `"default"`) foram **apagados** — eram chutes de antes da **D17**,
  copiados entre litologias, que a **D15** já declarava sem valor e que nada no código usava mais.
  Sobrou a `siena_white`. Regra nova e simples: **quem não está no arquivo não foi calibrado.**
  Quem escreve nele é o calibrador. Os valores antigos estão no histórico do git. Calibração feita
  é a que tem **`calibracao.json`** ao lado das vagas (limiar + critério escrito); é isso
  que o calibrador usa para dizer "calibrada". Estado: **44 de 180 vagas — a faixa A fechou em
  08/10/2026**, as 11 litologias com 4/4: `siena_white` (08/09/2026), `nevada_black`
  (02/10/2026), `ubatuba_green` e `ipanema_beige` (03/10/2026), `itaunas_white` (05/10/2026),
  `santa_cecilia` (06/10/2026), `white_mirage` (07/10/2026), `golden_storm`, `white_olympus`,
  `shadow_white` e `san_francisco_green` (08/10/2026). As duas últimas tinham sido puladas e
  foram selecionadas sem a opinião de especialista; elas, a `white_mirage` e a `golden_storm` são
  rochas movimentadas (ver `docs/dataset.md` e **D20**). **3 de 45 litologias calibradas** —
  `siena_white` (01/10/2026, refeita em 09/10), `nevada_black` e `ubatuba_green` (09/10/2026);
  as outras 8 da faixa A esperam calibração.
- **Mais de uma máquina.** O Henrique alterna entre este PC e outro. O que precisa existir nos
  dois vai para o **git**; `_cache/`, `results/`, o `.venv` e o `sam3.pt` não vão, e cada máquina
  tem os seus. **A versão do ultralytics pode diferir entre elas** — cada `calibracao.json` grava
  a versão usada. A equivalência da **D18** depende dessa versão, não da máquina, então a
  verificação agora **viaja no git**: o `verificar_d18.py`, ao passar, anota a versão em
  `AI/SAM/d18_verificado.json`. Verificar numa máquina vale para a outra na mesma versão. Quem
  responde "a versão daqui já está coberta?" é o `ambiente.py` — não a memória de ninguém.
- **`cv2.imread` não abre caminho com acento no Windows** — e o caminho deste projeto tem acento
  (`…ARIA - Análise e Reconhecimento…`). A armadilha é que **importar o ultralytics
  monkey-patcha `cv2.imread`** por uma versão que aceita Unicode: quem importa ultralytics antes
  nunca vê o bug, quem não importa recebe `None` silencioso. Em código que não depende do
  ultralytics, use `np.fromfile` + `cv2.imdecode` (ver `calibrator.abrir_imagem`).
- **Não usar `masks.xyn` — usar `sam_cache.pecas_por_deteccao`** (**D21**, 09/10/2026). O
  `masks.xyn` funde os contornos soltos de uma detecção numa só poligonal
  (`masks2segments(strategy="all")`), ligando-os por pontes de ida e volta, que viravam retas na
  preview e iam para o `.txt`. Hoje cada contorno é um polígono próprio: uma detecção é uma
  **lista de peças**, no cache (`polys[i]`) e no `.txt` (uma linha por peça). "Marcação", na
  regra e no `calibracao.json`, continua sendo **detecção**, não peça. Cache `.npz` de antes da
  mudança é tratado como ausente (`sam_cache.cache_atual`) e recapturado sozinho.
- **`rock_viewer.py` ordena por volume de dados** (faixa A primeiro), não em ordem alfabética: a
  ordem **é** a prioridade de trabalho. Cada litologia tem 4 vagas nomeadas pelo papel.
- **Litologia 4/4 abre em modo revisão**, não recusa. `rock_viewer.py <rocha>` numa litologia
  completa mostra a grade com as 4 escolhas no topo (serve para só olhar as imagens — Enter sai
  sem alterar nada) e oferece substituir uma vaga. Se há `calibracao.json`, a troca exige digitar
  `SUBSTITUIR`, e a troca é registrada em `substituicoes` do `meta.json`. Imagem nova na vaga
  **apaga o `_cache/<vaga>__*.npz`** daquela vaga — o cache é indexado pela vaga, não pela
  imagem, e reaproveitá-lo daria curva e polígonos da imagem antiga (reescolher a MESMA imagem
  não apaga nada). O calibrador lê esse histórico: vaga trocada depois do `calibrado_em` faz a
  litologia aparecer como **⊘ desatualizada**, não como calibrada — o limiar continua escrito,
  mas não foi escolhido nas 4 imagens atuais. Quem grava `calibracao.json` continua sendo só
  o calibrador.
- **`sam_cache.py`** implementa a varredura offline de limiar (**D18**): roda o SAM uma vez com
  `conf` no piso, guarda scores + polígonos, e filtra sem GPU. Equivalência provada no fonte do
  ultralytics **e verificada empiricamente** — `python verificar_d18.py` compara a filtragem do
  cache com o SAM rodando de novo em cada limiar.
- **O calibrador é o dono do limiar; o `inference.py` é o dono das máscaras finais.** O
  `calibrator.py` não escreve em `results/` nem gera `.txt` — ele decide sondas e limiar e grava
  `rock_prompts.json` + `calibracao.json`.
