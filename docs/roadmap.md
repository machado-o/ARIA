# Roadmap — ARIA

Estado vivo do desenvolvimento e ordem de execução. As decisões que justificam esta ordem estão
em [`decisoes.md`](decisoes.md).

> Última atualização: 2026-10-09
> **Dois horizontes** (informado pelo Henrique em 09/10/2026):
> 1. **Prévia na Jacitec, 20 a 23/10/2026** — o marco apertado. A janela útil antes dela é
>    **até 10/10**, porque a agenda de outubro ocupa de 11 a 19/10 — ver `pendencias.md`.
> 2. **Entrega final do TCC: pelo menos um mês depois da Jacitec**, ou seja, não antes de
>    ~23/11/2026. A data exata ainda não está fechada — ver `pendencias.md`.
>
> O prazo-alvo de **15/10/2026** que este arquivo usava (estimativa de 26/09) está **superado**.
> O cronograma abaixo foi montado sobre ele e assume que só o **Experimento 1** (Fase 2) roda —
> suposição a rever com o prazo novo; rever é decisão do Henrique, ainda não tomada.

---

## Onde o projeto realmente está

| Componente | Estado |
|---|---|
| `rock_viewer.py` — seleção das 4 vagas | ✅ reescrito para o protocolo D17; **modo revisão** (2026-10-08) numa litologia 4/4 |
| `calibrator.py` — UI de calibração | ✅ **reescrito** (2026-09-26): 3 abas, um slider, 4 previews |
| `inference.py` — inferência sobre `selectRocks/` | ✅ funciona; já aceita o layout em pasta |
| `sam_cache.py` — varredura offline de limiar | ✅ núcleo pronto (D18) |
| `verificar_d18.py` — prova empírica da D18 | ✅ **novo**: 32 comparações, nenhuma divergência |
| `rock_prompts.json` | 🟡 **provisório** (**D15**) — 46 entradas, mas só 13 configurações distintas |
| `selectRocks/` | 🟡 **44 de 180 vagas** — **faixa A completa**: as 11 litologias com 4/4, incluindo `shadow_white` e `san_francisco_green`, feitas em 08/10/2026 depois de puladas |
| Litologias com `calibracao.json` | 🟡 **3 de 45** — `siena_white` (01/10/2026, refeita em 09/10), `nevada_black` e `ubatuba_green` (09/10/2026) |
| Inferência em lote sobre o dataset | ❌ **não existe** |
| Conjunto-ouro anotado | ❌ não existe |
| Avaliação (IoU / mAP / falso positivo) | ❌ não existe |
| Treino e avaliação YOLO | ❌ não existe (`AI/YOLO/` está vazio) |
| Integração Xception | 🟡 **treinado** (03/10, D19): 96,72% no `test/` (98,71% no `val/`), abaixo dos 99,21% do original. Com o sorteio por imagem do original, o mesmo modelo dá 99,92%: a diferença vem da divisão dos dados. Os dois números são reportados (D19, 06/10); falta só integrar o roteador. Ver Fase 4 |
| **Monografia** (`Overleaf/TCC/`) | 🟡 **reestruturada em 26/09**: bibliografia (37 entradas), esqueleto, Introdução, Fundamentação, Metodologia e Conclusão escritas; Resultados só com o que já foi medido |
| Artigo de PD1 e LatinoWare2026 | 🔴 intocados — continuam desalinhados (**D13**) |

> ⚠️ A monografia **nunca foi compilada** depois da reestruturação: não há LaTeX na máquina de
> desenvolvimento. `Overleaf/TCC/verificar_tex.py` faz a conferência estrutural possível
> (citação sem entrada no `.bib`, `
ef` sem `\label`, ambiente desbalanceado, figura ausente),
> mas o veredito é do Overleaf.

**O buraco estrutural:** `inference.py` lê de `selectRocks/`, que tem **uma imagem por rocha**.
Não existe caminho do Professor para um conjunto de treino do Aluno. É a primeira coisa a
resolver na Fase 3.

