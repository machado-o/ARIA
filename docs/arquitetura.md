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
- **Estado:** o original (DeepStoneAI) não tem pesos salvos; o classificador foi **reproduzido**
  em PyTorch + `timm`, 480 × 480, no split oficial (**D19**), e treinado em 03/10/2026 (96,72%
  no `test/`). Código em `AI/Xception/` (treino, avaliação, `roteador.py` com litologia +
  confiança + top-3); falta ligar o roteador ao Estágio 2 (`roadmap.md` → Fase 4).
- **Substituição possível:** EfficientNetV2, ConvNeXt — só se sobrar tempo.

---

## Estágio 2 — Professor: SAM3

- **Modelo:** SAM3 (Segment Anything Model 3) via Ultralytics, modelo de fundação com capacidade
  zero-shot. O ARIA **não** se descreve como zero-shot: a calibração por litologia é uma adaptação
  ao domínio, e o texto do TCC diz isso (resposta ao parecer da LatinoWare).
- **Score:** é a probabilidade da detecção multiplicada por um escore de presença; não é uma
  probabilidade calibrada, e a escala precisa ser medida (fica na década baixa, 0,01 a 0,77).
- **Embeddings de texto:** OpenAI CLIP.
- **Papel:** gerar polígonos de anomalia sem anotação humana, processando o dataset **offline**.
- **Entrada:** imagem + conjunto de sondas de texto com limiar de confiança por litologia.
- **Saída:** polígonos em formato YOLO + visualizações.

### Sondas, não rótulos

As palavras usadas como prompt são **chaves lexicais de recall**, não classificações (**D2**).

| Sonda | Cor na visualização | Admitida em (das 11 da faixa A) |
|---|---|---:|
| `crack` | vermelho | 9 |
| `vein` | azul | 3 |
| `Stain` | laranja | 8 |
| `Dark patches` | magenta | 9 |
| `light spot` | amarelo | 6 |
| `scratch` | verde | 4 |
| `white stain` | ciano | 6 (registrada em 10/10/2026 — **D8**) |

> Quem decide se a sonda entra é a descoberta de cada litologia (**D17**), não a cor da rocha: a
> coluna antiga dizia "rochas claras" para `Dark patches` e "rochas escuras" para `light spot`, e
> as calibrações desmentiram as duas. Contagem dos `calibracao.json` em 22/11/2026.

> As cores valem as de `AI/SAM/sondas.py` (`CORES`), que é a fonte; esta coluna é só leitura
> rápida. Até 10/10/2026 ela ainda mostrava as cores de antes da unificação do cadastro.

**O que a calibração realmente faz:** para cada litologia, define *quais* sondas entram e *com que
limiar*. Esse limiar é a materialização do critério arbitrário que separa feição de defeito —
tirado da cabeça do inspetor e colocado num arquivo auditável (**D3**).

**Exemplo visual no lugar de palavra:** segundo o Henrique (25/11/2026), já se tentou guiar o SAM
por um exemplo visual, e pareceu marcar pior. Ainda sem registro de como foi (ver `pendencias.md`).

**Prompts contextuais — hipótese não testada:** o paper do CLIP mostra que o template
`"a photo of a [X]"` supera consistentemente `"X"` isolado em zero-shot. Para rochas,
`"crack on a stone surface"` poderia desambiguar melhor que `"crack"` (a palavra "vein" cobre
tanto veia sanguínea quanto veio mineral). Testável como sonda exploratória no calibrador — candidato a análise
de sensibilidade **se sobrar tempo**. O crédito do achado é do paper do CLIP, não deste trabalho.

### Configuração — `rock_prompts.json`

```json
{ "<litologia>": { "<sonda>": <limiar de confiança> } }
```

Quem escreve é só o calibrador, e só tem litologia calibrada: **quem não está no arquivo não foi
calibrado.** Não há fallback — a entrada `"default"` e os 45 valores provisórios de antes da
**D17** foram apagados em 09/10/2026 (**D15**; os valores antigos estão no histórico do git).

