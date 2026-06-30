# Roteiro — Apresentação PD1 · ARIA

> Apresentação: `apresentacao/pd1.html` · alvo **10 minutos** · 12 slides
> Autor: Henrique Machado de Oliveira · Orientador: Everson Scherrer Borges

---

## Como rodar

- Abra `pd1.html` em qualquer navegador (duplo clique). Não precisa de internet para funcionar — só as fontes vêm da web; **teste antes na máquina da banca** (se estiver offline, ele usa fontes do sistema, fica bom do mesmo jeito).
- Navegação: **→ / espaço** avança · **←** volta · **F** tela cheia · **Home/End** primeiro/último · clicar na metade direita/esquerda também navega.
- No slide 10 (resultado do SAM), a máscara entra sozinha após ~1 s; **clicar na imagem alterna** entre a chapa original e as anotações — use isso ao vivo.
- Cada slide tem âncora: `pd1.html#6` abre direto no slide 6 (útil se precisar pular).

## Mapa de tempo

| # | Slide | Slide | Acumulado |
|---|-------|------:|----------:|
| 1 | Capa | 0:30 | 0:30 |
| 2 | O problema | 1:00 | 1:30 |
| 3 | Por que automatizar é difícil | 0:50 | 2:20 |
| 4 | Pergunta + Hipótese | 0:50 | 3:10 |
| 5 | Fundamentos | 0:50 | 4:00 |
| 6 | Pipeline ARIA | 1:10 | 5:10 |
| 7 | Calibração do SAM | 1:00 | 6:10 |
| 8 | Protocolo experimental | 0:50 | 7:00 |
| 9 | Resultado — DeepStoneAI | 0:40 | 7:40 |
| 10 | Resultado — SAM (ice_leke) | 1:10 | 8:50 |
| 11 | Honestidade + futuro | 0:50 | 9:40 |
| 12 | Encerramento | 0:30 | 10:10 |

**Regra de bolso:** se passar de ~5:30 no slide 6, acelere a fundamentação. Slides cortáveis sob pressão: **5 (fundamentos)** vira meia frase; **3** pode resumir a um muro só. Nunca corte 4, 6, 10.

---

## Roteiro slide a slide

### Slide 1 — Capa · 0:30 (→ 0:30)
**Fala:**
> Bom dia a todos. Meu nome é Henrique, sou orientado pelo professor Everson, e vou apresentar o ARIA — um pipeline hierárquico Teacher–Student para detectar automaticamente anomalias em chapas de rochas ornamentais. É um problema de uma indústria que o Espírito Santo lidera no país.

**Dica:** respire, não comece com pressa. Deixe a capa no ar enquanto se apresenta.

---

### Slide 2 — O problema · 1:00 (→ 1:30)
**Fala:**
> Hoje, o controle de qualidade da chapa é feito a olho. Um operador olha a superfície e decide se aquela fissura, aquele veio ou aquela mancha desclassifica a peça. O problema é que **não existe um critério único**: dois operadores classificam a mesma chapa de formas diferentes. E o mesmo operador muda ao longo do turno — fadiga, repetição, cansaço visual. Como essa classificação **define o preço de venda**, a inconsistência vira prejuízo direto. E não é um nicho pequeno: estamos falando de um setor com dezenas de milhares de imagens, 45 tipos comerciais de rocha, e o Espírito Santo como principal polo exportador do Brasil.

**Transição:** "A pergunta natural é: por que ainda não automatizaram isso?"

---

### Slide 3 — Por que automatizar é difícil · 0:50 (→ 2:20)
**Fala:**
> Por dois motivos. O primeiro é a **variabilidade geológica**: a mesma feição muda de significado conforme a rocha. Um veio é defeito num mármore branco, mas é padrão natural e esperado num granito. Um modelo generalista, treinado em tudo ao mesmo tempo, confunde as duas coisas e dispara **falso positivo**. O segundo muro é o **custo da anotação**: para treinar visão computacional você precisa de milhares de imagens rotuladas à mão, com defeitos sutis — caro e inviável em escala.

