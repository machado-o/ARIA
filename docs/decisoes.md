# Decisões Fechadas — ARIA

> **Fonte única de verdade do projeto.** Toda decisão fechada mora aqui. Os demais documentos
> **linkam** para cá em vez de repetir o teor. Se uma decisão mudar, muda-se **aqui** e só aqui.
>
> ⚠️ **A numeração foi refeita em 2026-08-23.** Referências a "D1…D10" em textos antigos
> (`Overleaf/`, `LatinoWare2026/`, `apresentacao/`) apontam para a numeração velha e **não valem**.
>
> Última atualização: 2026-08-23

---

## D1 — Escopo: o TCC é o ARIA, e só

**Decisão:** O TCC desenvolve e valida o **ARIA** (Análise e Reconhecimento Inteligente de
Anomalias) — um pipeline de visão computacional para marcação automatizada de anomalias
superficiais em chapas de rochas ornamentais. O projeto é **isolado**: não há vínculo, menção ou
promessa de integração com nenhuma plataforma, produto ou empresa.

**Justificativa:** vincular o TCC a um produto do qual o autor é sócio (a) cria conflito de
interesse que consome tempo de arguição, (b) promete uma integração que não pode ser demonstrada
dentro do trabalho, e (c) obriga o leitor a carregar dois nomes o tempo todo sem ganho. A
motivação industrial se sustenta sozinha: o setor de rochas ornamentais do Espírito Santo, maior
polo produtor e exportador do país.

**Consequência:** `Hartheus.md` foi removido do repositório. Qualquer menção remanescente em
`Overleaf/`, `LatinoWare2026/` ou `apresentacao/` é texto desatualizado a corrigir (ver D13).

---

## D2 — Prompts são sondas de recall, não rótulos semânticos

**Decisão:** As palavras usadas como prompt (`crack`, `vein`, `Stain`, `Dark patches`,
`light spot`) **não são afirmações sobre a natureza do que foi encontrado**. São chaves lexicais
escolhidas por fazerem o CLIP+SAM3 responder a certas assinaturas visuais. O objetivo do conjunto
é **maximizar a cobertura de regiões anômalas**, não classificá-las.

**Consequência direta:** todas as regiões recebem `class_id = 0` no treinamento do Aluno. O
`inference.py` continua gravando IDs por sonda (**D8**) para não perder a informação de qual
sonda disparou, mas eles são **colapsados para 0** antes do treino.

**Justificativa:** afirmar que a região marcada por `"crack"` *é* uma fissura seria tratar como
verdade uma inferência não verificada. Como não há validação de que o modelo distingue fissura de
veio, o rótulo semântico é uma afirmação que o projeto não pode sustentar — o rótulo binário é a
única leitura honesta do que o pipeline produz.

**Na escrita:** apresentar como decisão deliberada e como consequência lógica do desenho, **não**
como limitação envergonhada ou omissão. Multi-classe → trabalho futuro (D12).

---

## D3 — O problema central é a arbitrariedade da marcação, não o falso positivo

**Decisão:** O problema que o TCC ataca é a **subjetividade e a arbitrariedade da marcação manual**
de anomalias.

A fronteira entre *feição natural* e *defeito comercial* é arbitrária: depende da rocha, do
cliente, do lote e — hoje — do inspetor. Esse critério vive implícito na cabeça de cada operador,
e por isso muda de pessoa para pessoa e de turno para turno. Não existe um "certo" absoluto a ser
descoberto.

**A contribuição do ARIA é tornar esse critério explícito e parametrizado:** um conjunto de
sondas e limiares por litologia, gravado em arquivo, que pode ser **auditado, discutido,
versionado e aplicado de forma idêntica mil vezes**. O trabalho não elimina a arbitrariedade —
ele a tira da cabeça do inspetor e a coloca num parâmetro inspecionável.

