# Decisões Fechadas — ARIA

> **Fonte única de verdade do projeto.** Toda decisão fechada mora aqui. Os demais documentos
> **linkam** para cá em vez de repetir o teor. Se uma decisão mudar, muda-se **aqui** e só aqui.
>
> ⚠️ **A numeração foi refeita em 2026-08-23.** Referências a "D1…D10" em textos antigos
> (dentro de `apresentações/`) apontam para a numeração velha e **não valem**.
>
> Última atualização: 2026-11-25
>
> **Como ler.** Cada decisão guarda o texto original e as emendas datadas, e nada é apagado: o
> registro de *quando* cada coisa foi decidida é o que mostra que o desenho não foi ajustado depois
> de ver resultado. Para saber só o que vale hoje, use o resumo abaixo.

## Resumo: o que vale hoje

| | Decisão | O que vale hoje |
|---|---|---|
| D1 | Escopo | O TCC é o ARIA, isolado de qualquer empresa ou produto |
| D2 | Sondas | As palavras são instrumentos de busca, não rótulos; rótulo único (`class_id = 0`) |
| D3 | Problema | A arbitrariedade não escrita do critério de marcação, não o falso positivo |
| D4 | Hipótese | **Só a H1** (a H2 saiu em 23/11). Decidida por dominância, com a precisão desempatando (emenda de 25/11) |
| D5 | Experimento | Quatro braços do Professor (`unico`, `regra_todas`, `regra_autor`, `autor`); o teste da H1 é `unico` × `regra_todas` |
| D6 | Experimento 2 | **Trabalho futuro** desde 23/11, com a H2 |
| D7 | Referência | Auditoria cega (emenda de 19/11): avaliadora externa como referência, o autor julga à parte, kappa entre os dois |
| D8 | Cadastro de sondas | 7 sondas em `AI/SAM/sondas.py`; sonda nova entra no fim |
| D9 | Dataset | Público, do Kaggle; uma pasta renomeada (`white_liberdade`) |
| D10 | Aluno | YOLO11-seg (no trabalho futuro) |
| D11 | Aprendizado ativo | Trabalho futuro |
| D12 | Multiclasse | Trabalho futuro |
| D13 | `apresentações/` | Não é fonte de verdade (a monografia foi realinhada; os artigos, não) |
| D14 | Nome | ARIA |
| D15 | Calibração antiga | Apagada; quem não está no `rock_prompts.json` não foi calibrado; calibração por litologia |
| D16 | Teorias de adoção | Fora do texto |
| D17 | Protocolo | 1 imagem de descoberta + 3 de limiar, só do `train/`; regra do joelho em escala log; critério escrito |
| D18 | Varredura | SAM uma vez no piso, limiar filtrado sem GPU; equivalência exata, verificada por versão |
| D19 | Classificador | Reprodução do Xception; reportar 96,72% (`test/` oficial) e 99,92% (sorteio por imagem) |
| D20 | Movimentadas | Calibradas como as demais; termo "movimentada"; recorte à parte nos resultados |
| D21 | Contornos | Cada contorno solto é um polígono; a unidade da regra continua sendo a detecção |

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
`apresentações/` é texto desatualizado a corrigir (ver D13).

---

## D2 — Prompts são sondas de recall, não rótulos semânticos

**Decisão:** As palavras usadas como prompt (as da **D8**: `vein`, `crack`, `Stain`,
`Dark patches`, `light spot`, `scratch`, `white stain`) **não são afirmações sobre a natureza do que foi
encontrado**. São chaves lexicais
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

> **Vigente:** a H1, na redação de 19/11/2026 (a última nota do item abaixo), decidida pela regra
> da emenda de 25/11/2026 (fim desta seção). A H2 saiu do escopo em 23/11/2026.

- **H1 (Experimento 1 — D5):** um critério de marcação **parametrizado por litologia** produz
  segmentações mais alinhadas ao **critério de referência anotado** (**D7**) do que um critério
  **único e global**.

  > ⚠️ **Corrigido em 2026-09-26.** A redação anterior dizia "ao julgamento de especialistas",
  > mas o gabarito quantitativo é anotado pelo **autor** (D7, fonte 1) — não por um especialista
  > do setor. O especialista entra só na **preferência pareada cega** (D7, fonte 2), que produz
  > estatística de preferência e não IoU, e cuja realização ainda depende de um contato em
  > aberto. Prometer "especialista" na hipótese e medir com o gabarito do autor era um flanco
  > gratuito: a hipótese passa a enunciar exatamente o que é medido. Se o especialista aparecer,
  > ele **reforça** o resultado; ele não é mais requisito para a H1 existir.
  > **Reescrita em 2026-11-19**, com a auditoria cega (emenda da **D7**): um critério de
  > marcação **parametrizado por litologia** produz marcações mais alinhadas ao **julgamento
  > humano**, medido em auditoria cega (precisão e recall relativo), do que um critério **único e
  > global**.
- **H2 (Experimento 2 — D6):** modelos Alunos **especialistas** (um por litologia) alinham-se
  melhor ao julgamento humano do que um único Aluno **generalista** — e esse ganho é **função do
  volume de dados** disponível por litologia.

A segunda metade de H2 é uma pergunta de pesquisa por direito próprio: *quantas imagens uma
litologia precisa para que a especialização compense?* (ver D6).

> **A H2 saiu do escopo em 23/11/2026**, com o Experimento 2 inteiro (**D6**). O TCC tem uma
> hipótese só, a H1.

