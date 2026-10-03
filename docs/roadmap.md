# Roadmap — ARIA

Estado vivo do desenvolvimento e ordem de execução. As decisões que justificam esta ordem estão
em [`decisoes.md`](decisoes.md).

> Última atualização: 2026-10-02
> Prazo-alvo de trabalho: **15/10/2026** — estimativa dada pelo Henrique em 26/09/2026
> ("deve ser até dia 15"). **Ainda não confirmada com o Rafael** — ver `pendencias.md`.
> São ~19 dias: o cronograma abaixo assume que só o **Experimento 1** (Fase 2) roda.

---

## Onde o projeto realmente está

| Componente | Estado |
|---|---|
| `rock_viewer.py` — seleção das 4 vagas | ✅ reescrito para o protocolo D17 |
| `calibrator.py` — UI de calibração | ✅ **reescrito** (2026-09-26): 3 abas, um slider, 4 previews |
| `inference.py` — inferência sobre `selectRocks/` | ✅ funciona; já aceita o layout em pasta |
| `sam_cache.py` — varredura offline de limiar | ✅ núcleo pronto (D18) |
| `verificar_d18.py` — prova empírica da D18 | ✅ **novo**: 32 comparações, nenhuma divergência |
| `rock_prompts.json` | 🟡 **provisório** (**D15**) — 46 entradas, mas só 13 configurações distintas |
| `selectRocks/` | 🟡 **16 de 180 vagas** — `siena_white`, `nevada_black`, `ubatuba_green`, `ipanema_beige` 4/4; restam 28 na faixa A (`shadow_white` pulada por ora) |
| Litologias com `calibracao.json` | 🟡 **1 de 45** — `siena_white` (01/10/2026) |
| Inferência em lote sobre o dataset | ❌ **não existe** |
| Conjunto-ouro anotado | ❌ não existe |
| Avaliação (IoU / mAP / falso positivo) | ❌ não existe |
| Treino e avaliação YOLO | ❌ não existe (`AI/YOLO/` está vazio) |
| Integração Xception | 🔴 **sem pesos** — o material do DeepStoneAI (02/10) tem a receita (`Xception.ipynb`, Keras) mas nenhum modelo salvo. Plano: **reproduzir** em PyTorch (**D19**) — ver Fase 4 |
| **Monografia** (`Overleaf/TCC/`) | 🟡 **reestruturada em 26/09**: bibliografia (37 entradas), esqueleto, Introdução, Fundamentação, Metodologia e Conclusão escritas; Resultados só com o que já foi medido |
| Artigo de PD1 e LatinoWare2026 | 🔴 intocados — continuam desalinhados (**D13**) |

> ⚠️ A monografia **nunca foi compilada** depois da reestruturação: não há LaTeX na máquina de
> desenvolvimento. `Overleaf/TCC/verificar_tex.py` faz a conferência estrutural possível
> (citação sem entrada no `.bib`, `ef` sem `\label`, ambiente desbalanceado, figura ausente),
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

**Estado: 16 de 180 vagas; 1 de 45 litologias calibrada.** A faixa A são as 11 primeiras —
**44 vagas**, das quais 16 feitas (`siena_white`, em 08/09/2026, calibrada em 01/10/2026;
`nevada_black`, em 02/10/2026; `ubatuba_green` e `ipanema_beige`, em 03/10/2026; as três a
calibrar) e **28 pendentes**. A `shadow_white` foi pulada em 03/10 (difícil julgar o que é
defeito; ajuda pedida na faculdade). Ordem de trabalho da faixa A:
`siena_white` ✅, `nevada_black` ✅ (seleção), `ubatuba_green` ✅ (seleção), `ipanema_beige` ✅ (seleção), `shadow_white` ⏸️, `itaunas_white`,
`santa_cecilia`, `san_francisco_green`, `white_mirage`, `golden_storm`, `white_olympus`.

```bash
cd AI/SAM
python rock_viewer.py          # entrega siena_white / descoberta, e segue em ordem de faixa
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

> **A próxima ação do Henrique é selecionar as vagas do resto da faixa A** (`ubatuba_green` é a
> próxima) e calibrar cada litologia ao fechar as 4 vagas dela.

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
3. **Rodar o Professor duas vezes por imagem** — configuração calibrada e configuração `default`.
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
- **Decidir o que fazer com a ponte entre contornos.** `masks.xyn` usa
  `masks2segments(strategy="all")`: quando a máscara de uma detecção tem vários contornos, eles
  são fundidos numa poligonal só, ligados por pontes de ida e volta — e é essa poligonal que o
  `inference.py` grava no `.txt`. Medido em `siena_white/descoberta` (crack @0,08): **45 das 76**
  detecções têm mais de um contorno; a ponte tem área ~zero, então no agregado o polígono infla
  só **2,4%** sobre a máscara (IoU **0,93**), mas numa detecção com 18 contornos chegou a
  **2,5×**. Três saídas possíveis: usar `strategy="largest"` (perde área real), quebrar cada
  contorno em uma instância separada (mais fiel, muda a contagem de instâncias), ou aceitar e
  declarar. **Decisão metodológica — do Henrique.**
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
   2. ⏳ **treinar** em 480 × 480 — combinado para depois de 02/10, com a GPU livre (o
      calibrador também usa GPU; selecionar imagens não). Medido: ~186 imagens/s → ~2,6 min por
      época, **≤ ~1h10** no pior caso (25 épocas sem parada antecipada);
   3. **avaliar** no `test/` uma vez; se ficar claramente abaixo do original, testar com
      ampliação (regra de recuo da D19);
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
