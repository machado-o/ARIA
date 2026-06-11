# Arquitetura do Pipeline — ARIA

## Visão Geral

Pipeline hierárquico em dois estágios para controle de qualidade em rochas ornamentais:

```
            Pipeline ARIA
┌──────────────────────────────────────┐
│  Imagem da chapa                     │
│        │                             │
│        ▼                             │
│  ┌─────────────────────────────┐     │
│  │  Estágio 1: Classificador   │  → identifica tipo litológico/comercial
│  │  Xception (DeepStoneAI)     │     │
│  └─────────────┬───────────────┘     │
│                │ tipo de rocha       │
│                ▼                     │
│  ┌─────────────────────────────┐     │
│  │  Estágio 2: Segmentador     │  → detecta anomalias superficiais
│  │  ┌──────────────────────┐   │     │
│  │  │ SAM3 (Teacher)       │   │  gera anotações de polígonos
│  │  └──────────────────────┘   │     │
│  │  ┌──────────────────────┐   │     │
│  │  │ YOLO11-seg (Student) │   │  inferência rápida (produção)
│  │  └──────────────────────┘   │     │
│  └─────────────────────────────┘     │
│        │                             │
│        ▼                             │
│  Polígonos de anomalias              │
│  (formato YOLO, coords normalizadas) │
└──────────────────────────────────────┘
```

---

## Estágio 1 — Classificador (DeepStoneAI)

- **Modelo:** Xception
- **Tarefa:** Identificar o nome comercial/litológico da chapa de rocha entre as 45 classes do dataset e **rotear** a imagem para o fluxo de análise correspondente
- **Estado:** Validado em projeto anterior (DeepStoneAI) com bons resultados; será integrado ao pipeline
- **Possível substituição:** Se houver tempo, pode-se avaliar arquiteturas mais recentes (EfficientNetV2, ConvNeXt etc.)
- **Integração com Estágio 2:** Em aberto — ver seção "Conexão entre Estágios"

---

## Estágio 2 — Segmentador (SAM3 + YOLO11)

### Teacher: SAM3

- **Modelo:** SAM3 (Segment Anything Model 3) via Ultralytics — Foundation Model com capacidade zero-shot
- **Embeddings de texto:** OpenAI CLIP
- **Função:** Gerar anotações de polígonos de alta qualidade sem anotação manual humana, processando o dataset de forma **offline** (em batch, fora da linha de produção)
- **Entrada:** Imagem + prompts de texto calibrados por tipo de rocha (injeção de conhecimento de domínio)
- **Saída:** Polígonos de anomalias em formato YOLO + visualizações

**Estratégia de prompts (`rock_prompts.json`):**

Cada tipo de rocha possui um conjunto de features com limiares de confiança calibrados individualmente.

| Feature          | Descrição                    | Color (vis.) |
| ---------------- | ------------------------------ | ------------ |
| `crack`        | Fissuras na superfície        | Vermelho     |
| `vein`         | Veios minerais / estrias       | Azul         |
| `Stain`        | Manchas / descoloração       | Laranja      |
| `Dark patches` | Áreas escuras (rochas claras) | Preto        |
| `light spot`   | Pontos claros (rochas escuras) | Ciano        |

**Nota sobre qualidade dos prompts — prompts contextuais vs. palavras simples:**

O CLIP foi treinado em legendas e descrições de imagens, não em palavras isoladas. O paper original do CLIP identificou que o template `"a photo of a [X]"` consistentemente supera apenas `"X"` em zero-shot. Para o domínio de rochas ornamentais, prompts contextuais como `"crack on a stone surface"` ou `"mineral vein in granite"` podem produzir embeddings mais precisos que `"crack"` ou `"vein"` isolados, pois desambiguam o contexto visual (ex.: "vein" cobre veias sanguíneas, veios minerais, etc.). Testável diretamente via `rock_prompts.json` + `inference.py` — candidato a análise de sensibilidade nos resultados do TCC.

**Configuração padrão (fallback):**

```json
{ "crack": 0.1, "vein": 0.007, "Stain": 0.3 }
```

**Grupos de calibração por cor/textura:**