---

## ~~Fase 0 — Desbloqueio~~ ✅ 2026-08-23

1. ✅ **Casing de path.** `.gitignore` agora lista `AI/dataset/` **e** `AI/Dataset/`;
   `calibrator.py` e `rock_viewer.py` apontam para `../dataset`. Antes, numa máquina Linux, o
   `.gitignore` não protegia as 34.630 imagens.
2. ✅ **`class_id = -1` silencioso eliminado.** `validate_prompts()` roda **antes** de carregar o
   modelo e aborta nomeando a rocha e a sonda. Verificado: apontou `giallo_maracana: scratch`.
3. ✅ **Sonda exploratória não corrompe mais o `.txt`.** No `calibrator.py`, sonda fora do
   `CLASS_ID_MAP` aparece no preview mas não grava polígono, com aviso na tela.
4. ✅ **`scratch` registrado como id 5** (**D8**) nos dois arquivos.
5. ✅ **`rock_viewer.py` ordena por faixa de volume** (**D15**), não em ordem alfabética — a
   ordem em que ele entrega as rochas **é** a prioridade de trabalho.

---

## Fase 1 — Recalibração pela faixa A

Ver **D15** e **D17**. O `selectRocks/` foi **zerado em 2026-08-23**: as 14 imagens antigas foram
apagadas e a seleção recomeça com o protocolo de 4 vagas.

**Estado: 44 de 180 vagas; 3 de 45 litologias calibradas** (`siena_white`, `nevada_black` e
`ubatuba_green` — as duas últimas em 09/10/2026, a ~30 min cada; restam 8 na faixa A). A faixa A são as 11 primeiras —
**44 vagas, todas feitas** (`siena_white`, em 08/09/2026, calibrada em 01/10/2026;
`nevada_black`, em 02/10/2026; `ubatuba_green` e `ipanema_beige`, em 03/10/2026;
`itaunas_white`, em 05/10/2026; `santa_cecilia`, em 06/10/2026; `white_mirage`, em 07/10/2026;
`golden_storm`, `white_olympus`, `shadow_white` e `san_francisco_green`, em 08/10/2026; as dez a
calibrar). A `shadow_white` havia sido pulada em 03/10 e a `san_francisco_green` em 07/10 por ser
difícil julgar o que é defeito nelas; as duas foram selecionadas em 08/10 **sem a opinião de
especialista**, que não veio. Elas, a `white_mirage` e a `golden_storm` são rochas movimentadas
(lista em `dataset.md` → *Litologias movimentadas*). Ordem de trabalho da faixa A:
`siena_white` ✅, `nevada_black` ✅ (seleção), `ubatuba_green` ✅ (seleção), `ipanema_beige` ✅ (seleção), `shadow_white` ✅ (seleção), `itaunas_white` ✅ (seleção),
`santa_cecilia` ✅ (seleção), `san_francisco_green` ✅ (seleção), `white_mirage` ✅ (seleção), `golden_storm` ✅ (seleção), `white_olympus` ✅ (seleção).

> **A seleção da faixa A está completa** (44/44, em 08/10/2026). O que falta na faixa é
> calibração, não seleção: em 09/10/2026, 8 das 11 litologias ainda não têm `calibracao.json`.

```bash
cd AI/SAM
python rock_viewer.py          # próxima vaga pendente, em ordem de faixa
python rock_viewer.py <rocha>  # completa as vagas — ou, se já 4/4, abre em revisão
python rock_viewer.py --all    # mostra val/ e test/ para estudo (não selecionáveis)
```

A ferramenta conduz vaga por vaga, dizendo o que procurar em cada uma. Ela só oferece imagens do
`train/` e recusa qualquer outra (**D17**).

O `calibrator.py` **está pronto** (2026-09-26) e já calibrou a primeira litologia. Ele tem três
abas:

1. **Descoberta** — na chapa mais rica, quais sondas respondem a algo real;
2. **Limiar** — um slider e as 4 previews simultâneas, mais a curva *limiar × marcações* das
   três vagas de limiar, com o joelho marcado como **sugestão**;
3. **Fechar** — a contagem por vaga, o **critério escrito** (obrigatório) e o salvamento.

> **A próxima ação do Henrique é calibrar as oito litologias da faixa A que faltam** —
> `ipanema_beige`, `itaunas_white`, `santa_cecilia`, `white_mirage`, `golden_storm`,
> `white_olympus`, `shadow_white` e `san_francisco_green`. A `nevada_black` e a `ubatuba_green`
> foram calibradas em 09/10/2026. Não há mais vaga de faixa A para selecionar.

> **Primeira observação (`siena_white`, 01/10/2026):** o autor divergiu da regra nas 3 sondas
> admitidas (`vein`, `Stain`, `Dark patches`), sempre para cima — limiar de trabalho ≈ 2× o joelho.
> Uma litologia não é padrão; se repetir na faixa A, é o resultado previsto na **D17**
> (*"onde a curva engana"*). A forma da regra já está fechada na D17 (joelho, sem parâmetro livre).

---

## Fase 2 — Experimento 1: SAM calibrado × SAM default

Ver **D5** e **D7**. Não exige treino nenhum — é o caminho mais curto até um resultado real.

1. **Montar o conjunto-ouro (~50 imagens).**
   10 litologias da faixa A × 5 imagens cada, **retiradas do split `test/`** para nunca
   contaminarem treino algum.
2. **Anotar às cegas — antes de rodar qualquer inferência sobre essas imagens.**
   A ordem é a metodologia: anotar depois de ver a máscara do modelo destrói a independência da
   anotação. Ferramenta externa (LabelMe/CVAT), exportando polígono.
3. **Rodar o Professor uma vez por imagem, com todas as sondas no piso, e filtrar os quatro
   braços do cache** (**D18**) — `default`, regra com todas as sondas, regra com as sondas do
   autor e calibrado pelo autor (**D5**, quarto braço acrescentado em 2026-10-10).
4. **Avaliar contra o ouro:** IoU, precisão, recall e taxa de falso positivo (D7), por braço e
   por litologia.
5. **Preferência pareada cega com especialista** (D7): máscara A × B embaralhadas, sem
   identificação. Produz a estatística de preferência.
6. **Escrever o resultado.** Inclui o par de figuras *default × calibrado* na mesma chapa — a
   evidência que hoje falta em todo o material escrito.

**Entregável:** H1 respondida, com número e com figura. Fecha como contribuição mesmo se a Fase 2
não terminar.

---

## Fase 3 — Experimento 2: especialistas × generalista, por faixa

Ver **D6**. Executa faixa por faixa. **Cada faixa é escrita antes de a seguinte começar.**

### 3.0 — Construir o que não existe

- **`sam_batch.py`** — roda o Professor sobre uma **amostra** de N imagens por litologia (não
  sobre as 34.630: são ~4 sondas por imagem, o custo é proibitivo e desnecessário), grava labels
  e monta a estrutura `images/` + `labels/` + `data.yaml` que o Ultralytics exige.
- **Pós-processamento do Professor** — área mínima, teto de instâncias por imagem, simplificação
  de polígono. No único exemplo existente (`samples/ice_leke.txt`) são **107 polígonos numa
  imagem**, com até 1.742 pontos. Um Aluno treinado nisso aprende a marcar tudo. Isso é etapa
  metodológica documentada, não gambiarra.
