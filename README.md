# ARIA — Análise e Reconhecimento Inteligente de Anomalias

Pipeline de visão computacional para marcar anomalias na superfície de chapas de rochas
ornamentais. TCC de Bacharelado em Sistemas de Informação, IFES Cachoeiro de Itapemirim.

## O problema

Decidir o que é defeito numa chapa de rocha é uma escolha, não uma medida. A mesma feição pode
valorizar uma chapa e desclassificar outra, conforme a rocha, o cliente e o lote. Hoje esse
critério mora na cabeça de cada inspetor e muda de pessoa para pessoa.

O ARIA não tenta acabar com essa arbitrariedade. Ele tira o critério da cabeça do inspetor e o
escreve num arquivo, como um conjunto de palavras e limiares por rocha, que pode ser lido,
discutido, versionado e aplicado do mesmo jeito mil vezes.

## Como funciona

```
Imagem da chapa
      ↓
Xception            identifica a rocha (litologia)
      ↓
SAM3 (Professor)    fora da linha de produção: marca as anomalias, guiado pelas
                    palavras e limiares calibrados para aquela rocha
      ↓
YOLO11-seg (Aluno)  na linha de produção: aprende a reproduzir as marcações, rápido
                    (desenho previsto; trabalho futuro nesta versão)
```

O modelo grande (SAM3) é caro, então roda uma vez, só para produzir as marcações. Quem rodaria
na produção é o modelo pequeno (YOLO).

**As palavras não são rótulos.** `crack`, `vein`, `Stain`, `Dark patches`, `light spot`,
`scratch` e `white stain` são palavras que fazem o modelo reagir a certas aparências. Elas não
afirmam o que a região é: por isso todas as marcações viram uma classe só, "anomalia".

## O experimento

Pergunta: um critério calibrado para cada rocha marca melhor do que um critério único para todas?

São quatro versões do Professor, cada uma diferente da anterior em uma coisa só: limiar único
para todas as rochas; limiar da regra por rocha, com todas as palavras; só as palavras que o
autor aceitou para aquela rocha; e o limiar ajustado pelo autor. Nenhuma exige treino.

A avaliação é uma **auditoria cega**: uma avaliadora vê uma marcação por vez, sem saber de que
versão ela veio, e responde se a marcaria como defeito. Daí saem a precisão e o recall relativo de
cada versão. O autor julga a mesma amostra, separado, e a concordância entre os dois mede quanto o
próprio julgamento varia. Detalhes em [`docs/decisoes.md`](docs/decisoes.md) (D4, D5 e D7).

Treinar os modelos YOLO especialistas por rocha e compará-los a um modelo único ficou como
trabalho futuro.

## Dataset

**34.630 imagens · 45 litologias · conjunto público do Kaggle**, dividido em train/val/test. O
desbalanceamento é natural: de 106 a 4.588 imagens por rocha.

| Faixa | Imagens por rocha | Rochas | Estado |
|---|---|---|---|
| A | 1.000 ou mais | 11 | selecionadas e calibradas |
| B | 500 a 999 | 6 | — |
| C | 200 a 499 | 14 | — |
| D | menos de 200 | 14 | — |

Detalhes em [`docs/dataset.md`](docs/dataset.md).

## Uso

```bash
cd AI
.venv\Scripts\python.exe ambiente.py                         # o que esta máquina tem e pode rodar

cd SAM
..\.venv\Scripts\python.exe rock_viewer.py                   # escolher as 4 imagens de uma rocha
..\.venv\Scripts\python.exe -m streamlit run calibrator.py   # calibrar palavras e limiares
..\.venv\Scripts\python.exe inference.py                     # rodar o Professor nas rochas calibradas
```

Cada rocha tem quatro imagens de calibração: uma de *descoberta*, que define quais palavras
entram, e três de *limiar* (sutil, típica e forte), que juntas definem o limiar. Uma imagem só não
serve: a mais rica em anomalias puxa o limiar para cima, e a mais sutil, para baixo. A escolha é
sempre manual e só do `train/`, para não contaminar a avaliação.

Instalação e o resto dos comandos estão no [`CLAUDE.md`](CLAUDE.md).

## Estrutura

```
AI/
├── dataset/       # train/ val/ test/ — somente leitura, fora do git
├── models/        # pesos (fora do git)
├── SAM/           # Professor: seleção, calibração, inferência e auditoria
├── Xception/      # classificador de litologia
└── YOLO/          # Aluno (trabalho futuro)
docs/              # fonte de verdade do projeto
apresentações/     # monografia (Overleaf), artigos e apresentações
```

## Documentação

A verdade do projeto está em [`docs/`](docs/): [`decisoes.md`](docs/decisoes.md) (o que está
decidido e por quê), [`roadmap.md`](docs/roadmap.md) (onde cada parte está) e
[`pendencias.md`](docs/pendencias.md) (o que falta). A monografia em `apresentações/Overleaf/TCC/`
está alinhada com as decisões; os artigos antigos da mesma pasta, não (D13).