**Consequência:** "reduzir falsos positivos" deixa de ser o enunciado central. Falso positivo
continua sendo **medido** (D7), mas como consequência, não como tese.

**Na escrita:** este é o eixo da introdução e da conclusão. Substitui o argumento antigo de que o
ARIA existiria para "evitar que um veio natural vire defeito" — argumento que contradiz o próprio
código (a sonda `vein` está ativa em todas as configurações) e que fica **descartado**.

---

## D4 — Hipóteses

- **H1 (Experimento 1 — D5):** um critério de marcação **parametrizado por litologia** produz
  segmentações mais alinhadas ao julgamento de especialistas do que um critério **único e global**.
- **H2 (Experimento 2 — D6):** modelos Alunos **especialistas** (um por litologia) alinham-se
  melhor ao julgamento humano do que um único Aluno **generalista** — e esse ganho é **função do
  volume de dados** disponível por litologia.

A segunda metade de H2 é uma pergunta de pesquisa por direito próprio: *quantas imagens uma
litologia precisa para que a especialização compense?* (ver D6).

---

## D5 — Experimento 1: SAM calibrado × SAM default

**Decisão:** O primeiro experimento compara duas configurações do **Professor**, sem envolver
treinamento nenhum:

| Braço | Configuração de sondas |
|---|---|
| **Calibrado** | conjunto e limiares específicos do grupo litológico |
| **Default** | conjunto e limiares únicos para todas as rochas |

Mesma imagem, mesmo modelo, mesma máquina — muda só a configuração.

**Justificativa:** é o experimento mais barato do projeto (não exige treino) e testa a **premissa
de que todo o resto depende**. Hoje não existe nenhuma evidência no projeto de que calibrar muda
alguma coisa: as figuras mostram apenas o resultado já calibrado. Se calibrado ≈ default, é
melhor descobrir agora.

**Prioridade:** este experimento vem **antes** do Experimento 2. Ele fecha sozinho como
contribuição, e garante que existe resultado mensurável mesmo se o prazo apertar.

---

## D6 — Experimento 2: especialistas × generalista, estratificado por volume

**Decisão:** O segundo experimento compara Alunos YOLO11-seg treinados sobre as anotações do
Professor:

| Braço | Descrição |
|---|---|
| **Especialista** | um modelo por litologia, treinado só nas anotações daquela litologia |
| **Generalista** | um modelo único, treinado nas anotações de todas as litologias |
| **Controle** | um modelo único treinado com anotações **calibradas** — separa o efeito do nº de modelos do efeito da qualidade da anotação |

O braço de controle existe porque, sem ele, o desenho muda duas variáveis ao mesmo tempo
(quantidade de modelos **e** especificidade das anotações) e nenhum resultado seria atribuível.

**Estratificação por volume — o desenho executa por faixas, na ordem:**

| Faixa | Critério | Litologias |
|---|---|---|
| **A** | ≥ 1000 imagens | 11 |
| **B** | 500 – 999 | 6 |
| **C** | 200 – 499 | 14 |
| **D** | < 200 | 14 |

Os resultados são **reportados por faixa**, não agregados. Isso converte o desbalanceamento do
dataset de limitação em **variável do experimento** e responde à segunda metade de H2.

**Regra de execução (inegociável):** cada faixa é um **marco entregável**. A faixa A é executada,
avaliada e **escrita** antes de a faixa B começar. Em qualquer ponto de corte existe um resultado
completo e defensável; as faixas não alcançadas viram trabalho futuro declarado.

---

## D7 — De onde vem a referência de avaliação

**Decisão:** duas fontes de referência, complementares:

**1. Conjunto-ouro anotado às cegas (~50 imagens).**
O autor anota as imagens **antes** de rodar qualquer inferência sobre elas. A ordem importa: quem
anota depois de ver a máscara do modelo fica ancorado nela, e a anotação deixa de ser
independente. Esse conjunto é o gabarito quantitativo dos dois experimentos e não é usado em
treino.