> **Emenda de 25/11/2026 (Henrique): como a H1 é decidida.** Registrada **antes** de qualquer
> julgamento da auditoria: o pacote ainda não tinha sido enviado à avaliadora, e o autor ainda
> não tinha julgado. Até aqui o texto dizia que a H1 é medida por precisão e recall relativo, mas
> não dizia o que fazer se as duas medidas apontassem para lados opostos, e esse é o caso mais
> provável (o braço único marca 11.964 regiões contra 7.289 do `regra_todas`).
>
> - **A comparação da H1 é `unico` × `regra_todas`** (**D5**). A referência é o julgamento da
>   avaliadora (**D7**); o do autor entra como concordância e é reportado à parte.
> - **Dominância:** um braço vence se for **melhor** numa medida (IC 95% da diferença todo acima
>   de zero) e **não pior** na outra (IC 95% da diferença não fica todo abaixo de zero).
> - **Se houver troca** (cada braço melhor numa medida), **a precisão desempata**: a H1 é
>   confirmada se o `regra_todas` tiver precisão maior, e refutada se for o `unico`. A troca é
>   reportada em números, nos dois sentidos.
> - **Sem diferença em nenhuma das duas:** a H1 não é confirmada nesta amostra, e o texto reporta
>   o IC, que diz o tamanho máximo do efeito compatível com os dados.
> - **Por que a precisão desempata:** as marcações do Professor são rótulo de treino, e rótulo
>   errado é aprendido pela rede (`sec:ruidosos`); e os defeitos são raros, porque a maioria das
>   chapas chega quase limpa ao fim do beneficiamento (observação do Henrique), e com defeito raro
>   quem marca muito erra quase sempre.
> - **As outras duas comparações são aninhadas.** Como o autor ficou acima da regra nos 45 pares,
>   `autor` ⊂ `regra_autor` ⊂ `regra_todas`: o recall relativo cai de um para o outro **por
>   construção**. Nelas se reporta quanta precisão se ganha por ponto de recall perdido, e não
>   cada medida sozinha.
> - **Análises secundárias, declaradas agora como exploratórias** (não decidem a H1): o score do
>   SAM3 prevê o "sim"?; a ordem dos braços é a mesma para os dois avaliadores?; o kappa e a taxa
>   de "não sei" são piores nas movimentadas?; as discordâncias se concentram entre o limiar da
>   regra e o do autor?; precisão por sonda; precisão de uma família de limiares entre o da regra
>   e o do autor; precisão do braço `autor` julgada pelo autor × pela avaliadora. Detalhes em
>   `reflexao.md`.

---

## D5 — Experimento 1: SAM calibrado × SAM default

**Decisão:** O primeiro experimento compara duas configurações do **Professor**, sem envolver
treinamento nenhum:

| Braço | Configuração de sondas |
|---|---|
| **Calibrado** | conjunto e limiares específicos do grupo litológico |
| **Default** | conjunto e limiares únicos para todas as rochas |

Mesma imagem, mesmo modelo, mesma máquina — muda só a configuração.

**Como o braço `default` é definido — regra fixada em 2026-09-26, antes de qualquer resultado:**

O braço default **não é escolhido a dedo**. Ele aplica **a mesma regra de limiar** do braço
calibrado (**D17**), mudando **uma única coisa**: o escopo dos dados sobre os quais a regra roda.

| Braço | Escopo da curva que produz o limiar |
|---|---|
| **Calibrado** | as 3 vagas de limiar **daquela litologia** |
| **Default** | as 3 vagas de limiar de **todas as litologias reunidas** |

Sonda por sonda: reúnem-se os scores de todas as litologias num só conjunto, aplica-se a regra e
obtém-se **um limiar global por sonda**. O conjunto de sondas do braço default é o que a mesma
regra de descoberta admite sobre o material reunido.

> **Precisado em 2026-10-05:** "o que a descoberta admite sobre o material reunido" é a **união**
> das sondas admitidas em pelo menos uma litologia calibrada. A descoberta é julgamento do autor
> por litologia, não uma fórmula, então não há como "rodá-la" sobre as 45 juntas; a união é a
> leitura mecânica e sem parâmetro livre. Na prática deve coincidir com todas as sondas do
> `CLASS_ID_MAP` (**D8**), inclusive as que forem registradas durante a calibração — uma sonda
> só fica de fora se não for admitida em nenhuma litologia.

**Terceiro braço — acrescentado em 2026-10-05: o calibrado pelo autor.**

| Braço | Limiar | Comparação que ele permite |
|---|---|---|
| **Default** | joelho sobre todas as litologias reunidas | — |
| **Calibrado pela regra** | joelho daquela litologia (limiar da regra, **D17**) | × default: efeito do **escopo** — ⚠️ não é uma variável só, ver o quarto braço abaixo |
| **Calibrado pelo autor** | limiar de trabalho daquela litologia (**D17**) | × calibrado pela regra: efeito do **ajuste humano** |

Por quê: na `siena_white` o autor divergiu da regra nas três sondas, sempre para cima e por
cerca do dobro. O limiar de trabalho é o que vai para o `rock_prompts.json` e rotula o conjunto
do Aluno — deixá-lo fora do experimento mediria uma configuração que o sistema não usa. Com três
braços, o conhecimento de domínio aparece decomposto: quanto vem de tratar cada litologia à
parte, e quanto vem do olho de quem calibra. Custo: uma inferência a mais por imagem avaliada
(desde 19/11, as chapas da auditoria cega — **D7**), nenhuma anotação adicional.

O que **não** muda: o default continua saindo da regra sobre o material reunido, nunca de média
(simples ou ponderada) dos limiares de trabalho — vale o parágrafo abaixo. E *default × calibrado
pelo autor* muda duas coisas ao mesmo tempo (escopo e quem escolhe): pode ser mostrado, mas não
é a evidência da H1.

**Quarto braço — acrescentado em 2026-10-10, antes de qualquer resultado do experimento: a regra
com todas as sondas.**

A tabela acima diz que *calibrado pela regra × default* muda "uma variável só". **Estava
errado:** mudam duas. O default usa a união das sondas (na prática, todas); o calibrado pela
regra usa só as que o autor admitiu na descoberta daquela litologia. Um ganho de recall do
default não seria atribuível — pode vir do limiar ou de ter mais sondas.

Quem levantou foi o autor, revisando a `siena_white`: a litologia parece ter tipos de defeito
diferentes em partes diferentes do bloco, ou seja, em chapas distantes. As sondas do calibrado
saem de **uma** chapa de descoberta (**D17**); um defeito que só aparece em outra parte do bloco
fica sem sonda, e o default, que tem todas, o pegaria.

A separação é possível porque o joelho não depende da descoberta: ele sai das 3 vagas de limiar
para qualquer sonda. Os braços passam a ser quatro, cada um diferindo do anterior em **uma**
coisa:

| Braço | Sondas | Limiar | Comparado ao anterior, mede |
|---|---|---|---|
| **Default** | todas | joelho sobre todas as litologias reunidas | — |
| **Regra, todas as sondas** | todas | joelho daquela litologia | o **escopo** do limiar — o teste limpo da **H1** |
| **Regra, sondas do autor** | as admitidas na descoberta | joelho daquela litologia | a **seleção de sondas**: o recall que ela custa e a precisão que compra |
| **Calibrado pelo autor** | as admitidas na descoberta | limiar de trabalho | o **ajuste humano** do limiar |

"Regra, sondas do autor" é o braço que até aqui se chamava "calibrado pela regra". "Todas" é o
cadastro de `sondas.py` (**D8**), igual nos dois primeiros braços.

Custo: nenhuma anotação a mais. Pela **D18**, o SAM roda uma vez com todas as sondas em cada
imagem avaliada e os quatro braços são filtros do mesmo cache — é isso que permite à auditoria
cega (**D7**, emenda de 19/11) julgar cada detecção uma vez só para todos os braços. Nos scripts
os braços se chamam `unico`, `regra_todas`, `regra_autor` e `autor`.

**Figuras de exemplo (decisão do autor, 10/10/2026):** a figura "critério único × calibrado" usa,
no lado calibrado, o **limiar de trabalho** (braço calibrado pelo autor), a não ser que o joelho
da regra dê figura melhor. A legenda diz qual dos dois foi usado — a figura ilustra, não é a
evidência da H1.

**O que o braço novo não resolve:** se uma imagem de descoberta basta para escolher as sondas de
uma litologia. Ele mede o tamanho do problema. Se a seleção custar recall demais, a saída é
admitir todas as sondas e calibrar só o limiar — o que muda a **D17** e é decisão a tomar com o
número na mão, não antes.

**Por que assim, e não pela mediana dos limiares calibrados:** se o default fosse a mediana das
configurações calibradas, o resultado seria quase aritmético — o ótimo de cada litologia vence a
mediana dos ótimos **nos dados dela** por construção. Isso é regressão à média, não achado, e o
controle passaria a ser função do tratamento. A regra sobre o material reunido é o contrafactual
honesto — *"e se tivéssemos tratado as 45 rochas como uma só?"*, que é o que a H1 pergunta — e
**pode dar negativo**, o que é justamente o que torna a hipótese falseável.

> ⚠️ **Consequência inegociável:** os dois braços têm de usar a **mesma regra mecânica**. Se o
> calibrado fosse escolhido no olho e o default por fórmula, a comparação mudaria duas coisas ao
> mesmo tempo — o escopo **e** quem escolhe — e nenhum resultado seria atribuível. É isto que
> obriga a regra da D17 a ser mecânica.

> ⚠️ **Havia um `"default"` no `rock_prompts.json`** (`crack 0,1 · vein 0,007 · Stain 0,3`) que
> **não servia** para este braço: foi escolhido no olho e a própria **D15** o declarava
> provisório. Medido na `siena_white`, o joelho da curva sugere `vein ≈ 0,145` contra os `0,007`
> do arquivo — vinte vezes de diferença. Usá-lo seria montar um espantalho e perder o experimento
> na arguição. **A entrada foi apagada em 09/10/2026** (**D15**), justamente para que ninguém a
> pegue por engano; o braço default se constrói rodando a regra sobre o material reunido, como
> descrito acima.

**Justificativa:** é o experimento mais barato do projeto (não exige treino) e testa a **premissa
de que todo o resto depende**. Hoje não existe nenhuma evidência no projeto de que calibrar muda
alguma coisa: as figuras mostram apenas o resultado já calibrado. Se calibrado ≈ default, é
melhor descobrir agora.

**Prioridade:** este experimento vem **antes** do Experimento 2. Ele fecha sozinho como
contribuição, e garante que existe resultado mensurável mesmo se o prazo apertar.
(Foi o que aconteceu: desde 23/11/2026 ele é o único experimento do TCC, **D6**.)

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

> **Decidido em 22/11/2026 (Henrique): até a entrega de 01/12, tentar o Experimento 2 só na faixa
> A.** As faixas B, C e D viram trabalho futuro. Consequência para a **H2**: com uma faixa só, a
> primeira metade (especialista × generalista) pode ser respondida na faixa A, mas a segunda — o
> ganho como **função do volume** — precisa de mais de uma faixa e passa a trabalho futuro. Se o
> treino da faixa A não couber no prazo, o Experimento 2 inteiro vira trabalho futuro. Ainda
> faltam, antes de treinar: o `sam_batch.py`, a regra de split do Aluno e contra o quê ele é
> avaliado (ver `pendencias.md`).

> **Fechado em 23/11/2026 (Henrique): o Experimento 2 inteiro vira trabalho futuro, e a H2 com
> ele.** O TCC mede só o Experimento 1 (os quatro braços do Professor). Motivo: sem referência de
> verdade para o Aluno, medi-lo contra os rótulos do próprio SAM mostraria só que ele imita o
> Professor, o que não responde à H2. E o custo (`sam_batch.py`, pós-processamento, SAM sobre
> milhares de chapas, ~13 treinos) competia com o que fecha o trabalho: a auditoria e o texto. O
> YOLO continua na arquitetura descrita; a destilação e a H2 entram como trabalho futuro, como
> **escopo**, não como falha (diretrizes 2.5). Opcional, só se sobrar tempo: um YOLO generalista
> como **demonstração** de que o pipeline fecha (figuras SAM × YOLO e FPS), sem hipótese.

---

## D7 — De onde vem a referência de avaliação

> ⚠️ **Vigente para o Experimento 1: a emenda de 19/11/2026, no fim desta seção** (auditoria
> cega). O texto abaixo é a decisão original, mantida como histórico.

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

> ⚠️ **O que "às cegas" garante, e o que não garante.** Garante que o autor anotou **antes de
> rodar a inferência nestas imagens**, então a anotação não é cópia da máscara. **Não** garante
> ingenuidade: o autor passou meses calibrando sondas e olhando saída do SAM, e isso molda a
> noção do que ele considera anomalia. A independência é **parcial** e deve aparecer no texto
> como limitação declarada — não como garantia de imparcialidade.

**Justificativa:** toda métrica quantitativa de segmentação — IoU, mAP, taxa de falso positivo —
exige uma referência. Usar a saída do próprio SAM como referência mede *fidelidade da cópia*, não
acerto, e torna a comparação entre braços sem sentido (cada braço teria um gabarito diferente).