- ✅ **Ponte entre contornos — resolvida em 2026-10-09 (D21).** `masks.xyn` usa
  `masks2segments(strategy="all")`: quando a máscara de uma detecção tem vários contornos, eles
  são fundidos numa poligonal só, ligados por pontes de ida e volta — e era essa poligonal que o
  `inference.py` gravava no `.txt`. Medido em `siena_white/descoberta` (crack @0,08): **45 das
  76** detecções têm mais de um contorno; no agregado o polígono inflava só **2,4%** sobre a
  máscara (IoU **0,93**), mas numa detecção com 18 contornos chegou a **2,5×**. Decisão do
  Henrique: **cada contorno é um polígono próprio**. `sam_cache.pecas_por_deteccao` é a fonte
  única, usada pelo cache do calibrador e pelo `inference.py`; o `sam_batch.py` deve usá-la
  também. Sobra desta frente a **área mínima** (item acima): separar expõe fragmentos minúsculos.
- **`train.py` / `eval.py`** — treino dos Alunos e avaliação contra o conjunto-ouro da Fase 1.

### 3.1 — Faixa A (≥1000 imagens · 11 litologias)

Treinar os três braços (especialista, generalista, controle calibrado — D6), avaliar contra o
ouro, **escrever**.

### 3.2 — Faixa B (500–999 · 6 litologias)
### 3.3 — Faixa C (200–499 · 14 litologias)
### 3.4 — Faixa D (<200 · 14 litologias)

Cada uma repete o ciclo: treinar → avaliar → escrever. O gráfico final — desempenho da
especialização **em função do volume de dados** — é o resultado que responde à segunda metade de
H2 e que nenhum trabalho do referencial responde.

---

## Fase 4 — Integração e fechamento

1. **Xception como roteador — reprodução do DeepStoneAI (D19).** Não depende de calibração nem
   do SAM, então pode correr em paralelo às Fases 1–3. Ordem:
   1. ✅ **estruturar** `AI/Xception/` (02/10) — `common.py`, `train.py`, `evaluate.py`,
      `roteador.py`. Teste de fumaça passou (1.024 imagens, 2 + 2 épocas, de 39% para 60% de
      acurácia na validação); a avaliação recusa reavaliar o `test/`;
   2. ✅ **treinar** em 480 × 480 (03/10) — 15 + 10 épocas, sem parada antecipada, ~1h10 no
      venv novo (`AI/.venv`). Melhor checkpoint: fase finetune, época 7 (val_loss 0,034).
      Histórico em `AI/Xception/runs/xception_480/`;
   3. ✅ **avaliado no `test/`** (03/10, uma vez): **96,72%** de acurácia, 92,32% balanceada,
      F1 macro 0,924. No `val/`: 98,71% / 97,71% / 0,976. Fica abaixo dos 99,21% do original, e
      o `test/` já não pode ser reusado. **Achado, ainda não decidido:** os erros se concentram
      em poucas classes (`white_superiore` 0/36, `white_himalaya` 0,28, `naica` 0,69), e as
      chapas de `white_superiore` no `test/` parecem visualmente de **outro bloco/lote** que as
      de `train/` e `val/`. Hipótese: o split do dataset separa o `test/` por lote mas mistura
      chapas vizinhas entre `train/` e `val/`, o que deixa o val otimista. **Confirmado em
      04/10:** com o sorteio por imagem do DeepStoneAI, o mesmo modelo dá **99,92%** (run
      `xception_480_aleatorio`). **Decidido em 06/10 (D19):** os dois números vão para a
      monografia, sem ampliação e sem mais treino;
   4. o **roteador**: recebe a imagem, identifica a litologia e seleciona a configuração de
      sondas + o Aluno correspondente.
2. **Teste end-to-end** dos três estágios.
3. **FPS** — medir de fato, ou reduzir o discurso de tempo real no texto. Hoje o material escrito
   vende velocidade em várias seções e nunca mede.

---

## Fora do escopo (trabalhos futuros declarados)

- Loop de aprendizado ativo (**D11**)
- Rotulagem multi-classe (**D12**)
- Faixas não alcançadas do Experimento 2 (**D6**)
- Generalização além das 45 litologias
- API de serviço e integração com sistemas de chão de fábrica