**Dica:** o exemplo veio×fissura é o coração do argumento — diga com convicção, é o que justifica toda a abordagem.

---

### Slide 4 — Pergunta + Hipótese · 0:50 (→ 3:10)
**Fala:**
> Isso me leva à pergunta de pesquisa: **uma classificação prévia, que restringe o domínio visual do segmentador, reduz os falsos positivos frente a um modelo generalista único?** A hipótese — a H1 — é que sim: um especialista que só conhece *um* tipo de rocha sabe qual é a aparência *normal* daquela rocha, e por isso erra menos do que um modelo que tenta dar conta de todas ao mesmo tempo.

**Dica:** este é o slide âncora da defesa. Fale devagar; é o que a banca vai cobrar.

---

### Slide 5 — Fundamentos · 0:50 (→ 4:00)
**Fala:**
> A solução combina três peças já consolidadas. O **SAM** é um modelo de fundação: segmenta imagens sem treino específico, em zero-shot, guiado por texto via CLIP. A arquitetura **Teacher–Student** com pseudo-labeling: um modelo pesado funciona como professor e gera anotações automáticas que treinam um modelo leve, o aluno — sem rótulo humano em massa. E o **YOLO11**, o aluno, que faz inferência rápida na borda, viável em tempo real na linha de produção. A novidade não é nenhuma peça isolada — é **como elas se combinam** para este problema.

**Transição:** "Vamos ver o encaixe."

---

### Slide 6 — Pipeline ARIA · 1:10 (→ 5:10)
**Fala:**
> Este é o pipeline. Entra a imagem da chapa. A **Xception** classifica o tipo litológico — é o estágio 1, o porteiro que decide para qual especialista a chapa vai. Em seguida vem o bloco que é o coração do trabalho, o **Teacher–Student**: o **SAM**, como professor, gera as anotações já calibradas para aquela litologia; e essas anotações treinam os modelos **YOLO**, os alunos — um por tipo de rocha, 45 no total — que produzem os polígonos das anomalias. O ponto central: a hierarquia **restringe o domínio antes de segmentar**. E quero ser claro sobre o escopo: a contribuição que investigo é o **segmentador especialista, o estágio 2** — a classificação é reaproveitada de um trabalho anterior do grupo.

**Dica:** aponte para o bloco tracejado ao dizer "Teacher–Student". É o foco.

---

### Slide 7 — Calibração do SAM · 1:00 (→ 6:10)
**Fala:**
> Como o SAM, que nunca viu rocha na vida, vira especialista? Por **injeção de conhecimento de domínio**. Para cada litologia eu defino, num arquivo de configuração, um conjunto de prompts em linguagem natural e um **limiar de confiança** próprio — é o que está nesse JSON, para a rocha ice_leke. Como o CLIP foi treinado com legendas, frases contextuais funcionam melhor que palavras soltas. Três detalhes importam: as 45 rochas são organizadas em **grupos por cor e textura**, então não calibro 45 do zero; e a imagem usada na calibração é escolhida **à mão** — porque usar o próprio SAM para escolher seria raciocínio circular, enviesaria a avaliação.

**Dica:** "raciocínio circular" costuma render pergunta da banca — deixe claro que é decisão metodológica deliberada.

---

### Slide 8 — Protocolo experimental · 0:50 (→ 7:00)
**Fala:**
> E como eu testo a hipótese? Comparando dois pipelines sobre **a mesma arquitetura YOLO**. De um lado o ARIA: **45 modelos especialistas**, um por litologia, com anotações calibradas. Do outro o baseline generalista: **um único modelo**, prompts genéricos, todas as rochas juntas. Como a arquitetura é idêntica, a comparação **isola exatamente a variável que me interessa — a hierarquia**. As métricas são mAP e IoU, complementadas por validação qualitativa com especialistas do setor.

**Transição:** "Agora, o que já temos de resultado."

---

