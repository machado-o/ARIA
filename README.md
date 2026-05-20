# Hartheus.AI — ARIA Pipeline (`ARIA`)

Pipeline de segmentação semântica de avarias em rochas ornamentais para controle de qualidade em linha de produção. TCC de Bacharelado em Sistemas de Informação — IFES Cachoeiro de Itapemirim.

## O que é ARIA

**ARIA** (Análise e Reconhecimento Inteligente de Anomalias) é um pipeline hierárquico de IA:

```
Imagem de rocha
      ↓
Classificador Xception  →  identifica o tipo de rocha
      ↓
SAM3 (professor)        →  gera anotações poligonais por tipo, guiado por prompts calibrados
      ↓
Labels YOLO (.txt)      →  formato de segmentação, prontos para treino
      ↓
YOLO (aluno)            →  45 modelos especialistas (1 por tipo de rocha); inferência rápida em produção
```

Esta branch cobre a fase do **SAM3 como professor**: calibrar prompts e limiares de confiança por tipo de rocha para gerar anotações de alta qualidade que depois treinam o YOLO.

## Dataset

45 tipos de rocha em `AI/Dataset/{train,val,test}/<rock_name>/`.

| Prontidão | Quantidade | Status |
|-----------|-----------|--------|
| 500+ imagens | 17 tipos | Prontos para treino YOLO |
| 200–500 imagens | ~12 tipos | Borderline, monitorar overfitting |
| <200 imagens | 7 tipos | SAM-only por enquanto |

## Workflow

### 1. Selecionar imagem representativa

```bash
cd AI/SAM
python rock_viewer.py              # próxima rocha sem seleção
python rock_viewer.py <rock_name>  # rocha específica
python rock_viewer.py --cols 6     # grade mais larga
```

Abre contact sheet HTML no browser. Clique na imagem para abrir lightbox (←→ navegam, Enter seleciona). Digitar o número no terminal copia a imagem para `selectRocks/<rock_name>.EXT`.

**Regra:** a seleção é sempre manual — usar o modelo para escolher a imagem de calibração é raciocínio circular.

### 2. Calibrar prompts

Editar `rock_prompts.json` diretamente: chave = nome da pasta em `SAM/selectRocks/`, valor = `{ "prompt_label": conf_float }`.

```json
{ "crack": 0.1, "vein": 0.007, "Stain": 0.3 }
```

Rodar `inference.py` e verificar os resultados em `results/`. O `calibrator.py` (UI Streamlit para calibração interativa) está sendo reconstruído.

**Dica:** rochas com fundo escuro (nevada_black, sao_gabriel_black) usam `light spot` em vez de `Dark patches` nos prompts.

### 3. Rodar inferência

```bash
cd AI/SAM
python inference.py   # lê selectRocks/, grava máscaras em results/
```

**Gotcha:** `inference.py` aplica um monkey-patch em `clip.simple_tokenizer.SimpleTokenizer` para compatibilidade com Ultralytics SAM3. Não remover o bloco `try/except` no topo do arquivo.

## Docker

```bash
# A partir de /docker
docker compose up --build ai    # sobe o serviço de IA (batch, sem porta exposta)
docker compose down
```

Suporta sm_50 a sm_120 (Maxwell → Blackwell) via PyTorch cu128.

## Estrutura

```
AI/
├── Dataset/                # train/ val/ test/ — compartilhado entre modelos
├── models/                 # pesos dos modelos — compartilhado
├── SAM/                    # fase do professor
│   ├── inference.py        # inferência em lote
│   ├── rock_viewer.py      # seletor de imagem representativa
│   ├── rock_prompts.json   # prompts e confs por tipo (gitignored)
│   ├── selectRocks/        # imagem representativa por tipo
│   ├── results/            # máscaras .jpg + labels .txt (YOLO format)
│   └── samples/            # exemplos de resultado para documentação
├── Xception/               # classificador de tipo de rocha (futuro)
├── YOLO/                   # fase do aluno (futuro)
└── requirements.txt
TCC/                        # documentação acadêmica
BRANCHES.md                 # comparação com feat/matheus + plano híbrido
```

## Relação com outras branches

Ver [`PROJETO.md`](PROJETO.md) para o contexto da plataforma Hartheus, comparação com `feat/matheus` e o plano de integração futura.