**Definição operacional de falso positivo:** região marcada pelo modelo sem sobreposição
(IoU = 0) com qualquer região do conjunto-ouro.

> **Emenda de 06/11/2026 (Henrique): o conjunto-ouro passa a ser condicional.** Ele só é feito
> se houver tempo, disposição ou ajuda para anotar; senão, a avaliação fica só na análise
> qualitativa (item 2, provavelmente com alguém da faculdade de Minas), e a falta de métrica
> quantitativa entra no texto como limitação declarada. Enquanto isso, treinos e escrita seguem
> sem esperar por ele. **O que não muda:** o conjunto-ouro, se vier, sai do `test/`. Os treinos
> usam só `train/` e `val/`, e nada roda sobre o `test/` antes da anotação. Assim a opção de
> fazê-lo continua aberta.

> **Emenda de 19/11/2026 (Henrique): o Experimento 1 é avaliado por auditoria cega, no lugar do
> conjunto-ouro.** Ninguém desenha polígono. Um programa mostra uma marcação por vez, sorteada,
> sem dizer de que braço veio, e o avaliador responde *sim / não / não sei* à pergunta "você
> marcaria esta região como defeito?". Como os quatro braços da **D5** são filtros do mesmo cache
> (**D18**), um julgamento por detecção serve a todos os braços que a contêm.
>
> - **Avaliadores:** uma estudante de Engenharia de Minas, sem contato com a calibração, é a
>   referência da H1. O autor julga **a mesma amostra, separadamente** (cada um na sua tela, sem
>   ver nem discutir a resposta do outro), e a concordância entre os dois (kappa de Cohen) mede a
>   arbitrariedade que a **D3** afirma.
> - **O que mede:** a **precisão** de cada braço e o **recall relativo** ao conjunto das
>   marcações de todos os braços (o *pooling* usado em avaliação de recuperação de informação). O
>   que nenhum braço marcou fica fora do denominador de todos, então a comparação entre braços é
>   justa. **Não mede** o recall absoluto nem a qualidade da borda (IoU).
> - **Falso positivo** passa a ser a marcação julgada "não". A definição por IoU = 0 só valia com
>   o conjunto-ouro.
> - **Amostra:** 3 chapas do `test/` por litologia calibrada, sorteadas com semente fixa. As
>   detecções são sorteadas por estrato (o padrão de pertencimento aos braços), com pesos na
>   análise, e a ordem é intercalada para que qualquer começo da lista seja amostra válida: a
>   avaliadora pode parar onde quiser.
> - **Por que assim:** o conjunto-ouro não tinha prazo para sair (anotar polígono de trinca fina
>   à mão é lento), e a auditoria responde a pergunta que a calibração deixou aberta, regra × autor,
>   em uma ou duas horas de cliques.
> - **Alternativas consideradas e descartadas** (levantadas em 05/10/2026): preferência pareada
>   cega (diz "A melhor que B", sem número absoluto); rótulo fraco por chapa ou por célula de uma
>   grade (mede detecção, não a máscara); anomalia sintética inserida em chapa limpa (gabarito
>   exato, realismo duvidoso); consistência sob espelhamento e rotação (mede robustez, não acerto);
>   corrigir a máscara do modelo em vez de anotar do zero (a anotação ficaria ancorada no modelo).
>   O rótulo fraco por chapa ("há defeito não marcado aqui?") é o único caminho barato para o
>   recall absoluto e fica como extensão futura.

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
| `white stain` | 6 |

`white stain` entrou em 10/10/2026, a pedido do Henrique, depois de testada como sonda
exploratória na `san_francisco_green`: marcou regiões que nenhuma das sondas anteriores marcava,
e que podem existir em outras litologias. Nas litologias calibradas antes dessa data ela não foi
avaliada — aparece no calibrador como candidata desmarcada.

Novas sondas podem ser adicionadas ao `rock_prompts.json` **desde que registradas no
`CLASS_ID_MAP`**, que desde 09/10/2026 mora num lugar só: `AI/SAM/sondas.py`. Antes ele era
duplicado em `inference.py` e `calibrator.py`, com um comentário pedindo que as duas cópias
fossem mantidas iguais à mão — e a tabela de **cores** que acompanhava cada cópia já havia
divergido (`Dark patches` saía preto puro no resultado final e magenta no calibrador). Como todos
os IDs colapsam para 0 antes do treino (**D2**), registrar uma sonda a mais não altera o
resultado — só amplia a cobertura.

> O id é posicional e vai para o `.txt`: sonda nova entra **no fim**. Renumerar uma sonda já
> usada faria os `.txt` já gravados passarem a dizer outra coisa, sem erro nenhum.

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

**Uma pasta foi renomeada: `whte_liberdade` → `white_liberdade`** (09/10/2026, decisão do autor).
O typo é do dataset original do Kaggle. É a **única** alteração feita no `AI/dataset/`, que fora
isso continua somente-leitura, e precisa ser **refeita em toda máquina** — porque o índice de
classe é a posição no nome ordenado, e `whte` cai depois de todos os `white_*`. Com o typo, sete
classes (índices 37 a 43) ficavam em posições diferentes das do treino já salvo em
`runs/xception_480/`, e nada avisava: dois treinos comparáveis por número passariam a falar de
rochas diferentes. Conferido depois do rename: as 45 classes do disco batem exatamente com as do
run salvo. Mencionar o rename no statement de reprodutibilidade, já que o dataset público tem a
grafia antiga.

- [x] ~~TODO: confirmar se o DeepStoneAI usou este mesmo conjunto~~ — **confirmado em
  2026-10-02.** O artigo do SBAI 2025 descreve as mesmas 34.630 imagens em 45 classes e cita este
  dataset (`chapas_polidas_rochas_2023`, Araujo, Kaggle). **Citar o DeepStoneAI é obrigatório.**
  Ressalva: o DeepStoneAI fundiu `train/test/valid` e fez um split próprio, então o número dele
  (Xception 99,21%) não é comparável ao teste do ARIA — ver `roadmap.md` → Fase 4.

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

## D13 — `apresentações/` não é fonte de verdade

