# Roadmap — ARIA

Estado vivo do desenvolvimento e ordem de execução. As decisões que justificam esta ordem estão
em [`decisoes.md`](decisoes.md).

> Última atualização: 2026-08-23
> Prazo-alvo de trabalho: **01/10/2026** (a confirmar com o orientador — ver `pendencias.md`)

---

## Onde o projeto realmente está

| Componente | Estado |
|---|---|
| `rock_viewer.py` — seleção das 4 vagas | ✅ reescrito para o protocolo D17 |
| `calibrator.py` — UI de calibração | 🟡 lê o layout novo; falta a interface das 4 vagas |
| `inference.py` — inferência sobre `selectRocks/` | ✅ funciona; já aceita o layout em pasta |
| `sam_cache.py` — varredura offline de limiar | ✅ núcleo pronto e testado (D18) |
| `rock_prompts.json` | 🟡 **provisório** (**D15**) — 46 entradas, mas só 13 configurações distintas |
| `selectRocks/` | 🔴 **zerado** — 0 de 180 vagas (45 litologias × 4, D17) |
| Inferência em lote sobre o dataset | ❌ **não existe** |
| Conjunto-ouro anotado | ❌ não existe |
| Avaliação (IoU / mAP / falso positivo) | ❌ não existe |
| Treino e avaliação YOLO | ❌ não existe (`AI/YOLO/` está vazio) |
| Integração Xception | 🟡 modelo já testado neste dataset com bom resultado; falta o código de roteamento |

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

**Estado: 0 de 180 vagas** (45 litologias × 4). A faixa A são as 11 primeiras — **44 vagas**.

```bash
cd AI/SAM
python rock_viewer.py          # entrega siena_white / descoberta, e segue em ordem de faixa
python rock_viewer.py --all    # mostra val/ e test/ para estudo (não selecionáveis)
```

A ferramenta conduz vaga por vaga, dizendo o que procurar em cada uma. Ela só oferece imagens do
`train/` e recusa qualquer outra (**D17**).

Depois de a **primeira litologia** estar completa (4/4), o próximo passo é terminar o
`calibrator.py`: exibir as 4 imagens lado a lado e escolher o limiar que melhor serve ao
**conjunto**. O núcleo já existe em `sam_cache.py` (**D18**) — falta a interface.

> ⚠️ **Ainda em aberto (TODO da D17):** o valor de X na regra *"o maior limiar que ainda marca ao
> menos X% das feições anotadas"*. Só dá para fixar depois da primeira litologia calibrada.

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

1. **Xception como roteador.** O modelo já foi testado neste dataset com bom resultado; falta o
   código que recebe a imagem, identifica a litologia e seleciona a configuração de sondas +
   o Aluno correspondente.
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
