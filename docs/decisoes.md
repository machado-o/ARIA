# Decisões Metodológicas Fechadas — ARIA

> **Fonte única de verdade.** Toda decisão metodológica fechada do TCC mora aqui.
> Os demais documentos (`arquitetura.md`, `dataset.md`, `pontos_tcc.md`) **linkam** para
> esta página em vez de repetir o teor. Se uma decisão mudar, muda-se **aqui** e só aqui.
>
> Última atualização: 2026-06-10

---

## D1 — Identidade: ARIA × Hartheus

**Decisão:** O TCC desenvolve e valida o **ARIA** (Análise e Reconhecimento Inteligente de
Anomalias) — o *pipeline/método* hierárquico de IA. **Hartheus** é a *plataforma web*
(produto da fábrica: frontend de anotação, backend, banco, AI Service) na qual o ARIA se
destina a ser o núcleo inteligente.

- **Protagonista do texto:** ARIA (o método proposto e validado).
- **Papel do Hartheus:** contexto aplicado, estabelecido em um parágrafo na introdução —
  ARIA é a contribuição de IA destinada a alimentar o AI Service do Hartheus.
- ARIA é uma das abordagens de IA pesquisadas dentro do Hartheus (ver `../Hartheus.md`).

**Justificativa:** sendo um TCC de Sistemas de Informação, nomear a plataforma situa a
contribuição num produto real e demonstra visão sistêmica, sem desviar o foco do método.

---

## D2 — Rotulagem: binária (`class_id = 0`)

**Decisão:** Todas as anomalias recebem `class_id = 0` no treinamento YOLO. O `inference.py`
continua gerando IDs por prompt (`vein=0, crack=1, Stain=2, Dark patches=3, light spot=4`),
mas eles são **colapsados para 0** antes do treino.

**Justificativa:** labels multi-classe são tão confiáveis quanto os embeddings CLIP no
domínio de rochas — qualidade **não validada**. Tratar IDs distintos como *ground truth*
assumiria que o SAM distingue fissura de veio corretamente, o que é afirmação não verificada.
Gerar e preservar os IDs originais mantém a porta aberta para multi-classe sem reprocessar
o dataset.

**Na escrita:** apresentar como decisão deliberada (não omissão). Multi-classe → Trabalhos
Futuros (ver D9).

---

## D3 — Experimento central: 45 especialistas × 1 generalista

**Decisão:** O coração do TCC é a comparação entre:

| Pipeline | Xception | SAM | YOLO |
|---|---|---|---|
| **ARIA (especialista)** | identifica tipo → seleciona prompts calibrados → roteia | segmenta com prompts específicos por rocha | **45 modelos** — um por litótipo, treinado só nas anotações do seu tipo |
| **Baseline (generalista)** | ausente | segmenta com config genérica (`default`) para todas | **1 modelo** — treinado em anotações de todas as rochas |

Mesma arquitetura **YOLO11-seg** nos dois casos. O que muda é a **quantidade de modelos
(1 vs. 45)** e a **especificidade das anotações**. O experimento isola exatamente o ganho da
hierarquia especialista.

**Hipótese de benefício:** anotações calibradas por litologia capturam anomalias reais com
menos ruído (veios naturais não viram defeito) → o YOLO herda essa especificidade.

---

## D4 — Integração dos estágios

**Decisão:** O Xception identifica o tipo litológico e **roteia** a imagem para o modelo YOLO
especialista correspondente, selecionando os prompts calibrados em `rock_prompts.json` para a
geração de anotações. Um modelo YOLO por tipo de rocha (45 no total).

---

## D5 — Ground truth: avaliação qualitativa por especialistas

**Decisão:** Amostras dos resultados SAM de cada tipo litológico são submetidas a
**especialistas do setor de rochas ornamentais**. A validação é **qualitativa** — os
especialistas avaliam se as segmentações fazem sentido técnico/industrial. **Não há** anotação
humana paralela pixel-a-pixel.

**Na escrita:** mAP e IoU são sensíveis à qualidade da anotação, e o *ground truth* é gerado
pelo próprio SAM. A comparação quantitativa Teacher×Student é válida, mas deve ser
contextualizada; a validação qualitativa a complementa. A subjetividade da anotação é parte
da discussão metodológica — não um problema a esconder.

---

## D6 — Escopo de anomalias

**Decisão:** Conjunto de trabalho desta versão: `crack`, `vein`, `Stain`, `Dark patches`,
`light spot`. As anomalias **não são rotuladas** no treino (decorrência de D2). Novos tipos
podem ser adicionados ao `rock_prompts.json` futuramente sem quebrar o pipeline.

---

## D7 — Versão do YOLO

**Decisão:** Versão estudada e referência do TCC: **YOLO11 (YOLOv11-seg)**. YOLO12 e YOLO26
surgiram após o período de estudo inicial — candidatos a avaliação **se houver tempo**, com o
YOLO11 como baseline de versão. Não é bloqueador para iniciar o treinamento.

---

## D8 — Aprendizado Ativo (Active Learning): TRABALHO FUTURO

**Decisão:** O loop de aprendizado ativo (SAM refinando predições de baixa confiança do YOLO
em produção) é **trabalho futuro**. **Nunca** aparece como contribuição desta versão — apenas
na seção de Trabalhos Futuros.

> ⚠️ Regra inegociável. O `.tex` antigo descrevia o AL como parte central do sistema — isso
> está sendo corrigido (ver `PENDENCIAS.md`).

---

## D9 — Rotulagem multi-classe: TRABALHO FUTURO

**Decisão:** Treinar o YOLO com `class_ids` distintos por tipo de anomalia é **extensão
planejada**, fora do escopo desta entrega. Requer validação humana de uma amostra das
anotações SAM ou tratamento explícito como pseudorrótulos. Mencionada só em Trabalhos Futuros.

---

## D10 — Nome do projeto

**Decisão:** **ARIA** — Análise e Reconhecimento Inteligente de Anomalias. Definido.
