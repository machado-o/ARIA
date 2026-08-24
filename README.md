# ARIA — Análise e Reconhecimento Inteligente de Anomalias

Pipeline hierárquico de visão computacional para marcação automatizada de anomalias superficiais
em chapas de rochas ornamentais. TCC de Bacharelado em Sistemas de Informação — IFES Cachoeiro de
Itapemirim.

## O problema

A inspeção de anomalias em chapas de rocha é manual e, sobretudo, **arbitrária**. A fronteira
entre *feição natural* e *defeito comercial* depende da rocha, do cliente, do lote — e, hoje, do
inspetor. Esse critério vive implícito na cabeça de cada operador, e por isso muda de pessoa para
pessoa e de turno para turno.

**A proposta do ARIA não é eliminar essa arbitrariedade — é torná-la explícita.** O critério sai
da cabeça do inspetor e vira um conjunto de sondas e limiares por litologia, gravado em arquivo:
algo que pode ser auditado, discutido, versionado e aplicado de forma idêntica mil vezes.

## Como funciona

```
Imagem da chapa
      ↓
Xception            →  identifica a litologia e roteia
      ↓
SAM3 (Professor)    →  offline, em lote: gera os polígonos de anomalia,
                       guiado por sondas calibradas para aquela litologia
      ↓
Labels YOLO (.txt)  →  formato de segmentação, sem conversão intermediária
      ↓
YOLO11-seg (Aluno)  →  online: inferência rápida na linha de produção
```

O modelo de fundação é caro, então roda **uma vez**, fora da linha, só para produzir o conjunto de
treino. Quem roda em produção é o Aluno.

### As sondas não são rótulos

As palavras usadas como prompt (`crack`, `vein`, `Stain`, `Dark patches`, `light spot`) não
afirmam o que a região é — são chaves lexicais escolhidas por fazerem o CLIP+SAM3 responder a
certas assinaturas visuais. O objetivo é **maximizar cobertura**, não classificar. Por isso todas
as regiões recebem `class_id = 0` no treino: dizer que a região marcada por `"crack"` *é* uma
fissura seria uma afirmação que este trabalho não valida.

## O experimento

**Experimento 1 — o critério explícito funciona?**
Professor com sondas calibradas por litologia × Professor com configuração única global. Sem
treinamento nenhum, avaliado contra um conjunto-ouro anotado às cegas e por preferência pareada
cega de um especialista do setor.

**Experimento 2 — a especialização compensa, e a partir de quantos dados?**
Alunos especialistas (um por litologia) × Aluno generalista × Aluno de controle (único, treinado
com anotações calibradas — separa o efeito do número de modelos do efeito da qualidade da
anotação).

O segundo experimento roda **estratificado por volume de dados** e reporta resultado por faixa —
o que transforma o desbalanceamento do dataset de limitação em variável medida, e responde a uma
pergunta que o referencial não responde: *quantas imagens uma litologia precisa para que a
especialização compense?*

## Dataset

**34.630 imagens · 45 litologias · conjunto público (Kaggle)**, dividido em train/val/test.
O desbalanceamento é natural e não foi equalizado.

| Faixa | Critério | Litologias |
|---|---|---|
| A | ≥ 1000 imagens | 11 |
| B | 500 – 999 | 6 |
| C | 200 – 499 | 14 |
| D | < 200 | 14 |

Da maior (`siena_white`, 4.588) à menor (`white_samoa` e `quartzito_verde_sauipe`, 106).
Detalhamento em [`docs/dataset.md`](docs/dataset.md).

## Uso

```bash
cd AI/SAM
python rock_viewer.py                                     # preencher as 4 vagas da litologia
.venv\Scripts\python.exe -m streamlit run calibrator.py   # calibrar sondas e limiares
python inference.py                                       # rodar o Professor
```

Cada litologia tem **quatro** imagens de calibração, com papéis distintos: uma de *descoberta*
(define quais sondas entram) e três de *limiar* — sutil, típica e forte — que juntas definem o
limiar de confiança. Uma imagem só não serve: a mais rica em anomalias enviesa o limiar para
cima, a mais sutil enviesa para baixo.

A seleção é **sempre manual** (usar o próprio modelo para escolher seria raciocínio circular) e
sai **apenas do split `train/`**, para não contaminar a avaliação.

## Estrutura

```
AI/
├── dataset/       # train/ val/ test/ — somente leitura, fora do git
├── models/        # pesos (fora do git)
├── SAM/           # fase do Professor: seleção, calibração e inferência
├── Xception/      # classificador de litologia (a integrar)
└── YOLO/          # fase do Aluno (a implementar)
docs/              # fonte de verdade do projeto
Overleaf/          # monografia e artigo — saída desatualizada, ver docs/decisoes.md D13
```

## Documentação

A verdade do projeto está em [`docs/`](docs/) — começando por
[`decisoes.md`](docs/decisoes.md) (o que está fechado e por quê) e
[`roadmap.md`](docs/roadmap.md) (onde o desenvolvimento realmente está).
