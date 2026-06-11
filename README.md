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

```bash
cd AI/SAM
.venv\Scripts\python.exe -m streamlit run calibrator.py
```

UI interativa para ativar prompts, ajustar limiares de confiança, visualizar as máscaras geradas e salvar em `rock_prompts.json`. Alternativa manual: editar `rock_prompts.json` diretamente (`{ "prompt_label": conf_float }`).

**Dica:** rochas com fundo escuro (nevada_black, sao_gabriel_black) usam `light spot` em vez de `Dark patches` nos prompts.

### 3. Rodar inferência

```bash
cd AI/SAM
python inference.py   # lê selectRocks/, grava máscaras em results/
```

**Gotcha:** `inference.py` aplica um monkey-patch em `clip.simple_tokenizer.SimpleTokenizer` para compatibilidade com Ultralytics SAM3. Não remover o bloco `try/except` no topo do arquivo.

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
└── YOLO/                   # fase do aluno (futuro)
docs/                       # base de conhecimento e governança (.md): decisões, diretrizes, ROADMAP, PENDENCIAS
Hartheus.md                 # contexto da plataforma Hartheus e branches
```

## Relação com outras branches

Ver [`Hartheus.md`](Hartheus.md) para o contexto da plataforma Hartheus e o plano de integração futura.