> O `inference.py` **não lê o limiar daqui**: lê do `selectRocks/<litologia>/calibracao.json`, que
> tem limiar **e** critério escrito. Este arquivo é o resumo, e serve ao `--provisorio`.

### Fluxo de `inference.py`

1. Lê imagens de `selectRocks/<litologia>/` (**4 por litologia** — D17).
2. Carrega as sondas e os limiares do `calibracao.json` da litologia. Litologia sem calibração, ou
   com calibração desatualizada (vaga trocada depois), é **recusada e listada** antes de o modelo
   carregar — a não ser com `--provisorio`, que aceita o `rock_prompts.json` e registra isso.
3. Grava `results/<litologia>/procedencia.json`: de onde veio cada limiar desta rodada.
4. Roda o SAM3 uma vez por sonda, com o limiar configurado.
5. Grava o resultado individual por sonda e a imagem combinada em `results/<litologia>/`.
6. Grava os polígonos em `.txt` (YOLO, coords normalizadas 0–1), uma linha por peça (**D21**).

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

IDs gravados: `0=vein, 1=crack, 2=Stain, 3=Dark patches, 4=light spot, 5=scratch, 6=white stain` — preservados
no arquivo, **colapsados para 0** antes do treino (**D2**).

> Sonda ausente do `CLASS_ID_MAP` costumava gravar `class_id = -1` em silêncio. Desde 2026-08-23,
> a validação aborta antes de carregar o modelo, nomeando a rocha e a sonda (**D8**). O cadastro
> mora em `AI/SAM/sondas.py`, um lugar só, compartilhado pelo `inference.py` e pelo
> `calibrator.py` (09/10/2026).

### Gotcha obrigatório

`inference.py` e `calibrator.py` aplicam monkey-patch em `clip.simple_tokenizer.SimpleTokenizer`.
O Ultralytics chama o tokenizer como função, mas ele não tem `__call__`. **Sem o patch o modelo
falha silenciosamente** — sem exceção, sem saída. Não remover.

---

## Estágio 2 — Aluno: YOLO11-seg

> ⏸️ **Trabalho futuro desde 23/11/2026 (D6).** O Aluno faz parte da arquitetura descrita no TCC,
> mas não foi treinado nesta versão. O que segue é o desenho previsto.

- **Versão:** YOLO11-seg (**D10**).
- **Papel:** inferência rápida na linha de produção.
- **Entrada:** polígonos do Professor, todos com `class_id = 0` (**D2**).
- **Desenho previsto (D6):** um modelo por litologia (especialista), um modelo único (generalista)
  e um modelo único treinado com as anotações calibradas (controle), executados por faixa de volume.
- **Estado:** `AI/YOLO/` está vazio.

---

## Conexão entre os estágios

Xception identifica a litologia → seleciona a configuração de sondas e limiares calibrada para
ela (`calibracao.json`, fase offline) e roteia para o Aluno especialista correspondente (fase
online).

O experimento desta versão (**D5**) testa só o Estágio 2 do Professor: se o critério por litologia
marca melhor que um critério único. Se a especialização dos Alunos compensa é a pergunta do
trabalho futuro (**D6**).

---

## Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3 |
| Deep learning | PyTorch + CUDA |
| Classificador | Xception |
| Professor | SAM3 via Ultralytics |
| Embeddings de texto | OpenAI CLIP |
| Aluno | YOLO11-seg |
| Visualização | OpenCV |
| UI de calibração | Streamlit |

> As versões são **por máquina** (o autor alterna entre dois PCs) e por isso não ficam escritas
> aqui — este parágrafo já esteve errado por isso. Rode `AI/ambiente.py` para ver as da máquina em
> que estiver, e o estado da verificação da **D18** nela.

---

## Fora do escopo

Loop de aprendizado ativo (**D11**) e rotulagem multi-classe (**D12**) são trabalhos futuros.