**Decisão:** a pasta `apresentações/` (que reúne `Overleaf/TCC`, `Overleaf/artigo de PD1`,
`Overleaf/artigo LatinoWare2026` e `apresentacao de PD1`) contém **saída desatualizada**, escrita
antes das decisões acima. Enquanto não for revisada, **não** serve como referência para nada —
nem para o Claude, nem para o Henrique.

A verdade do projeto é `docs/`. A correção dessa pasta é uma tarefa posterior, listada em
`pendencias.md`, e acontece **depois** que `docs/` estiver estável.

**Divergências já conhecidas:** menções ao Hartheus (D1); "SAM" onde é SAM3; orientador
desatualizado; "45 especialistas" sem estratificação (D6); "constituir o banco de imagens" (D9);
o argumento do veio natural (D3).

---

## D14 — Nome

**Decisão:** **ARIA** — Análise e Reconhecimento Inteligente de Anomalias.

---

## D15 — A calibração atual é PROVISÓRIA

**Decisão:** o conteúdo do `rock_prompts.json` escolhido antes do protocolo da **D17** é
**provisório e incerto**. Não é resultado de calibração validada e **não deve ser tratado como
tal** por ninguém, em nenhum documento.

Medido em 23/08/2026, quando esta decisão foi escrita: 46 entradas, **13 configurações distintas**
entre as 46, e **18 litologias** com o mesmo conjunto. Ou seja, o número era quase todo
copiado — a configuração não era "da litologia", era de um grupo grande de litologias que ninguém
havia olhado uma por uma.

> ⚠️ Essa contagem **envelhece a cada calibração** e não deve ser reescrita a cada vez. Ela já
> mudou uma vez por motivo legítimo: ao ser calibrada em 01/10/2026 a `siena_white` saiu do grupo
> de 18 (que virou 17) e passou a ser uma configuração distinta a mais. Para contar de novo, não
> confie neste parágrafo — conte:
>
> ```bash
> cd AI/SAM && ..\.venv\Scripts\python.exe -c "import json,collections;d=json.load(open('rock_prompts.json',encoding='utf-8'));r={k:v for k,v in d.items() if not k.startswith('_')};a=collections.Counter(json.dumps(v,sort_keys=True) for v in r.values());print(len(r),'entradas',len(a),'distintas','maior grupo',a.most_common(1)[0][1])"
> ```

**Esvaziado em 09/10/2026 (decisão do autor).** Os valores provisórios **foram apagados do
arquivo**; sobrou só a `siena_white`, a única calibrada de fato. O arquivo deixa de ser "chutes
antigos que ninguém pode usar" e passa a ser o que o calibrador escreve quando uma litologia é
calibrada: **quem não está nele não foi calibrado**. Os valores antigos continuam no histórico do
git (commit anterior a esta data), então nada se perdeu.

Por que foi seguro: nada no código dependia deles. O `inference.py` lê o `calibracao.json`
(09/10/2026), e o calibrador, para litologia sem calibração, já semeava o limiar pela **regra**
(`semear_da_regra`, o joelho da curva) e não pelo número do arquivo. O único efeito que o arquivo
ainda tinha era deixar **sondas pré-marcadas** ao abrir uma litologia — o que contrariava a D17,
em que é a imagem de **descoberta** que decide quais sondas entram. Esvaziar corrigiu isso de
graça.

O mesmo valia para as imagens de `selectRocks/`: a compreensão do autor sobre marcações e sobre
rochas amadureceu desde que foram escolhidas. **A pasta foi zerada em 2026-08-23** e a seleção
recomeçou do zero com o protocolo de 4 vagas (**D17**), junto com a escolha de sondas.

**Ordem de trabalho:** a recalibração segue a **faixa de volume de dados** (**D6**) — faixa A
primeiro. O `rock_viewer.py` já ordena as litologias por volume decrescente e mostra a faixa e o
número de pendentes da faixa a cada iteração, para que a prioridade não dependa de disciplina.

**Fechado em 22/11/2026 (Henrique): a calibração é por litologia**, não por grupo cromático
(grupo de cor da rocha: brancas, beges, verdes...). A pergunta ficou em aberto até a faixa A
estar calibrada; com as 11 feitas, a regra do joelho, que não tem parâmetro livre, produziu
limiares diferentes dentro de um mesmo grupo de cor, e o texto do TCC já descreve a calibração
por litologia. O agrupamento cromático de `dataset.md` fica como registro da configuração
antiga.

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

> ⚠️ **As 3 imagens não produzem 3 limiares para tirar média.** É **um** limiar testado contra
> **três casos** — elas são júri, não medições. Média seria pior que qualquer uma delas: a sutil
> pediria ~0,03, a forte ~0,15, e a média ~0,09 é um valor que nunca foi conferido em imagem
> nenhuma e pode estar ruim nas duas pontas. Média de ótimos não é ótimo. Daí a interface do
> calibrador ser **um slider e quatro previews simultâneos** (D18).

**Layout em disco** — o papel de cada imagem é o próprio nome do arquivo, então nunca há dúvida
sobre qual serve para quê:

```
selectRocks/<litologia>/
├── descoberta.JPG      define QUAIS sondas entram
├── limiar_sutil.JPG    \
├── limiar_tipica.JPG    } definem o LIMIAR de confiança
├── limiar_forte.JPG    /
└── meta.json           split e arquivo de origem de cada uma
```

O `meta.json` registra de onde veio cada imagem (`train/1234.JPG`) e quando foi escolhida — é o
material do statement de reprodutibilidade do TCC. O `inference.py` já lê esse layout sem
alteração.

**Origem das imagens: somente `train/`.** A avaliação sai do `test/` (**D7**: a auditoria cega,
desde 19/11; antes, o conjunto-ouro); calibrar sobre
uma imagem de `test/` seria ajustar o limiar em cima da própria prova. O `val/` fica reservado
para a validação do Aluno. O `rock_viewer.py` já restringe a seleção ao `train/`; a flag `--all`
mostra os outros splits apenas para estudo, sem permitir seleção.

