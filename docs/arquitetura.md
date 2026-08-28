# Arquitetura do Pipeline — ARIA

Como o sistema funciona por dentro. As decisões que justificam este desenho estão em
[`decisoes.md`](decisoes.md); o estado de execução, em [`roadmap.md`](roadmap.md).

---

## Visão geral

```
  Imagem da chapa
        │
        ▼
  ┌─────────────────────────────┐
  │ Estágio 1 — Classificador   │  Xception: identifica a litologia
  │ (DeepStoneAI)               │  e roteia
  └──────────────┬──────────────┘
                 │ litologia
                 ▼
  ┌─────────────────────────────┐
  │ Estágio 2 — Segmentador     │
  │  ┌───────────────────────┐  │
  │  │ SAM3 (Professor)      │  │  offline, em lote: gera os polígonos
  │  └───────────────────────┘  │
  │  ┌───────────────────────┐  │
  │  │ YOLO11-seg (Aluno)    │  │  online: inferência rápida em produção
  │  └───────────────────────┘  │
  └──────────────┬──────────────┘
                 ▼
  Polígonos de anomalia (formato YOLO, coords normalizadas)
```

O Professor roda **uma vez, fora da linha**, para produzir o conjunto de treino. O Aluno é o que
roda em produção. Isso é o que torna o pipeline viável industrialmente: o custo do modelo de
fundação é pago uma vez, não por chapa.

---

## Estágio 1 — Classificador (Xception / DeepStoneAI)

- **Tarefa:** identificar a litologia entre as 45 classes e **rotear** — escolhe tanto a
  configuração de sondas quanto o Aluno especialista correspondente.
- **Estado:** modelo já treinado e testado neste mesmo dataset, com bom resultado. Falta o
  **código de roteamento** que o conecta ao Estágio 2 (`roadmap.md` → Fase 3).
- **Substituição possível:** EfficientNetV2, ConvNeXt — só se sobrar tempo.

---

## Estágio 2 — Professor: SAM3

- **Modelo:** SAM3 (Segment Anything Model 3) via Ultralytics — modelo de fundação com
  capacidade zero-shot.
- **Embeddings de texto:** OpenAI CLIP.
- **Papel:** gerar polígonos de anomalia sem anotação humana, processando o dataset **offline**.
- **Entrada:** imagem + conjunto de sondas de texto com limiar de confiança por litologia.
- **Saída:** polígonos em formato YOLO + visualizações.

### Sondas, não rótulos

As palavras usadas como prompt são **chaves lexicais de recall**, não classificações (**D2**).

| Sonda | Cor na visualização | Escopo |
|---|---|---|
| `crack` | vermelho | todas |
| `vein` | azul | todas |
| `Stain` | laranja | todas |
| `Dark patches` | preto | rochas claras |
| `light spot` | ciano | rochas escuras |
| `scratch` | magenta | pontual |

**O que a calibração realmente faz:** para cada litologia, define *quais* sondas entram e *com que
limiar*. Esse limiar é a materialização do critério arbitrário que separa feição de defeito —
tirado da cabeça do inspetor e colocado num arquivo auditável (**D3**).

**Prompts contextuais — hipótese não testada:** o paper do CLIP mostra que o template
`"a photo of a [X]"` supera consistentemente `"X"` isolado em zero-shot. Para rochas,
`"crack on a stone surface"` poderia desambiguar melhor que `"crack"` (a palavra "vein" cobre
tanto veia sanguínea quanto veio mineral). Testável via `rock_prompts.json` — candidato a análise
de sensibilidade **se sobrar tempo**. O crédito do achado é do paper do CLIP, não deste trabalho.

### Configuração — `rock_prompts.json`

```json
{ "<litologia>": { "<sonda>": <limiar de confiança> } }
```

Fallback: chave `"default"`. Se ela também faltar, `inference.py` usa
`{ "crack": 0.1, "vein": 0.007, "Stain": 0.3 }` hardcoded.

> **Estado real: o conteúdo é PROVISÓRIO (D15).** O arquivo tem 46 entradas mas apenas **13
> configurações distintas** — 18 litologias compartilham o mesmo conjunto. Não é calibração
> validada. A recalibração será feita do zero, pela ordem das faixas de volume, e só depois se
> decide se o critério é por litologia ou por grupo cromático. **Até lá, nenhum texto deve
> afirmar nenhuma das duas coisas.**

### Fluxo de `inference.py`

1. Lê imagens de `selectRocks/<litologia>/` (**4 por litologia** — D17).
2. Carrega as sondas da litologia em `rock_prompts.json`.
3. Roda o SAM3 uma vez por sonda, com o limiar configurado.
4. Grava o resultado individual por sonda e a imagem combinada em `results/<litologia>/`.
5. Grava os polígonos em `.txt` (YOLO, coords normalizadas 0–1).

> ⚠️ **Este script não produz conjunto de treino.** Ele processa só as imagens de calibração — é
> ferramenta de **calibração**, não de produção de dataset. O `sam_batch.py` que roda sobre uma
> amostra do dataset **ainda não existe** (`roadmap.md` → Fase 3.0).
>
> Para calibrar, a varredura de limiar não passa mais por aqui: `sam_cache.py` roda o SAM uma vez
> com `conf` no piso e filtra offline (**D18**).

### Formato de saída

```
<class_id> <x1> <y1> ... <xN> <yN>
```

IDs gravados: `0=vein, 1=crack, 2=Stain, 3=Dark patches, 4=light spot, 5=scratch` — preservados
no arquivo, **colapsados para 0** antes do treino (**D2**).

> Sonda ausente do `CLASS_ID_MAP` costumava gravar `class_id = -1` em silêncio. Desde 2026-08-23,
> `validate_prompts()` aborta antes de carregar o modelo, nomeando a rocha e a sonda (**D8**).

### Gotcha obrigatório

`inference.py` e `calibrator.py` aplicam monkey-patch em `clip.simple_tokenizer.SimpleTokenizer`.
O Ultralytics chama o tokenizer como função, mas ele não tem `__call__`. **Sem o patch o modelo
falha silenciosamente** — sem exceção, sem saída. Não remover.

---

## Estágio 2 — Aluno: YOLO11-seg

- **Versão:** YOLO11-seg (**D10**).
- **Papel:** motor de inferência rápida para a linha de produção.
- **Entrada:** polígonos do Professor, `class_id = 0`.
- **Quantidade:** um modelo por litologia (especialista) × um modelo único (generalista) × um
  modelo único treinado com anotações calibradas (controle) — **D6**. Executado por faixas de
  volume de dados, não de uma vez.
- **Estado:** ❌ não iniciado. `AI/YOLO/` está vazio.

---

## Conexão entre os estágios

Xception identifica a litologia → seleciona a configuração de sondas em `rock_prompts.json`
(fase offline) e roteia para o Aluno especialista correspondente (fase online).

O desenho experimental que testa se essa hierarquia compensa está em **D5** (Experimento 1) e
**D6** (Experimento 2).

---

## Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.13 |
| Deep learning | PyTorch + CUDA |
| Classificador | Xception |
| Professor | SAM3 via Ultralytics |
| Embeddings de texto | OpenAI CLIP |
| Aluno | YOLO11-seg |
| Visualização | OpenCV |
| UI de calibração | Streamlit |

---

## Fora do escopo

Loop de aprendizado ativo (**D11**) e rotulagem multi-classe (**D12**) são trabalhos futuros.