### Slide 9 — Resultado · DeepStoneAI · 0:40 (→ 7:40)
**Fala:**
> O primeiro estágio já está validado. Num trabalho anterior do grupo, comparamos quatro arquiteturas para classificar as 45 litologias, e a **Xception chegou a 99,21% de acurácia**. Isso é importante porque o pipeline inteiro depende desse porteiro: classificação confiável significa **roteamento confiável** — a chapa certa indo para o especialista certo.

**Dica:** resultado de terceiro/publicado — credite "trabalho do grupo", não é seu experimento central.

---

### Slide 10 — Resultado · SAM (ice_leke) · 1:10 (→ 8:50)
**Fala:**
> E este é o resultado central até aqui. À esquerda, uma chapa real da rocha ice_leke. *(clique para alternar)* Estas são as anotações que o **SAM gerou sozinho**, sem nenhum treino específico em rochas — só guiado pelos prompts calibrados. À direita, dá para ver que cada prompt isola um tipo de feição: **fissura, veio, mancha e áreas escuras**, cada um com seu limiar. Essas máscaras viram polígonos no formato do YOLO — são exatamente os pseudo-labels que vão treinar o aluno. A ice_leke é a **primeira das 45** litologias totalmente calibrada; as outras estão em andamento.

**Dica:** este é o slide visual mais forte — use o clique para alternar original/máscara ao vivo, dá impacto. Não corra.

---

### Slide 11 — Honestidade + futuro · 0:50 (→ 9:40)
**Fala:**
> Sendo honesto sobre o que isto prova: confirma a **viabilidade** — o SAM gera anotações relevantes em zero-shot. Mas **ainda não testa a H1**. A comparação de falsos positivos entre especialista e generalista depende de treinar os modelos YOLO — é a etapa quantitativa seguinte. E como o ground truth vem do próprio SAM, a validação qualitativa com especialistas complementa o mAP e o IoU. Como trabalhos futuros: o loop de aprendizado ativo, a rotulagem multiclasse por tipo de anomalia, e a integração do ARIA como serviço da plataforma Hartheus. Os próximos passos imediatos são calibrar as 45 litologias, treinar especialistas e baseline, e fazer a comparação.

**Dica:** assumir a limitação é força, não fraqueza — bancas valorizam clareza sobre o que ainda falta.

---

### Slide 12 — Encerramento · 0:30 (→ 10:10)
**Fala:**
> Em resumo: ARIA é classificar para segmentar melhor, e a contribuição central é o segmentador especialista Teacher–Student. Obrigado pela atenção — fico à disposição para as perguntas.

**Dica:** termine com calma e silêncio; deixe o "Obrigado" no telão durante a arguição.

---

## Perguntas prováveis da banca (prepare-se)

- **"Se o ground truth é o próprio SAM, a comparação não é circular?"** → Não, porque a comparação especialista×generalista usa a *mesma* fonte de anotação para os dois lados; o que varia é a hierarquia. A qualidade absoluta da anotação é checada à parte, com especialistas.
- **"Por que 45 modelos e não um multitarefa?"** → Exatamente a hipótese: especializar restringe o domínio e reduz falso positivo. O baseline de 1 modelo testa se vale a pena.
- **"E o custo de manter 45 modelos?"** → YOLO é leve; o roteamento pela Xception carrega só o especialista necessário. Trade-off discutido como trabalho futuro (e o loop ativo ajuda).
- **"Por que SAM e não anotação humana?"** → Custo e escala — é o segundo muro do slide 3.
- **"Os prompts em inglês num contexto brasileiro?"** → O CLIP é treinado majoritariamente em inglês; os termos técnicos (crack, vein, stain) são os que melhor ancoram no espaço de embeddings.

## Checklist pré-apresentação

- [ ] Testar `pd1.html` **na máquina/projetor da banca**, em tela cheia (F).
- [ ] Conferir se as 6 imagens do ice_leke aparecem (pasta `figuras/` ao lado do HTML).
- [ ] Ensaiar cronometrando — alvo 10:00, teto ~10:30.
- [ ] Levar o arquivo num pendrive como backup (a pasta `apresentacao/` inteira).