~~Isso não custa cobertura: o split é aleatório estratificado~~ — **corrigido em 10/10/2026.** O
verificado foi só a **proporção** 70/15/15 em todas as 45 classes, não o sorteio. A investigação do
Xception (**D19**, `pendencias.md`) mostrou que a numeração dos arquivos segue a sequência das
chapas e que o `test/` de ao menos uma rocha (`white_superiore`) parece vir de outro bloco. Logo a
restrição ao `train/` **tem custo**: fenômeno que só exista num bloco que caiu inteiro no `test/`
não aparece na calibração. O mesmo fato torna a avaliação mais exigente — a auditoria mede a
marcação em chapa que a calibração não pôde antecipar. Para a faixa A o `train/` tem de 808 a 3.212
imagens por litologia: o que limita a cobertura na seleção é a varredura do autor, não o split.

**Para que lado errar:** a literatura de pseudo-rotulagem tende a limiar **alto** / viés de
precisão — o *Soft Teacher* reporta melhor resultado em 0,9 de score, notando que limiar maior dá
mais precisão e menos recall, e a literatura de ruído de rótulo registra que redes de alta
capacidade **memorizam** rótulo errado. ⚠️ **Não copiar o número:** aquilo são scores calibrados
de um detector; os do SAM3 com prompt de texto são de outra escala. Medido em
`siena_white/descoberta` (2026-09-26, 4 sondas): os scores vão de **0,011 a 0,77**, com mediana
entre 0,04 e 0,08 — ou seja, a massa vive na década baixa e a cauda alta é rala. (A faixa
"0,007–0,3" que este parágrafo citava antes é a dos `conf` **escolhidos** no `rock_prompts.json`
provisório, não a dos scores; eram coisas diferentes com o mesmo nome.) O que transfere da
literatura é a direção, não o número — **na dúvida, cortar mais apertado.**

**O critério tem de ser escrito.** Escolher limiar "no olho" é exatamente o que a **D3** acusa o
inspetor humano de fazer.

Distinção que importa e é fácil de confundir:

| | Muda por litologia? |
|---|---|
| **O valor do limiar** (`crack: 0.08`) | **Sim** — é o objetivo da calibração |
| **A regra que produz o valor** | **Não** — é a mesma para as 45 |

Uma litologia não define o limiar das outras. Ela serve para **calibrar a régua**: o parâmetro da
regra (aqui chamado de X) não é escolhível no abstrato, só se descobre a faixa utilizável vendo o
efeito uma vez em dados reais. Depois disso o X **congela** — se fosse reajustado a cada rocha,
voltaria a ser escolha no olho e a regra deixaria de ser regra.

~~**Verificação ao fim da faixa A:** conferir se a mesma regra se sustentou nas 11 litologias. Se
não, o X passa a ser definido por grupo cromático~~ — perdeu o objeto: a forma fechada da regra
(o joelho, logo abaixo) não tem X. A mesma regra rodou nas 11 sem ajuste, e a calibração ficou
por litologia (**D15**, 22/11/2026).

**Forma da regra — FECHADA em 2026-09-26: opção (b), o joelho da curva.**

A alternativa (a) — *"o maior limiar que ainda marca ao menos X% das feições anotadas"* — foi
**descartada por custo**: exigiria **135 imagens anotadas** (3 × 45), quase três vezes o
conjunto-ouro inteiro, e não cabe no prazo.

**A regra, enunciada:**

> Para cada sonda, some as três vagas de limiar numa única curva *limiar × nº de marcações*. O
> limiar é o **joelho** dessa curva: o ponto de maior distância à corda que liga as duas pontas,
> com o eixo do limiar em escala **logarítmica** (método Kneedle). Implementação:
> `sam_cache.joelho()`.

Três coisas que a regra fixa de propósito:

1. **A vaga `descoberta` fica de fora.** Ela foi escolhida por ser a mais rica em feições — entrar
   na conta puxaria o limiar para cima, que é exatamente o viés de seleção por visibilidade que a
   D17 existe para evitar.
2. **Escala log.** Os scores se concentram na década baixa (medido: 0,011 a 0,77, mediana entre
   0,04 e 0,08). Em escala linear o joelho cairia sempre no primeiro ponto.
3. **A regra é idêntica nas 45.** Muda só o material sobre o qual ela roda — e é isso que produz
   os dois braços do Experimento 1 (**D5**): por litologia → calibrado; sobre todas reunidas →
   default.

**Validação:** ~~as ~50 imagens do conjunto-ouro (**D7**), que seriam anotadas de qualquer forma,
testam se a regra produz bons limiares.~~ Desde 19/11/2026 quem testa a regra é a auditoria cega
(**D7**): os braços `regra_autor` × `autor` da **D5** comparam o limiar da regra com o do autor
nas mesmas sondas. Zero anotação adicional.

**Dois valores por sonda, com papéis distintos:**

| | O que é | Onde é usado |
|---|---|---|
| **limiar da regra** | o joelho, puro, sem intervenção | braços **default** e **calibrado pela regra** do Experimento 1 |
| **limiar de trabalho** | a regra mais o ajuste do autor, se houver | `rock_prompts.json`, produção, e o braço **calibrado pelo autor** (**D5**, 2026-10-05) |

O autor **pode discordar da regra**. Quando discorda, o calibrador grava os dois valores em
`calibracao.json`, junto do critério escrito. Isso preserva o experimento (os braços comparam
regra × regra, uma variável só) e ainda produz um resultado reportável: *"a regra foi aceita sem
ajuste em N das 11 litologias; nas outras, o autor divergiu em média X"*. Concordância alta é
evidência a favor da regra; divergência sistemática é achado sobre onde a curva engana — e nos
dois casos é melhor que "escolhi no olho".

**A calibração vale pelas 4 imagens que a produziram** (2026-10-08). Trocar uma vaga depois de
salvar o `calibracao.json` não apaga o limiar escrito, mas derruba a *afirmação* de que ele foi
escolhido olhando aquelas imagens — e é a afirmação que o TCC reporta, não o número solto. Então
a litologia volta a contar como **não calibrada** (⊘ *desatualizada* no calibrador) até alguém
reconferir o limiar nas imagens novas e salvar de novo. Mecânica: o `rock_viewer.py` registra
cada troca em `substituicoes` do `meta.json`; troca com data posterior ao `calibrado_em` derruba
o selo. Reescolher a **mesma** imagem não é troca e não derruba nada. A troca também apaga o
cache de máscaras daquela vaga (**D18**), que é indexado pela vaga e não pela imagem —
reaproveitá-lo daria curva e polígonos da imagem antiga sob a imagem nova.