| Grupo                | Rochas                                                                                            | Características                                                         |
| -------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Brancas/claras       | white_*, itaunas_white, shadow_white, siena_white, vitoria_white, naica                           | Incluem "Dark patches"; limiares padrão                                 |
| Escuras              | nevada_black, sao_gabriel_black                                                                   | "light spot" em vez de "Dark patches"; limiares mais baixos (0.05, 0.01) |
| Amarelas/bege        | giallo_*, golden_storm, icarai_yellow, maracuja_yellow, solarius, splendor_gold, santa_cecilia* | Grupo intermediário; incluem "Dark patches"                             |
| Verdes/quartzitos    | quartzito_*, san_francisco_green, new_caledonia, ubatuba_green                                    | Sem "Dark patches"; crack 0.06–0.08                                     |
| Coloridas (vermelho) | xango_red, tabaco_red                                                                             | Incluem "light spot"; crack 0.07                                         |
| Especiais            | kalahari, perla_venato, ornamental, rocky_mountain, olympios, ipanema_beige, white_liberdade      | Configurações individuais ou próximas do padrão                      |

**Pipeline de inferência (`inference.py`):**

1. Lê imagens de `selectRocks/` (uma imagem representativa por tipo de rocha)
2. Para cada imagem: carrega prompts de `rock_prompts.json` pelo nome da rocha
3. Para cada prompt: roda SAM3 com limiar configurado
4. Salva resultados individuais por prompt e imagem combinada em `results/<rock_name>/`
5. Grava polígonos em `.txt` (formato YOLO, coordenadas normalizadas 0–1)

**Formato de saída:**

```
<class_id> <x1> <y1> <x2> <y2> ... <xN> <yN>
```

Class IDs gerados pelo `inference.py`: 0=vein, 1=crack, 2=Stain, 3=Dark patches, 4=light spot.
São colapsados para `class_id=0` antes do treino YOLO — ver decisão **D2** em `decisoes.md`.

**Gotcha técnico obrigatório:** `inference.py` aplica monkey-patch em `clip.simple_tokenizer.SimpleTokenizer` para compatibilidade com Ultralytics SAM3. O bloco `try/except` no topo do arquivo é obrigatório — sem ele o modelo falha silenciosamente. Não remover.

### Student: YOLO11

- **Versão:** YOLO11 (YOLOv11-seg) — versão estudada e referência para o TCC
- **Versões alternativas a avaliar:** YOLO12 e YOLO26, lançadas após o período de estudo inicial; se houver tempo, comparar com YOLO11 como baseline de versão
- **Função:** Motor rápido de inferência para linha de produção industrial (tempo real)
- **Vantagem:** Arquitetura compacta e eficiente, adequada para Edge Computing — funciona em hardware com restrições de memória como câmeras industriais e dispositivos embarcados
- **Input esperado:** Anotações de polígonos geradas pelo SAM (formato YOLO, class_id=0 binário)
- **Quantidade:** 45 modelos especializados — um por tipo de rocha (pipeline ARIA); 1 modelo generalista (baseline de comparação)
- **Estado:** Não iniciado — aguarda conclusão da fase de calibração SAM

---

## Conexão entre os Estágios

Mecanismo técnico: o Xception identifica o tipo litológico da chapa e usa esse resultado para escolher os prompts e limiares calibrados em `rock_prompts.json`. O SAM então segmenta com conhecimento de domínio específico daquela rocha, e a imagem é roteada para o modelo YOLO especialista correspondente. Em produção: Xception identifica o tipo → roteia para o YOLO do tipo.

A definição do **experimento central (45 especialistas × 1 generalista)** e a hipótese de benefício associada são fonte única em `decisoes.md` (**D3**, **D4**).

---

## Loop de Aprendizado Ativo

Trabalho futuro — fora do escopo desta entrega. Conceito: SAM refinaria inferências de baixa confiança do YOLO em produção, melhorando o aluno continuamente sem intervenção humana. Ver `decisoes.md` (**D8**).

---

## Stack Técnica

| Componente              | Tecnologia                                             |
| ----------------------- | ------------------------------------------------------ |
| Linguagem               | Python 3.11                                            |
| Deep Learning           | PyTorch + CUDA                                         |
| Classificador           | Xception                                               |
| Teacher (segmentação) | SAM3 via Ultralytics                                   |
| Text embeddings         | OpenAI CLIP                                            |
| Aluno (inferência)     | YOLO11-seg (YOLO12 / YOLO26 a avaliar se houver tempo) |
| Visualização          | OpenCV                                                 |

---

## Estado Atual

O estado vivo do desenvolvimento e os próximos passos são fonte única em `../ROADMAP.md`.