**2. Preferência pareada cega, por especialista do setor.**
A mesma chapa é apresentada com a máscara do braço A e a do braço B, **embaralhadas e sem
identificação**. O especialista escolhe qual marcação representa melhor o que ele trataria como
defeito. Produz estatística de preferência (ex.: *"o especialista preferiu o calibrado em 43 de
50 pares"*), não IoU.

**Justificativa:** toda métrica quantitativa de segmentação — IoU, mAP, taxa de falso positivo —
exige uma referência. Usar a saída do próprio SAM como referência mede *fidelidade da cópia*, não
acerto, e torna a comparação entre braços sem sentido (cada braço teria um gabarito diferente).

**Definição operacional de falso positivo:** região marcada pelo modelo sem sobreposição
(IoU = 0) com qualquer região do conjunto-ouro.

---

## D8 — Escopo de sondas

**Decisão:** conjunto de trabalho desta versão:

| Sonda | id |
|---|---:|
| `vein` | 0 |
| `crack` | 1 |
| `Stain` | 2 |
| `Dark patches` | 3 |
| `light spot` | 4 |
| `scratch` | 5 |

Novas sondas podem ser adicionadas ao `rock_prompts.json` **desde que registradas no
`CLASS_ID_MAP`** de `inference.py` e `calibrator.py`. Como todos os IDs colapsam para 0 antes do
treino (**D2**), registrar uma sonda a mais não altera o resultado — só amplia a cobertura.

`vein` **permanece** no conjunto. Pela D2 ela é uma sonda de recall, não uma afirmação de que a
região é um veio mineral.

**Proteção:** sonda não registrada costumava gravar `class_id = -1` em silêncio, corrompendo o
`.txt` de treino. Desde 2026-08-23, `inference.py` valida toda a configuração **antes de carregar
o modelo** e aborta nomeando a rocha e a sonda; o `calibrator.py` mostra a máscara no preview mas
não grava polígonos de sonda não registrada.

---

## D9 — Dataset: público, não constituído pelo autor

**Decisão:** o conjunto de imagens é **público, obtido no Kaggle** — *Chapas polidas de rochas
ornamentais*, de `joovictorcostaaraujo`. O autor **não constituiu** o banco: selecionou,
caracterizou e pré-processou um conjunto existente.

<https://www.kaggle.com/datasets/joovictorcostaaraujo/chapas-polidas-de-rochas-ornametais>

**Consequência obrigatória na escrita:** o objetivo específico que hoje diz *"Constituir e
pré-processar um banco de imagens industriais"* é **factualmente falso** e precisa virar
*"Selecionar, caracterizar e pré-processar um conjunto de dados público"*, com citação da fonte.

**Benefício:** dataset público resolve de graça o statement de reprodutibilidade e elimina
qualquer necessidade de citar empresa ou parceiro.

- [ ] **TODO:** confirmar se o DeepStoneAI usou este mesmo conjunto (se sim, vira citação obrigatória).

---

## D10 — Versão do Aluno

**Decisão:** **YOLO11-seg** é a versão de referência do trabalho. YOLO12 e YOLO26 surgiram após o
período de estudo inicial — avaliação apenas **se houver tempo**, com YOLO11 como baseline de
versão. Não é bloqueador.

---

## D11 — Aprendizado Ativo: TRABALHO FUTURO

**Decisão:** o loop de aprendizado ativo (Professor refinando predições de baixa confiança do
Aluno em produção) é **trabalho futuro**. Nunca aparece como contribuição desta versão.

---

## D12 — Rotulagem multi-classe: TRABALHO FUTURO

**Decisão:** treinar o Aluno com `class_ids` distintos por sonda é extensão planejada, fora do
escopo. Exigiria validar que as sondas de fato identificam o que seus nomes sugerem — afirmação
que a D2 recusa fazer. Os IDs já são gravados, então a porta fica aberta sem reprocessar o
dataset.

---

## D13 — `Overleaf/`, `LatinoWare2026/` e `apresentacao/` não são fonte de verdade

**Decisão:** essas três pastas contêm **saída desatualizada**, escrita antes das decisões acima.
Enquanto não forem revisadas, **não** servem como referência para nada — nem para o Claude, nem
para o Henrique.

A verdade do projeto é `docs/`. A correção dessas pastas é uma tarefa posterior, listada em
`pendencias.md`, e acontece **depois** que `docs/` estiver estável.

**Divergências já conhecidas:** menções ao Hartheus (D1); "SAM" onde é SAM3; orientador
desatualizado; "45 especialistas" sem estratificação (D6); "constituir o banco de imagens" (D9);
o argumento do veio natural (D3).

---

## D14 — Nome

**Decisão:** **ARIA** — Análise e Reconhecimento Inteligente de Anomalias.

---

## D15 — A calibração atual é PROVISÓRIA

**Decisão:** o conteúdo atual do `rock_prompts.json` — 46 entradas, mas só **13 configurações
distintas**, com 18 litologias compartilhando o mesmo conjunto — é **provisório e incerto**. Não é
resultado de calibração validada e **não deve ser tratado como tal** por ninguém, em nenhum
documento.

O mesmo vale para as 14 imagens em `selectRocks/`: a compreensão do autor sobre marcações e sobre
rochas amadureceu desde que foram escolhidas, e **a seleção de imagem será refeita do zero**,
junto com a escolha de sondas de cada litologia.

**Ordem de trabalho:** a recalibração segue a **faixa de volume de dados** (**D6**) — faixa A
primeiro. O `rock_viewer.py` já ordena as litologias por volume decrescente e mostra a faixa e o
número de pendentes da faixa a cada iteração, para que a prioridade não dependa de disciplina.

**Ainda em aberto:** se a calibração deve ser individual por litologia ou por grupo cromático. A
decisão só será tomada depois que a faixa A estiver calibrada de fato, com base no que se
observar. **Até lá, nenhum texto deve afirmar qualquer uma das duas coisas.**

---

## D16 — TAM, Difusão de Inovações e Teoria Sociotécnica: FORA

**Decisão:** as teorias de adoção tecnológica (**TAM**, **Difusão de Inovações**, **Teoria
Sociotécnica**) **saem** do referencial teórico, da monografia e do artigo.

**Justificativa:** entraram apenas para atender ao escopo de uma submissão ao SBSI que não se
concretizou. Num trabalho de visão computacional elas diluem o foco e não sustentam nenhuma
afirmação do trabalho — não há capítulo de análise organizacional, nem coleta com usuários.

**Consequência:** remover a subseção "Automação e Sistemas de Informação no Setor de Rochas" da
monografia e a subseção "Adoção Tecnológica e Indústria 4.0" do artigo. O contexto de Indústria
4.0 pode ficar, em uma ou duas frases, como motivação — sem as três teorias.

---

## D17 — Protocolo de calibração: 1 imagem de descoberta + 3 de limiar

**O problema:** uma única imagem por litologia estava resolvendo **dois problemas diferentes** ao
mesmo tempo, e o ideal de imagem para cada um é oposto:

| Tarefa | Pergunta | A imagem precisa |
|---|---|---|
| **Descoberta de sonda** | a sonda faz o modelo responder a algo presente nesta litologia? | **conter** o máximo de fenômenos |
| **Escolha do limiar** | onde corto o score para marcar o que quero? | **representar** a variação típica |

As duas estratégias intuitivas são enviesadas em direções opostas. A chapa mais rica em anomalias
foi escolhida *porque* as feições eram visíveis — há efeito de seleção por visibilidade, e o
limiar sai **alto demais**, perdendo o defeito sutil das outras chapas. A chapa mais sutil produz
o inverso: limiar baixo demais, e enxurrada de marcações na chapa típica (provável origem dos
**107 polígonos** numa única imagem de `ice_leke`, 70 deles `vein`).

**Decisão — por litologia:**

- **1 imagem de descoberta** — a mais rica em anomalias. Define **quais sondas** entram.
- **3 imagens de limiar** — uma sutil, uma típica, uma forte. O limiar é escolhido para funcionar
  **no conjunto**, não perfeitamente em nenhuma. A pergunta deixa de ser "qual limiar acerta esta
  imagem" (que não tem resposta) e vira "qual limiar menos erra nas três" (que tem).

**Origem das imagens: somente `train/`.** O conjunto-ouro sai do `test/` (**D7**); calibrar sobre
uma imagem de `test/` seria ajustar o limiar em cima da própria prova. O `val/` fica reservado
para a validação do Aluno. O `rock_viewer.py` já restringe a seleção ao `train/`; a flag `--all`
mostra os outros splits apenas para estudo, sem permitir seleção.

Isso não custa cobertura: o split do dataset é **aleatório estratificado 70/15/15 em todas as 45
classes** (verificado), então `val/` e `test/` são amostras da mesma distribuição — não há
fenômeno que apareça sistematicamente só neles. E para a faixa A o `train/` tem de 700 a 3.200
imagens por litologia: o que limita a cobertura é a varredura do autor, não o split.

**Para que lado errar:** a literatura de pseudo-rotulagem tende a limiar **alto** / viés de
precisão — o *Soft Teacher* reporta melhor resultado em 0,9 de score, notando que limiar maior dá
mais precisão e menos recall, e a literatura de ruído de rótulo registra que redes de alta
capacidade **memorizam** rótulo errado. ⚠️ **Não copiar o número:** aquilo são scores calibrados
de um detector; os do SAM3 com prompt de texto operam entre 0,007 e 0,3. O que transfere é a
direção — **na dúvida, cortar mais apertado.**

**O critério tem de ser escrito.** Escolher limiar "no olho" é exatamente o que a **D3** acusa o
inspetor humano de fazer. A regra do projeto deve ser enunciável e reprodutível — algo como *"o
maior limiar que ainda marca ao menos X% das feições anotadas manualmente nas 3 imagens de
limiar"*. Enunciada assim, deixa de ser dúvida e vira parágrafo de metodologia.

- [ ] **TODO:** fixar o valor de X e a redação final da regra, depois da primeira litologia da
  faixa A calibrada com o protocolo novo.

---

## D18 — Calibração por varredura offline (cache de máscaras + scores)

**Decisão:** a calibração roda o SAM3 **uma vez por (imagem, sonda)** com `conf` no piso
(≈0,001), guarda as máscaras e seus scores, e depois varre qualquer limiar **offline**, sem GPU.

**Justificativa — verificada na fonte do `ultralytics 8.4.61`** (`SAM3SemanticPredictor.postprocess`):

```python
pred_scores = (pred_logits.sigmoid() * presence_score).squeeze(-1)
keep = pred_scores > self.args.conf          # filtro puro, depois do modelo
keep = torchvision.ops.nms(boxes, scores, self.args.iou)
```

O modelo produz máscaras e scores **sem conhecer o `conf`**; o `conf` apenas descarta. O NMS roda
depois do filtro, mas processa em ordem decrescente de score e só remove usando um sobrevivente de
score **maior** — então incluir máscaras de score baixo não pode derrubar uma de score alto. As
decisões sobre as máscaras acima de qualquer limiar são idênticas com ou sem as abaixo dele.

**Consequência: a varredura offline é exatamente equivalente a rodar de novo em cada limiar** —
não é aproximação. O ciclo de calibração deixa de ser "escolho conf → rodo o SAM → olho → ajusto →
rodo de novo" (minutos por iteração) e vira "rodo uma vez → arrasto o slider → vejo o efeito nas 4
imagens simultaneamente". É o que torna o protocolo da D17 viável em tempo humano.