- [x] ~~TODO: escolher entre (a) e (b)~~ — resolvido em 2026-09-26. O parâmetro que a antiga
  redação chamava de "X" **deixou de existir**: o joelho não tem parâmetro livre, o que elimina o
  problema de "congelar o X" depois da primeira litologia.

---

## D18 — Calibração por varredura offline (cache de máscaras + scores)

**Decisão:** a calibração roda o SAM3 **uma vez por (imagem, sonda)** com `conf` no piso
(≈0,001), guarda as máscaras e seus scores, e depois varre qualquer limiar **offline**, sem GPU.

**Justificativa — verificada na fonte do `ultralytics`** (`SAM3SemanticPredictor.postprocess`,
leitura feita em 2026-09-26):

```python
pred_scores = (pred_logits.sigmoid() * presence_score).squeeze(-1)
keep = pred_scores > self.args.conf          # filtro puro, depois do modelo
keep = torchvision.ops.nms(boxes, scores, self.args.iou)
```

O modelo produz máscaras e scores **sem conhecer o `conf`**; o `conf` apenas descarta. O NMS roda
depois do filtro, mas processa em ordem decrescente de score e só remove usando um sobrevivente de
score **maior** — então incluir máscaras de score baixo não pode derrubar uma de score alto. As
decisões sobre as máscaras acima de qualquer limiar são idênticas com ou sem as abaixo dele.

**Verificado também por execução, não só por leitura:** `AI/SAM/verificar_d18.py` roda o SAM com
`conf = t` e compara com a filtragem do cache do piso, para 4 sondas × 8 limiares (0,005 a 0,5).
**32 de 32 comparações idênticas** — mesmo número de detecções, mesmos scores e mesmos vértices de
polígono, sem tolerância. É este script que sustenta a afirmação no TCC.

> **A equivalência vale por versão do ultralytics, não por máquina** — o filtro vive no
> `postprocess` dela. Por isso o número da versão **não fica escrito aqui**: o autor alterna entre
> dois PCs e o parágrafo acima já esteve errado por isso (dizia `8.4.61` quando o venv tinha a
> `8.4.52`). Ao passar, o script grava a versão verificada em **`AI/SAM/d18_verificado.json`**, que
> vai para o git: verificar numa máquina vale para a outra na mesma versão. Quem responde "a versão
> daqui já está coberta?" é o `AI/ambiente.py`. Primeiro registro: **8.4.52**, 32/32, em
> 09/10/2026. Ao trocar de versão, rodar o script nela antes de calibrar.

**Consequência: a varredura offline é exatamente equivalente a rodar de novo em cada limiar** —
não é aproximação. O ciclo de calibração deixa de ser "escolho conf → rodo o SAM → olho → ajusto →
rodo de novo" (minutos por iteração) e vira "rodo uma vez → arrasto o slider → vejo o efeito nas 4
imagens simultaneamente". É o que torna o protocolo da D17 viável em tempo humano.

---

## D19 — Classificador: reproduzir o Xception do DeepStoneAI

**Decisão (2026-10-02):** o Estágio 1 é uma **reprodução** do Xception do DeepStoneAI (SBAI
2025; TCC de Pedro Lucas Brito Moreira, 2025), porque o material original não traz pesos
salvos — só a receita, em notebooks Keras.

**Mantido da receita original:** Xception com pesos do ImageNet (`timm`
`legacy_xception.tf_in1k`, o mesmo modelo do Keras); 15 épocas com a base congelada (lr 1e-4) e
fine-tuning das últimas 50 camadas (lr 1e-5); augmentation de flip, rotação, zoom e contraste;
sem pesos por classe.

**Mudado, e declarado no texto:**

| | DeepStoneAI | ARIA |
|---|---|---|
| Framework | Keras / TensorFlow | PyTorch + `timm` (TensorFlow não usa GPU no Windows nas versões recentes) |
| Split | `train/test/valid` fundidos e re-sorteados; `take/skip` sobre dataset embaralhado deixa validação e teste se sobreporem | **split oficial** `train/val/test` (70/15/15) — o mesmo da **D17**; o roteador nunca vê o `test/`, de onde sai a avaliação (**D7**) |
| Resolução | carrega em 480, amplia para 1080 | **480 × 480, sem ampliar** |
| Normalização | só divide por 255 → entrada em [0, 1] | **[-1, 1]**, a escala que os pesos do Xception esperam (`preprocess_input` do Keras) — o original alimentava os pesos do ImageNet fora da escala deles |

**Fidelidade verificada no código (`AI/Xception/common.py`, 2026-10-02):**

- as "últimas 50 camadas" do Keras foram mapeadas para os módulos do timm e conferidas por
  contagem: **12.168.304** parâmetros treináveis na base, igual à conta feita sobre o Keras;
- o BN fica em modo de inferência nas duas fases, como o `training=False` do notebook;
- a cabeça (Dropout 0,5 + Dense) é montada à mão: o `legacy_xception` do timm 1.0.27 calcula o
  dropout e **descarta o resultado** — com o `drop_rate` dele, o Dropout não existiria;
- callbacks do Keras reimplementados com a semântica do Keras (o `ReduceLROnPlateau` do
  PyTorch conta a paciência com um a mais).

**Regra de recuo:** se a acurácia em 480 ficar claramente abaixo dos 99,21% do original, testar
com ampliação — e reportar as duas. O 99,21% **não é diretamente comparável** (split diferente);
é referência, não meta.

**Regra de recuo encerrada sem rodar a ampliação (2026-10-06).** A regra disparou ao pé da letra
(96,72% no `test/`), mas supunha que a causa seria a resolução. A run `xception_480_aleatorio`
(04/10) respondeu a pergunta: com a mesma receita em 480 e a divisão por sorteio do DeepStoneAI,
o modelo dá **99,92%**, acima dos 99,21% do original. A resolução não é o gargalo; a diferença
vem da divisão dos dados. O treino em 1080 não foi feito e o `test/` não foi reavaliado.
Qualquer melhoria além da reprodução (augmentation fotométrica, pesos por classe) só será
testada depois de existir uma validação separada por sequência, tirada do `train/`.

**Como o resultado entra na monografia (2026-10-06).** Os dois números são reportados, nesta
ordem: o resultado do classificador é **96,72%** no `test/` oficial, e o texto explica a causa
(o `test/` de algumas rochas vem de outro bloco, que o treino não viu); em seguida, que com as
imagens embaralhadas entre as divisões, como no DeepStoneAI, a mesma receita chega a **99,92%**.
Leitura do Henrique: chapas do mesmo bloco em treino e teste fazem parte do problema real,
porque os datasets do setor sempre terão chapas do mesmo bloco; os dois números descrevem dois
cenários de uso (bloco já visto e bloco novo), e nenhum é tratado como erro do outro. O modelo
do roteador continua sendo o `xception_480` (split oficial); o `xception_480_aleatorio` é só
medição. Não há mais treino previsto para o classificador.

**Avaliação:** no `test/`, uma única vez, ao final: acurácia, acurácia por classe, F1 macro e
matriz de confusão. Pesos em `AI/models/` (fora do git); métricas em JSON no git.

---

## D20 — Litologias movimentadas: calibrar mesmo assim

**Contexto:** na seleção da faixa A o autor encontrou rochas de padrão movimentado, em que é
difícil dizer o que é defeito e o que é desenho da pedra, e pulou duas delas à espera de uma
opinião da faculdade que ainda não veio. A lista, o porquê e a pesquisa sobre o termo estão em
`dataset.md` → *Litologias movimentadas*.

**Decisão 1 — calibrar (2026-10-07):** as litologias movimentadas **são calibradas como as
demais**, pelo mesmo protocolo (**D17**). Elas não saem do experimento e a calibração não fica
parada à espera de terceiros. A opinião externa continua sendo buscada **em paralelo**; se vier,
entra na calibração dessas litologias.

**Justificativa:** deixá-las de fora tiraria até 3 das 11 litologias da faixa A e exigiria um
critério de exclusão que hoje não existe — a lista é impressão do autor. E a dificuldade de
julgar não é um desvio do trabalho: é a arbitrariedade da **D3** no seu caso mais forte.

**Decisão 2 — o termo (2026-10-07):** o trabalho diz **"movimentada"**, não "exótica", que foi
como o autor as chamou primeiro. "Exótico" é categoria comercial do setor, definida por raridade,
preço e tipo geológico; "movimentado", em oposição a "homogêneo", é o termo técnico para a rocha
cuja estrutura forma desenho (bandamento, foliação). Fontes e ressalvas em `dataset.md`.

> ⚠️ Adotar o termo **não** é afirmar que as três litologias da lista são petrograficamente
> movimentadas — isso não foi verificado por fonte nem por especialista. Até ser, o texto diz
> que o autor as *percebeu* como movimentadas.

**Decisão 3 — o recorte entra no texto (2026-11-19):** a monografia compara as quatro
movimentadas com as sete demais da faixa A (seção 4.5). A razão autor/regra não separa os grupos
(mediana 3,15 contra 3,58); os critérios escritos separam (sondas insuficientes em 3 das 4
movimentadas, contra 1 das 7 demais). O pertencimento continua sendo a identificação do autor.

**Ainda em aberto:**

- um critério de pertencimento aplicável por outra pessoa (classificação petrográfica ou
  medida de imagem);
- como a opinião externa é registrada quando vier (o `calibracao.json` hoje supõe um critério
  escrito só pelo autor). Desde 19/11 a referência da H1 é uma avaliadora externa (**D7**), mas
  ela julga marcações, não o pertencimento da litologia às movimentadas.

---

## D21 — Cada contorno solto é uma marcação própria, sem ponte

**Contexto:** a máscara de uma detecção do SAM pode ter vários contornos soltos. O `Masks.xyn`
do ultralytics os funde numa poligonal só (`masks2segments(strategy="all")` →
`merge_multi_segment`), ligando-os por pontes de ida e volta. Essa poligonal ia para o `.txt` de
treino e para a preview do calibrador, onde cada ponte aparecia como uma reta atravessando a
chapa. Em 09/10/2026, calibrando a faixa A, o autor viu as retas e as rejeitou.

**Decisão (2026-10-09):** **cada contorno vira um polígono próprio**, sem ponte. O autor não se
importa com o número de marcações no rótulo ficar alto. As saídas descartadas foram
`strategy="largest"` (perde área real) e aceitar a ponte declarando-a.

**Como:** `sam_cache.pecas_por_deteccao` tira os contornos direto da máscara, com as mesmas
chamadas do `Masks.xyn` menos a fusão. É a fonte única: o cache do calibrador e o `.txt` do
`inference.py` saem dela.

**O que não muda — a unidade da regra continua sendo a detecção.** O score é da detecção, e as
peças de uma mesma detecção entram e saem juntas na varredura. "Marcação", na curva da **D17**,
no calibrador e no `calibracao.json`, segue significando **detecção do SAM**. Verificado em
09/10/2026 nas três litologias então calibradas: as contagens por vaga no limiar de trabalho
(36 pares) e o limiar da regra das 9 sondas ficaram idênticos; a **D18** passou de novo com 32
comparações.

> Uma diferença pequena no piso: contorno com menos de 3 pontos não é polígono e fica de fora.
> Uma detecção feita só de contornos assim deixa de contar — antes a fusão juntava os pontos e
> ela passava. Em 168 pares (vaga, sonda) medidos, 15 perderam **uma** detecção no piso de 0,001;
> nenhuma acima do limiar de trabalho.

**Em aberto:**

- **A curva da regra deveria contar peças?** Levantado pelo autor em 09/10/2026: se o joelho
  procura onde o ruído começa, a fragmentação pode ser sinal dele. O cache guarda as duas
  contagens. Medido nas 9 sondas calibradas, o joelho por peça ficou mais perto do limiar do
  autor em 5, igual em 2 e mais longe em 2 — e abaixo do autor em todas (`nevada_black`/crack:
  regra 0,018, por peça 0,128, autor 0,240). A forma da regra está fechada na **D17** desde
  26/09; trocá-la depois de ver a divergência é ajustar a regra olhando o resultado, então, se
  for feito, o texto reporta as duas versões e diz que a segunda veio depois.
- **Área mínima.** Separar gera fragmentos minúsculos, que antes ficavam costurados a uma peça
  maior. O filtro e o seu valor são parte do pós-processamento do Professor (`roadmap.md` →
  Fase 3.0).
