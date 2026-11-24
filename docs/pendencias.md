# Pendências — ARIA

> Caixa de entrada de itens soltos. Marcos de desenvolvimento ficam no
> [`roadmap.md`](roadmap.md); decisões fechadas, em [`decisoes.md`](decisoes.md).
>
> Consolida o que antes estava espalhado em `auditoria.md`, `revisao-artigo.md` e
> `artigo-sbc.md` (os três foram removidos em 2026-08-23).
>
> Última atualização: 2026-11-23

---

## ➡️ Retomada — por onde começar (atualizado em 22/11/2026)

> Escrito em 11/10/2026 e revisto em 20/10, 06/11, 19/11 e 22/11. Riscar cada item ao fechar;
> quando a lista acabar, apagar a seção.
>
> **Sessão de 22/11 — as duas versões do TCC foram juntadas.** O texto de 06/11 (PC 1) nunca
> teve commit, e o de 19/11 (PC 2) foi escrito sem ele. Ficou a versão de 19/11 como base, mais o
> que só a de 06/11 tinha: correções de compilação (legendas, ficha catalográfica, larguras de
> tabela, siglas protegidas no `.bib`, Quadro dos braços do Exp. 1), detalhes da reprodução do
> Xception, a verificação da D18 nas duas versões, o efeito residual da D21, a precisão sobre a
> imagem típica e a citação do IoU (VOC no lugar de `iou_mahmood2021`). Duplicatas descartadas:
> o Apêndice A em `apendice.tex` e o segundo "terceiro resultado" da conclusão. A versão de 06/11
> inteira está no commit `e402f75`, segundo pai do merge. Compilado aqui em 22/11 (60 páginas, sem erro).
> As sobras de 06/11 foram decididas na mesma sessão (ver *Monografia — em aberto*). **Falta:**
> puxar no Overleaf (GitHub → Pull) e ver se o título provisório cabe na capa. Na mesma sessão,
> uma revisão geral dos `.md` e do código de `AI/` tirou as menções vencidas ao conjunto-ouro, ao
> `"default"` e aos limiares provisórios.
>
> **Plano do Henrique (22/11/2026), nesta ordem:**
> 1. tratar as pendências que faltam, uma a uma;
> 2. rever o texto parágrafo por parágrafo com o Claude;
> 3. mandar uma versão ao Rafael — **sem** os resultados da auditoria, o que é aceitável (ele
>    ainda não pediu nem deu data);
> 4. o Henrique faz os julgamentos dele na auditoria, para comparar com os da avaliadora.
>
> **Sessão de 19/11:** o texto avançou no que não dependia de decisão (ver *Escrita* → *revisão
> de 19/11*): seção 4.5 *Calibração da Faixa A*, Apêndice A, referências completas (nenhum
> `TODO-` sobrando), título provisório na capa e uma passada de tom no texto inteiro
> (`diretrizes-escrita.md` §2.5). Dar commit e push **antes** de editar no Overleaf ou no outro
> PC — em 06/11 isso não foi feito, e o texto divergiu (ver a sessão de 22/11, acima).
>
> **Auditoria cega do Experimento 1 — pronta para julgar (19/11/2026, emenda da D7).** O pacote
> `AI/SAM/auditoria/pacote_aria-auditoria-20261119.zip` (16,8 MB, gitignored; nas duas máquinas
> desde 22/11, vindo pelo `ARIA_backup_20261119.zip`) tem 420
> marcações, 60 por estrato. Elas caem em 32 das 33 chapas sorteadas do `test/`: uma chapa foi
> para a pasta `imgs/`, mas nenhuma marcação dela saiu no sorteio.
>
> **23/11: o aplicativo do pacote passou a afastar até a chapa inteira.** Antes a escala parava
> em 3,2×, e em 357 das 420 telas o afastar máximo não chegava à chapa inteira (na tela 41,
> mostrava 48% da largura). O `.zip` do PC 2 foi refeito com
> `auditoria_preparar.py --atualizar-app`: o `itens.js` e as imagens são os mesmos, só o
> `index.html` mudou. ⚠️ **No PC 1, depois do pull, rodar o `--atualizar-app` antes de enviar o
> `.zip` de lá**, porque o de lá ainda tem o aplicativo antigo. Próximos passos:
>
> 1. [ ] Mandar o `.zip` para a avaliadora, **Marcelli da Fonseca Carvalho** (estudante de
>    Engenharia de Minas). Ela extrai, abre o
>    `index.html` no computador, julga quantas conseguir e devolve o `.json` exportado.
> 2. [ ] O Henrique julga a mesma amostra, **separado**: cada um na sua tela, sem ver nem
>    comentar a resposta do outro. Ele não abre `itens.json` nem `limiares.json` antes.
> 3. [ ] Os `.json` vão para `AI/SAM/auditoria/respostas/`; rodar `auditoria_analisar.py`.
> 4. [ ] Escrever o resultado na seção do Experimento 1 (o TODO está lá), mais a figura único ×
>    calibrado sobre uma chapa da amostra. ⚠️ **Só depois do julgamento do Henrique:** a chapa é
>    do `test/` e está na amostra, e ver as marcações de um braço antes de julgar quebra o "às
>    cegas" dele.
> 5. [x] ~~Nome completo da avaliadora para os agradecimentos~~ — Marcelli da Fonseca Carvalho
>    (Henrique, 22/11/2026). Entra nos agradecimentos quando eles forem escritos.
>
> O texto do TCC já descreve a auditoria (metodologia, H1, objetivos, escopo) e traz o que não
> depende dos julgamentos: volume de marcações por braço e a reprodutibilidade da regra entre as
> duas máquinas.
>
> **Experimento 2 — fechado em 23/11/2026: vira trabalho futuro inteiro, com a H2** (nota na
> **D6**; em 22/11 a decisão tinha sido tentar só a faixa A). Com isso saem do caminho o
> `sam_batch.py`, a regra de split do Aluno e o "contra o quê avaliar".
> - [x] ~~Listar e reescrever os trechos do TCC que tratam o Experimento 2 e a H2~~ — feito em
>   23/11/2026 (o Henrique pediu para reescrever direto). Hipótese única (H1); o objetivo da H2
>   deu lugar à reprodução do classificador; a seção do Exp. 2 saiu da metodologia e dos
>   resultados; "Experimento 1" virou "o experimento"; o desenho de três braços do Aluno foi para
>   os trabalhos futuros (*Treinamento do Aluno e especialização por litologia*). Resumo e
>   abstract com um experimento só. O título ficou: "pseudo-rotulagem" continua valendo, porque o
>   Professor gera os rótulos. Compilado: 59 páginas, sem erro.
> - Opcional, só se sobrar tempo: um YOLO generalista como demonstração (figuras + FPS).
>
> **Prazos (informados em 19/11, "pelo que fiquei sabendo"):** defesa para a banca **até
> dezembro**; publicação **até fevereiro de 2027**. Confirmar com o Rafael. O 01/12 de 06/11
> fica como data de trabalho para a versão que vai à banca.

- [x] ~~**Conferir o que a sessão de 10/10 pode ter estragado**~~ — feito pelo Henrique em
  19/10/2026. A `santa_cecilia` foi salva de novo **sem a `vein`** (de propósito); `itaunas_white`
  e o crack 0,0385 da `ubatuba_green` foram conferidos e ficaram como estavam. Linha do tempo
  da `white stain` (pelos horários do `_cache/`): nasceu como sonda exploratória na
  `san_francisco_green` (10/10 17:23), foi registrada como id 6 às 18:08 e entrou salva em
  `ubatuba_green` (18:12), `itaunas_white` (18:16) e `santa_cecilia` (18:23).
- [x] ~~**Calibrar as 4 que faltavam da faixa A**~~ — `san_francisco_green`, `white_mirage`,
  `golden_storm` e `white_olympus`, em 20/10/2026. **A faixa A está calibrada: 11 de 45.** Os
  quatro critérios escritos dizem que **parece faltar sonda** para marcar o que o autor queria.
  Três delas são movimentadas (**D20**); a `white_olympus` não é, e a quarta movimentada, a
  `shadow_white`, não registrou essa queixa. Nenhuma litologia teve conferência de especialista
  (Henrique, 23/11/2026); isso fica registrado no `dataset.md` e no texto do TCC, e os critérios
  escritos não são retocados depois da calibração. Ver o achado em *Código* → regra × autor.

**3. ~~Texto do TCC — compilar~~** — compilado em 06/11/2026 (ver *Escrita* → Compilar). As
equações do joelho, o `lstlisting` com `literate` e as figuras saem corretos no PDF. Compilado de
novo em 22/11, depois de juntar as versões de 06/11 e 19/11.

**4. O que falta no texto, em ordem de peso** (resposta a "se pedirem o arquivo, falta muito?"):

- [ ] **Experimento** — a seção de resultados está sem número; depende só dos julgamentos da
  auditoria (pacote pronto, ver *Retomada*). O Experimento 2 saiu do escopo em 23/11 (**D6**).
- [ ] Por consequência: frase de resultado no resumo/abstract e a síntese de H1 na conclusão.
- [x] ~~**Figuras:** a do pipeline e as quatro capturas de tela~~ — feito em 20/10/2026.
  `figuras/arquitetura_aria.png` (citada no texto) e os quatro prints do Henrique, recortados
  sem a barra do navegador e a do Windows. Os originais ficam fora do repo, na pasta acima do
  `ARIA/`. Falta conferir no Overleaf se cabem na página.
- [x] ~~**Referências fora do `.bib`:** `TODO-sam3` e `TODO-movimentada`~~ — feito em 19/11/2026:
  `sam3_carion2026` (ICLR 2026, conferido no arXiv) e `camargo_geociencias2015`, com a definição
  atribuída a Meyer (2003) no texto, porque Meyer foi lido em segunda mão. Entrou um TODO novo,
  `TODO-fracstoneai` (ver *Escrita*).
- [ ] **Pré-textuais:** ~~agradecimentos~~ (escritos em 23/11/2026 e ligados no `main.tex`);
  dedicatória fica sem, por ora (Henrique); epígrafe de Box (24/11); banca no `macros.tex`
  (Everson e Igor, 24/11); falta só a data da defesa
  (o Henrique passa quando tiver).
- [x] ~~**Tabela regra × autor** nos resultados~~ — feito em 19/11/2026: seção 4.5 *Calibração
  da Faixa A* (`tab:calib_faixa_a`, por litologia) e o Apêndice A
  (`pos_textuais/apendice_limiares.tex`, os 45 pares), gerado do `regra_x_autor.csv`. Se uma
  litologia for recalibrada, gerar o CSV e o apêndice de novo.
- [ ] **Outros trechos de código** no texto — o Henrique disse que pensaria depois; hoje só o
  `calibracao.json` entra. Candidatos: a filtragem fora de linha, o joelho, os contornos (D21).

Como versão **parcial** o texto se sustenta: método completo, quatro seções de resultado
(varredura, escores, contornos, classificador) e o capítulo já abre com "resultados obtidos até
o momento".

---

## 🔴 Bloqueadores — dependem do Henrique

- [ ] **Prazos: defesa até dezembro de 2026, publicação até fevereiro de 2027** (informado pelo
  Henrique em 19/11/2026: "pelo que fiquei sabendo", ainda sem confirmação). O **01/12/2026**
  (definido em 06/11 como data de trabalho) fica como data da versão que vai à banca. Ele
  substituiu o "pelo menos um mês depois da Jacitec" (~23/11) de 09/10, que já tinha
  substituído o 15/10. Falta confirmar os prazos com o Rafael.
- [x] ~~**Agenda de outubro tira ~9 dias do cronograma**~~ (passou) (informado pelo Henrique em 05/10/2026).
  **11 a 18/10:** Foz do Iguaçu, LatinoWare (publicação do artigo FracStoneAI). **20 a 23/10:**
  Jacitec, onde ele apresenta uma prévia do TCC. O fim do dia 18 e o dia 19 vão para preparar a
  apresentação e outras responsabilidades — **não contar com eles**. Janela útil antes da viagem:
  **05 a 10/10**. Com a entrega final em novembro ou depois, o que essa agenda aperta é a
  **prévia da Jacitec**, não o TCC.
- [x] ~~**Confirmar se o DeepStoneAI usou este mesmo dataset.**~~ — sim, confirmado em
  2026-10-02 pelo artigo do SBAI (**D9**). Citação obrigatória.
- [x] ~~**Contato do especialista do setor** para a preferência pareada cega (D7)~~ — resolvido
  em 19/11/2026 pela emenda da **D7**: a preferência pareada saiu, e a avaliadora da auditoria
  cega é a Marcelli da Fonseca Carvalho, estudante de Engenharia de Minas. O formato é o pacote
  da auditoria (ver *Retomada*).
- [x] ~~**Versão final submetida ao Latinoware**~~ — **o artigo do TCC foi recusado** (informado
  em 06/11/2026). Ele seguiu na LatinoWare só com a versão do **projeto**, não com a do TCC.
- [x] ~~**Parecer da LatinoWare**~~ — **encerrado pelo Henrique em 19/11/2026: não orienta mais o
  trabalho.** Não trazer de volta. Registro antigo, só por histórico:
  (submissão #34865, recusa de 14/09/2026) — recebido em 06/11/2026.
  Veio só o *Review 1*. Ele abre dizendo que a premissa é "muito interessante" e o texto "bem
  escrito", e faz quatro críticas. Elas servem de revisão externa da monografia. Primeira leitura
  de cada uma contra o estado atual, ainda **não discutida com o Henrique**:
  1. *"A hipótese central não é avaliada empiricamente; não se mostra que a especialização reduz
     falsos positivos em relação ao baseline."* — Continua verdade na monografia: os
     Experimentos 1 e 2 estão vazios. Com o conjunto-ouro condicional (emenda da **D7**), a taxa
     de falso positivo só existe se ele for feito. Além disso, desde a **D3** o problema central
     é a arbitrariedade, não o falso positivo, então a hipótese tem de ser escrita de um jeito
     que a avaliação disponível consiga responder.
  2. *"Diz-se que as máscaras são satisfatórias sem dizer por qual critério."* — Na monografia
     isso já tem resposta parcial: a regra do joelho (**D17**) e o critério escrito de cada
     `calibracao.json`. **Conferido em 19/11/2026:** "satisfatório" não aparece em nenhum `.tex`.
  3. *"O pipeline se diz zero-shot, mas há várias adaptações ao domínio (limiar, prompts,
     imagens representativas)."* — Na monografia, "zero-shot" só aparece descrevendo modelos de
     fundação, não o pipeline. **Feito em 19/11/2026:** parágrafo novo na abertura de
     *Protocolo de Calibração* (`metodologia.tex`), assumindo a calibração como adaptação do
     Professor ao domínio e dizendo que o pipeline não é descrito como zero-shot.
  4. *"Falta ablação: a contribuição vem do Xception, dos prompts, dos YOLOs especialistas ou de
     todos?"* — Em parte coberta: os quatro braços da **D5** separam regra e autor e sondas e
     limiar; o controle da **D6** separa número de modelos e qualidade da anotação. **Não
     coberta:** a contribuição do Xception (roteador certo × errado × sem roteador). **Feito em
     19/11/2026:** entrou como limitação declarada na conclusão (*Contribuição do classificador
     não isolada*, com os ~3% de erro no `test/`). Rodar a ablação não está previsto.
  
  A crítica 1 continua aberta até os julgamentos da auditoria (ver *Retomada*): é a auditoria
  que mede a taxa de falso positivo de cada braço.

---

## 🧪 Avaliação — alternativas ao conjunto-ouro (decidido em 19/11/2026)

> Levantado em 05/10/2026, quando o Henrique não sabia se teria tempo de anotar as ~50 imagens.
> **Decidido em 19/11/2026 (emenda da D7, H1 reescrita):** auditoria por amostragem, com recall
> relativo por *pooling* entre os braços e kappa entre dois avaliadores. A preferência pareada
> saiu. O cardápio abaixo fica como registro do que foi considerado.

- [x] ~~**Decidir se o conjunto-ouro se mantém, encolhe ou é substituído.**~~ — substituído pela
  auditoria cega (**D7**).

| Alternativa | Custo | O que mede | O que não mede |
|---|---|---|---|
| **Auditoria por amostragem** — sortear detecções do modelo e julgar cada uma certa/errada | baixo (um clique por detecção, sem desenhar polígono) | precisão, taxa de falso positivo | recall (não mostra o que o modelo deixou passar), qualidade da borda |
| **Preferência pareada cega** — já é a fonte 2 da D7 | baixo, zero anotação | qual braço é melhor | número absoluto: diz "A melhor que B", não "A acerta X%" |
| **Rótulo fraco** — só "tem/não tem anomalia" por imagem ou por célula de uma grade | médio | precisão e recall em nível de detecção | qualidade da máscara (IoU) |
| **Anomalia sintética** — inserir trincas artificiais em chapas limpas | médio (código) | recall com gabarito exato | desempenho em defeito real; o realismo é questionável |
| **Consistência sem rótulo** — chapa espelhada/girada/reescalada deve dar a mesma máscara | baixo, automático | robustez | acerto (dá para errar de forma consistente) |
| **Corrigir a máscara do modelo** em vez de anotar do zero | médio | IoU, precisão, recall | — mas a anotação fica ancorada no modelo; a D7 rejeita isso de propósito |

- **Aluno contra os rótulos do SAM** não entra na lista: mede fidelidade da cópia, não acerto
  (D7). Serve como diagnóstico de treino.
- O que vale ainda: o resultado do Experimento 1 cobre a faixa A (as 11 calibradas), não as 45.

---

## 🪨 Litologias movimentadas — dá para marcar de forma correta? (em aberto)

> Levantado pelo Henrique em 07/10/2026, durante a seleção da faixa A, com o nome de
> "exóticas"; o termo passou a "movimentadas" no mesmo dia (**D20**). O tópico, a lista das
> litologias, onde ele encosta nas decisões e a pesquisa sobre o termo estão em `dataset.md` →
> *Litologias movimentadas*. Aqui fica só o que está pendente.

- [x] ~~**Decidir o que fazer com as movimentadas nos experimentos.**~~ — decidido em 07/10/2026
  (**D20**): calibrar mesmo assim, com a opinião externa buscada em paralelo. Deixar de fora e
  esperar a opinião foram as saídas descartadas.
- [ ] **Conseguir a opinião de alguém da faculdade que conheça rocha** sobre `shadow_white` e
  `san_francisco_green`. Pedida, sem resposta até 08/10/2026 — data em que as duas foram
  **selecionadas sem ela** (a **D20** já dizia que não bloqueia). Continua valendo: serve para
  conferir a marcação dessas quatro movimentadas depois do fato, e vale pedir também a
  classificação *homogênea × movimentada* das litologias da faixa A — é o critério técnico que a
  pesquisa encontrou. **Decidido em 22/11/2026:** pedir à Marcelli **depois** da auditoria, se ela
  topar mais uma tarefa — não junto do pacote.
- [x] ~~**Decidir o termo.**~~ — decidido em 07/10/2026 (**D20**): "movimentada", não
  "exótica", que é categoria comercial (raridade e preço).
- [ ] **Hipótese do autor sobre o desfecho (20/10/2026, levantada numa conversa com um amigo).**
  O Henrique suspeita que a resposta final do TCC seja esta: buscar anomalias por palavras
  (prompts) ainda é infundado, porque o SAM não foi treinado a fundo para cada especificidade e
  não parece haver palavras suficientes para nomear as formas que a natureza gera, mais as que
  vêm da lavra e do beneficiamento.
  **Posição registrada na conversa:** isso não ameaça o TCC; é um resultado possível, e os dados
  já apontam nessa direção — o autor acima da regra em 45/45 sondas, o "parece faltar sonda" em
  quatro critérios (três deles de movimentadas) e a `white stain` criada por falta de palavra.
  Mas "infundado" é forte demais: o que o trabalho mede é **até onde** o prompt textual funciona,
  e o indício é que funciona razoavelmente nas homogêneas e piora nas movimentadas. A frase
  honesta seria algo como "o vocabulário textual é o gargalo, e isso piora com a heterogeneidade
  da rocha". Cuidado: é hipótese até a auditoria do Experimento 1 medir — o recorte
  homogênea × movimentada (item abaixo) é o que a testaria. Na Jacitec entrou como hipótese
  (slide 9).
- [ ] **Decidir o critério de pertencimento.** Hoje a lista é impressão do autor. Para virar
  recorte, precisa ser aplicável por outra pessoa: classificação petrográfica vinda de quem
  conhece rocha, ou medida de imagem.
- [x] ~~**Decidir se as movimentadas são reportadas num recorte à parte**~~ — sim, decidido em
  19/11/2026 (**D20**, decisão 3); está na seção 4.5 da monografia.
- [ ] **Ler antes de citar:** a dissertação de Meyer (2003), origem da definição *homogêneo ×
  movimentado*, e o trabalho de Bolonha sobre caracterização estética de chapas — os dois só
  foram vistos em segunda mão.
- **As quatro movimentadas estão selecionadas** — `white_mirage` (07/10), `golden_storm`,
  `shadow_white` e `san_francisco_green` (08/10). São os casos para observar, na calibração, se a
  dificuldade aparece em número (distância entre o limiar da regra e o do autor). O autor
  registrou que a seleção das duas antes puladas **foi difícil**, e saiu sem conferência de
  especialista. ~~Isso precisa estar no critério escrito do `calibracao.json`~~ — fechado em
  23/11/2026: **nenhuma** litologia teve especialista (Henrique), e o critério escrito é o registro
  datado do que o autor escreveu ao calibrar; acrescentar uma frase depois o tornaria menos
  confiável, não mais. O fato fica no `dataset.md`.

---

## 🎤 Prévia na Jacitec — apresentada em 22/10/2026

> **Apresentação: quinta, 22/10/2026, 14h00–14h40, ~10 minutos** (pode passar um pouco).
> Slides em `apresentações/jacitec/slides.html`.

> **Como foi (relato do Henrique, 06/11/2026):** correu bem; passou um pouco do tempo, porque
> havia muito a dizer. Daí saiu a ideia do YOLOE (ver *Código*).

> Plano do Henrique (05/10/2026): até a viagem, focar em terminar seleção e calibração; na
> prévia, mostrar exemplos de imagens marcadas pelo SAM **default × calibrado**. A avaliação
> quantitativa contra o conjunto-ouro (**D7**) entra como próxima etapa, já definida na
> metodologia e ainda não executada.

- [x] ~~**Figuras regra × autor**~~ — geradas em 20/10/2026 em `apresentações/jacitec/figuras/`
  (vagas típica e forte das 11 litologias; `figuras_regra_autor.py`). É o braço "regra com as
  sondas do autor" contra o "calibrado pelo autor" da **D5**, **não** o default: este continua
  indisponível, pelo motivo do item abaixo. Todas as imagens são do `train/` (cuidado 2
  atendido). O cuidado 3 fica com o Henrique: escolher para o slide também um caso em que o
  autor não ficou claramente melhor.
- [ ] **Gerar as figuras *default × calibrado*** — não ficaram prontas para a prévia; passam para
  o **Experimento 1** (Fase 2). Os cuidados abaixo continuam valendo. São quatro braços desde
  10/10 (**D5**): `unico`, `regra_todas`, `regra_autor` e `autor`. Três cuidados:
  1. ~~**Não usar o `"default"` do `rock_prompts.json` como baseline.**~~ — a entrada foi apagada
     em 09/10, e o braço `unico` já existe: está no `auditoria/limiares.json`, calculado pela
     regra sobre as 11 da faixa A (não sobre as 45 — dizer isso na legenda).
  2. **Chapa do `test/` só depois do julgamento do Henrique.** A amostra da auditoria sai do
     `test/`; ver as marcações de um braço numa chapa dela antes de julgar quebra o "às cegas"
     dele (**D7**). Antes disso, usar `train/` ou `val/`.
  3. **Apresentar como exemplos ilustrativos, não como evidência.** Um par em que o calibrado
     ficou melhor não prova a **H1**, e a pergunta "foram escolhidos a dedo?" é previsível.
     Incluir também um caso de empate ou em que o calibrado piora.
- **Escopo da prévia:** a faixa A, seleção e calibração completas (20/10/2026). Material
  pronto em `apresentações/jacitec/`: figuras regra × autor, `regra_x_autor.csv`,
  `pipeline_estado.png` (o diagrama com o estado de cada etapa) e os prints das ferramentas.

---

## 🧩 Código

> ✅ Os três bugs de desbloqueio (**Fase 0**) foram corrigidos e verificados em 2026-08-23.

- [ ] 💡 **Opcional, só se sobrar tempo antes de 01/12: comparar com o YOLOE** (ideia de
  06/11/2026). O YOLOE é um YOLO de segmentação da Ultralytics que recebe a classe como texto,
  como o SAM3, quase na velocidade de um YOLO comum. Rodado **sem treino**, com as mesmas
  sondas, ele vira mais um braço: SAM3 calibrado × YOLOE. Para dar **número** a essa comparação,
  as detecções do YOLOE teriam de entrar numa auditoria nova — o pacote de 19/11 não se refaz
  (ver `CLAUDE.md`). Antes de qualquer coisa, conferir se a versão do `ultralytics` de cada
  máquina tem o YOLOE. Esperado: o mesmo limite de vocabulário textual do SAM3 (hipótese de 20/10/2026).

- [x] ~~**Calibrar `siena_white` no calibrador**~~ — feito em 2026-10-01 (`calibracao.json`).
  Primeira litologia calibrada de fato: **1 de 45**. Entraram 3 sondas — `vein`, `Stain` e
  `Dark patches`.
- [x] **Achado (20/10/2026): na faixa A inteira, o autor ficou acima do joelho em 45 de 45
  sondas**, com razão autor/regra mediana de **3,3×** (de 1,1× no crack da `shadow_white` a
  17,9× na white stain da `white_olympus`). Nas vagas típica e forte, a regra produz de 7 a 228
  marcações por chapa; o autor, de 0 a 46. A divergência que a `siena_white` sugeria (abaixo)
  se repetiu em todas: é o *"onde a curva engana"* da **D17**. ~~Falta decidir como isso entra na
  monografia~~ — entrou em 19/11/2026: seção 4.5 e Apêndice A (ver *Escrita*). Registro original:
- [x] **Observar: o autor divergiu da regra nas 3 sondas da `siena_white`**, e sempre para cima
  (limiar de trabalho ≈ 2× o joelho: `vein` 0,145 → 0,335; `Stain` 0,203 → 0,392 — era 0,414
  até a recalibração de 09/10/2026, feita já com a preview sem pontes da **D21**;
  `Dark patches` 0,235 → 0,397). Critério escrito: subir até a vaga típica parar de marcar matriz
  limpa. Uma litologia não é padrão, mas se a divergência se repetir na faixa A é o achado que a
  **D17** prevê (*"onde a curva engana"*) — e a direção bate com o "na dúvida, cortar mais
  apertado".
- [x] ~~**Selecionar as 4 imagens das litologias da faixa A**~~ (**D17**) — **a faixa A fechou em
  08/10/2026**: **44 de 180 vagas**, as 11 litologias com 4/4. `siena_white`, `nevada_black`
  (02/10), `ubatuba_green` e `ipanema_beige` (03/10), `itaunas_white` (05/10), `santa_cecilia`
  (06/10), `white_mirage` (07/10), `golden_storm`, `white_olympus`, `shadow_white` e
  `san_francisco_green` (08/10). As duas últimas tinham sido puladas (03/10 e 07/10) por ser
  difícil julgar o que é defeito nelas, e foram feitas sem a opinião de especialista, que não
  veio — as quatro movimentadas estão na lista em `dataset.md` → *Litologias movimentadas*.
- [x] ~~**Calibrar as quatro litologias da faixa A que faltavam**~~ — feito em 20/10/2026.
  **11 de 45** com `calibracao.json`: a faixa A inteira.
- [x] ~~**Decidir o próximo passo depois da faixa A**~~ — foi o Experimento 1, com a auditoria
  cega (19/11/2026). A seleção da faixa B não começou.
- [ ] **Decidir a regra de split do Aluno** (por sequência ou por sorteio), adiada pelo
  Henrique. O que se sabe sobre sequência e blocos está no item do Xception, logo abaixo.
- [x] ~~**Decidir o que fazer com o resultado do Xception no `test/`**~~ — decidido em
  2026-10-06 (**D19**): reportar os dois números, 96,72% com a causa explicada e 99,92% com as
  imagens embaralhadas; sem ampliação e sem mais treino. Histórico da investigação:
  96,72% contra 99,21% do DeepStoneAI. 169 erros, concentrados em poucos pares:
  `naica → white_olympus` 33, `white_himalaya → white_liberdade` 31, `white_superiore →
  kalahari` 21 e `→ white_olympus` 15. A `white_superiore` acertou 35/37 no `val/` e **0/36** no
  `test/`. Olhando as imagens, as do `test/` são acinzentadas, com veios lineares e paralelos;
  as do `train/` e `val/` são brancas, com veios ramificados. Parecem outro bloco. Se isso se
  confirmar, a regra de recuo da D19 (ampliação) não ataca a causa. O problema é de split, não
  de modelo. O `test/` já foi usado e não pode ser reavaliado.
  **Como o DeepStoneAI dividiu (verificado em 04/10, `DeepStoneAI/OneDrive_2_02-10-2026/`):**
  o `organize2.ipynb` **junta** `train/`, `valid/` e `test/` numa pasta por rocha; o
  `Xception.ipynb` faz um split **aleatório por imagem** (`validation_split=0.3`, seed 123) e
  corta a parte de validação ao meio, em val e test (15% cada; o artigo diz 25%). Como as
  imagens em sequência são chapas vizinhas do mesmo bloco, com os mesmos veios (observação do
  Henrique), os 99,21% foram medidos com vizinhas do treino dentro do teste. Provável agravante,
  ainda não confirmado: `take`/`skip` sobre um dataset que reembaralha a cada passada faz val e
  test se sobreporem. **Os dois números não medem a mesma coisa:** o `test/` do ARIA parece
  separado por lote (chapa nova), o do DeepStoneAI não.
  **Medido em 04/10** (`train.py --protocolo aleatorio`, run `xception_480_aleatorio`): mesmo
  modelo e mesma receita, só trocando a divisão pelo sorteio por imagem do DeepStoneAI →
  **99,92%** no teste (4 erros em 5.195; balanceada 99,91%). No `test/` original, 96,72%. A
  diferença de ~3 pontos vem da divisão, não do modelo: o sorteio põe chapas vizinhas do treino
  no teste. 70% do teste sorteado veio do `train/` original. **Falta decidir** como isso entra na
  monografia, e a regra de split do Aluno (por sequência ou por sorteio), adiada pelo Henrique.
  **Decidido em 06/10:** a ampliação para 1080 não será rodada (registro na **D19**); melhoria
  além da reprodução só depois de uma validação separada por sequência, tirada do `train/`.
  **Sondagem de 06/10** (miniaturas 32 × 32, diferença absoluta média, 5 rochas; medida
  grosseira, só de cor e brilho): a ordem numérica dos arquivos é mesmo uma sequência. No
  `train/`, imagens consecutivas ficam a 4,0 uma da outra e pares sorteados a 12,5
  (`white_superiore`); 4,0 contra 15,3 na `ipanema_beige`. O `test/` da `white_superiore` é mais
  escuro (brilho 188, contra 213 no `train/` e 226 no `val/`) e fica mais longe do treino que o
  `val/` (6,1 contra 3,0), o que apoia a hipótese de outro bloco. **Não vale para toda rocha:**
  na `ipanema_beige` o `test/` está tão perto do treino quanto o `val/` (3,2 e 3,8), e na
  `white_himalaya` o `val/` também está longe (35,6; `test/` 22,6). A validação por sequência
  não chegou a ser montada: o Xception foi fechado com os dois números.
- [x] ~~**Rever a vaga típica de `nevada_black`, `ubatuba_green` e `ipanema_beige`**~~ — revista
  em 2026-10-03. A típica tinha sido escolhida, em algumas, como "chapa com defeito em quantidade
  média"; a regra é a chapa **mais comum** da rocha, limpa se a rocha costuma ser limpa. É ela
  que impede o limiar de descer demais, porque mostra se ele marca matriz limpa. Revisão: só a
  `ubatuba_green` mudou (`train/175` → `train/2031`); nas outras duas a maioria das chapas tem
  mesmo algum defeito, e a escolha já seguia a regra. Para refazer uma vaga, desde 08/10/2026
  basta `rock_viewer.py <rocha>`: a litologia completa abre em revisão e oferece substituir a
  vaga (não é mais preciso apagar o arquivo à mão).
- [x] ~~**Terminar o `calibrator.py`**~~ — feito em 2026-09-26: 3 abas (descoberta / limiar /
  fechar), um slider com as 4 previews simultâneas sobre o cache do `sam_cache.py`, curva de
  limiar com o joelho marcado como sugestão, e critério de texto obrigatório para salvar.
- [x] ~~**Fechar a regra de limiar**~~ — fechada em 2026-09-26 na **D17**: opção (b), joelho da
  curva em escala log, sem parâmetro livre.
- [x] ~~**Decidir o que fazer com a ponte entre contornos do `masks.xyn`**~~ — decidido e feito
  em 2026-10-09 (**D21**): cada contorno é um polígono próprio, na preview e no `.txt`.
- [ ] **Decidir se a curva da regra conta detecções ou peças** (em aberto na **D21**, com a
  primeira medição). Hoje conta detecções.
- [x] ~~**Seção 4.3 da monografia** (`resultados.tex`, *Geometria dos Polígonos*) diz que o
  tratamento da ponte é "etapa a definir". Reescrever com a **D21**.~~ — visto em 19/11/2026: o
  item estava desatualizado. A 4.3 já descreve a separação dos contornos (revisão de 10/10).

---

## ✍️ Escrita

> A **monografia** (`apresentações/Overleaf/TCC/`) foi reestruturada em 2026-09-26 e já
> nasce alinhada com as decisões. O **artigo de PD1** e o **LatinoWare2026** continuam sendo
> saída desatualizada (**D13**) e ainda não foram tocados.

### ✅ Monografia — feito em 2026-09-26

- [x] `bibliografia.bib` saiu de 0 bytes para **37 entradas** (32 migradas do artigo + 5 novas:
  Soft Teacher, Unbiased Teacher, memorização de rótulo, Kneedle, Boxes2Pixels).
- [x] `main.tex` destravado — capa, ficha, resumo, listas e sumário ligados; capítulos apontam
  para os arquivos previstos.
- [x] `introducao.tex`, `ref_teorico.tex`, `metodologia.tex`, `resultados.tex` e `conclusao.tex`
  escritos do zero. `testes.tex` e `Texto Inicial.tex` removidos.
- [x] Resumo e abstract reais (faltam só as frases de resultado).
- [x] Título: typo "Convulacionais" e "avarias" corrigidos; ficha catalográfica com as tags reais
  e o orientador certo; `\local`, `\approvaldate` e palavras-chave preenchidos.
- [x] TAM / Difusão de Inovações / Teoria Sociotécnica **fora** (**D16**) — as três entradas
  ficaram no `.bib` sem citação, o que o bibtex simplesmente ignora.
- [x] Boxes2Pixels citado e posicionado (§2.7) sem alegar lacuna na literatura.
- [x] "Constituir o banco" → "selecionar, caracterizar e pré-processar um conjunto público"
  (**D9**); mAP explicado como AP por causa da classe única (**D2**).

### ✅ Monografia — revisão de 2026-10-10 (compilada em 06/11)

- [x] Experimento 1 com os **quatro braços** da **D5**; o limiar do autor ganhou papel próprio.
- [x] Classificador tratado como **reprodução** (**D19**): seção na metodologia, resultados com
  96,72% e 99,92%, limitação na conclusão corrigida.
- [x] Contornos (**D21**) decididos no texto; `white stain` no quadro de sondas.
- [x] **Split deixou de ser "aleatório"** no texto e na **D17**; rename `whte_liberdade` (**D9**)
  declarado; quadro de ambiente com as duas máquinas.
- [x] Explicações novas: o joelho em equação e a alternativa descartada (135 imagens), como uma
  sonda entra no conjunto, as litologias movimentadas (**D20**), um critério escrito real.
- [x] Seção **Ferramentas de Seleção e Calibração** (rock_viewer, calibrador, registro de
  calibração em `lstlisting`). `\lstlistingname` do template: "Algoritimo" → "Código".
- [x] `verificar_tex.py` reconhece o `label=` do `lstlisting`.

### ✅ Monografia — revisão de 2026-11-19 (compilada em 22/11)

- [x] **Seção 4.5 *Calibração da Faixa A*** (`resultados.tex`, `sec:res_calibracao`): sondas
  admitidas (2 a 6 por litologia, 45 pares), regra × autor (45/45 para cima, razão mediana 3,3,
  quartis 2,1 e 4,7, 34/45 com o dobro ou mais), marcações por vaga, o critério dominante
  ("matriz limpa", 7 de 11) e o "falta sonda" (4 de 11). Tabela `tab:calib_faixa_a`.
- [x] **Apêndice A** (`pos_textuais/apendice_limiares.tex`, ligado no `main.tex`): os 45 pares.
- [x] **Síntese da conclusão:** um terceiro resultado já firmado, a divergência regra × autor.
- [x] **Recorte movimentadas × demais** na 4.5 (**D20**, decisão 3) e trabalho futuro sobre o
  vocabulário de sondas.
- [x] **Passada de tom** (`diretrizes-escrita.md` §2.5, pedido do Henrique): *Limitações* virou
  *Escopo*, com dois parágrafos; saíram a rotulagem binária (é decisão, **D2**), a equivalência
  da varredura (já está na 4.1), a integração e a latência (já estão em trabalhos futuros) e o
  efeito líquido (fica na metodologia do Experimento 2). Na metodologia, as movimentadas perderam
  "elo mais frágil" e "a opinião de especialista foi pedida e não veio"; a referência e a
  preferência pareada, as frases defensivas. Na fundamentação, o "sem recorrer à alegação de
  lacuna" e o "não como hipótese original".
- [x] **Resumo e abstract:** diziam que a avaliação "usa um conjunto de referência anotado" (não
  existe ainda) e que o Aluno é "em tempo real" (nunca medido). Trocados pelos resultados que
  existem: regra × autor, movimentadas e classificador.
- [x] **Título provisório** na capa (`macros.tex`).
- [x] **FracStoneAI** citado com os números do artigo publicado, na introdução e na §2.7, que
  agora também liga o ARIA ao trabalho futuro que o FracStoneAI propôs (classificar a litologia
  e especializar a segmentação).
- [x] **Corrigido — o texto afirmava o que não era verdade:** a subseção *Litologias
  movimentadas* dizia que "o registro de calibração de cada uma o declara" (a falta de
  especialista). Nenhum dos quatro critérios diz isso. O texto passou a dizer que **o trabalho**
  o declara, e na passada de tom do mesmo dia a frase saiu. O pedido do `dataset.md` (o critério do `calibracao.json` dizer)
  foi retirado em 23/11/2026 (ver *Litologias movimentadas*).
- [x] **Corrigido:** a limitação *Independência parcial da referência* dizia que o
  conjunto-ouro "foi anotado", o que ainda não aconteceu (e agora é condicional). Passou ao
  presente.
- [x] **Referências:** `sam3_carion2026` e `camargo_geociencias2015` novas; o Boxes2Pixels com
  os prenomes corrigidos (eram "Mike" e "Hasan"; são Camile Lendering e Erkut Akdag, conferido no
  arXiv); o `note` do `dataset_araujo2023`, que sairia impresso na lista de referências e tinha
  um TAB no lugar do `\t` de `\textit`, virou comentário.
- [x] **TCC do Pedro Lucas e FracStoneAI** posicionados em §2.7 e citados na introdução (ver o
  item abaixo, que fica aberto pelos dados que faltam).
- [x] **`verificar_tex.py`:** não reconhecia `\cite[p.~X]{chave}` nem `\citeonline[...]{}`;
  uma chave inexistente citada com página passaria sem aviso.

### 🟡 Monografia — em aberto

- [x] ~~**Sobras da versão de 06/11**~~ — decididas pelo Claude em 22/11/2026, a pedido do
  Henrique (texto completo de 06/11 no commit `e402f75`). **Entraram:**
  - *Fundamentação, SAM 3:* o escore é o produto da probabilidade da detecção pelo escore de
    presença, logo não é probabilidade calibrada (conferido em
    `ultralytics/models/sam/predict.py`, linhas 2301–2302, na 8.4.61).
  - *Fundamentação:* *vein* designa tanto o veio mineral quanto a veia sanguínea.
  - *Fundamentação:* como o Boxes2Pixels funciona e a diferença de partida (caixa humana × palavra
    e limiar por litologia).
  - *Resultados, 4.5:* regra 4.093 × autor 572 marcações nas 33 imagens de limiar (o 572 confere
    com a soma da Tabela `tab:calib_faixa_a`).
  - *Conclusão:* no *Escopo*, uma frase dizendo que a concordância entre calibradores não foi
    medida; em *Trabalhos futuros*, o item *Concordância entre calibradores*.

  **Ficaram de fora:**
  - Os números do próprio TCC do Moreira: em 19/11 o texto passou a usar só os do artigo
    publicado, e os dois não batem.
  - "As sondas não identificam o tipo da anomalia": a rotulagem binária é decisão (**D2**), e a
    passada de tom a tirou das limitações.
  - O critério de pertencimento às movimentadas, a frequência de cada sonda e a `nevada_black`
    com `light spot`: detalhe sem peso no argumento.

- [x] ~~**`TODO-fracstoneai`**~~ — `fracstoneai_oliveira2026`, montada do PDF final em 19/11/2026,
  com `note = {No prelo}`: os anais do Latinoware 2026 ainda não estavam no SOL/SBC (o último
  volume era o de 2025). **Quando saírem, trocar o `note` por páginas e DOI.** ⚠️ Os números que
  este arquivo registrava (mAP50-95 de 0,04 a 0,21, "ruído de anotação") **não batem com o
  artigo publicado**: lá são precisão de máscara até 0,744 e mAP@0,5 de máscara de 0,10 a 0,36,
  e a leitura dos autores é que parte dos falsos positivos são defeitos reais deixados fora pelo
  critério de anotação. O texto usa os do artigo.
- [x] ~~**Entrada `moreira_tcc2025`**~~ — curso e campus os mesmos do ARIA (Henrique, 19/11/2026).
- [ ] **Título:** está na capa, **provisório**, a versão mais longa (sem "Teacher-Student"), para
  ver se cabe depois de compilar. Escolhido o definitivo, registrar em `decisoes.md`.
- [ ] **A `white stain` não foi admitida na `san_francisco_green`**, a litologia em que ela
  nasceu (calibrada em 20/10, só com `Stain` e `Dark patches`). A metodologia conta que ela foi
  registrada porque, testada ali, marcou manchas que a `light spot` não alcançava. Não é
  contradição (quem decide é a vaga de descoberta), mas a banca pode perguntar. Vale uma frase
  do Henrique explicando.
- [x] ~~**Citar e posicionar o TCC do Pedro Lucas Brito Moreira**~~ — feito em 19/11/2026
  (§2.7 e introdução), com as pendências de dados acima. Registro original: (IFES, 2025, *Redes Neurais
  Convolucionais para Segmentação e Classificação de Rochas Ornamentais*, **mesmo orientador**).
  É o trabalho mais próximo do ARIA: mesmo dataset, Xception (99,21%) + YOLO de segmentação de
  defeitos com **anotação manual** e 4 classes semânticas, métricas modestas por ruído de
  anotação. O ARIA responde exatamente a esse ponto — Professor (SAM3) no lugar da anotação
  manual, critério parametrizado (**D3**), rótulo binário (**D2**). Material em
  `Projects/ARIA - Análise e Reconhecimento Inteligente de Anomalias/DeepStoneAI/`. Entradas do
  `.bib` criadas (`moreira_tcc2025`, `fracstoneai_oliveira2026`); o artigo do SBAI 2025 também é
  citado (**D9**).
  - **Números para a motivação (D3)** — vêm do **FracStoneAI**, citado com os números do artigo
    publicado (ver o item `TODO-fracstoneai`, acima). ⚠️ Os "mask mAP50-95 de 0,04 a 0,21" que
    este item registrava vinham do repositório (`docs/NEXT-STEPS.md`) e **não batem** com o
    artigo; não usar.

- [x] ~~**`\cite{TODO-sam3}`** em `ref_teorico.tex`~~ — `sam3_carion2026`, em 19/11/2026.
- [x] ~~**Conferir a entrada `boxes2pixels_lendering2026`**~~ — conferida no arXiv em 19/11/2026;
  os prenomes estavam errados e foram corrigidos. Título e número (2604.11162) estavam certos.
- [x] ~~**Figura da arquitetura**~~ — `figuras/arquitetura_aria.png`, descomentada e citada
  no texto em 20/10/2026.
- [ ] **Resumo e abstract:** acrescentar as frases de resultado e conclusão quando os
  experimentos rodarem.
- [ ] **Conclusão §5.1:** sintetizar H1 e H2 — inclusive se o resultado for negativo.
- [ ] **Escolher o título do TCC.** Desde 19/11 o `macros.tex` tem o título **provisório** (ver o
  item *Título*, acima); o antigo ("…utilizando pipeline com abordagem *Teacher-Student*") ficou
  comentado ali. As duas opções enxutas estão em `docs/Titulo TCC.txt`. **O Overleaf é ligado
  ao GitHub (`machado-o/ARIA`), mas não puxa sozinho:** commit novo só aparece lá depois de
  *Menu → GitHub → Pull*. Quando escolher: aplicar no
  `macros.tex` e fechar como decisão em `decisoes.md`.
- [x] ~~**Banca**~~ — Prof. Dr. Everson Scherrer Borges e Prof. Dr. Igor Henrique Beloti Pizetta
  (Henrique, 24/11/2026), no `macros.tex`. A folha de aprovação segue comentada até a data da
  defesa (`\approvaldate`, hoje um valor fictício de 15/10/2026).
- [x] ~~**Dedicatória, agradecimentos e epígrafe**~~ — agradecimentos (23/11); epígrafe de Box e Draper,
  *Empirical Model-Building and Response Surfaces*, 1987 (24/11; conferir a página na fonte, ~p. 424
  — Kelvin foi descartado por soar como "só vale o que é número", contra a D3); dedicatória sem, por ora.
- [x] ~~**Compilar.**~~ — compilado localmente em 06/11/2026 (TinyTeX nesta máquina, pdfLaTeX +
  BibTeX): 63 páginas, sem erro, sem caixa estourando, sem referência indefinida. Corrigido na
  compilação: "Fonte: Fonte:" em todas as legendas (o `\legend` da classe já escreve "Fonte:"),
  tabelas largas, listagem partida, siglas em minúscula nas referências. O Overleaf continua
  sendo a fonte; a compilação local é conferência. Para refazer: pdflatex com
  `-output-directory` fora do repo e copiar o `.bib` para lá antes do bibtex (o bibtex não abre
  caminho com acento) — ou copiar a pasta `TCC/` inteira para um caminho sem acento e compilar
  lá (feito assim em 22/11: 60 páginas, sem erro, sem caixa estourando, sem referência
  indefinida, BibTeX sem aviso). A capa com o título provisório não foi conferida visualmente.

### 🔴 Artigo de PD1 e LatinoWare2026 — nada feito

> O artigo da LatinoWare2026 **foi recusado** (06/11/2026), e a lista abaixo só importa para
> ele se houver nova submissão. O parecer chegou e foi encerrado em 19/11 (ver *Bloqueadores*).

Continuam valendo, agora só para essas duas pastas: orientador desatualizado, "SAM" onde é SAM3,
"constituir o banco de imagens" (**D9**), "45 especialistas" sem estratificação (**D6**), o
argumento do veio natural (**D3**), menções ao Hartheus (**D1**), TAM/Difusão/Sociotécnica
(**D16**), e a lacuna na literatura derrubável pelo Boxes2Pixels. O material da monografia pode
ser portado para lá quando chegar a vez.

- [ ] Abstract (EN) cita "the *ice leke* lithotype"; o resumo (PT) omite. Devem ser fiéis.
- [ ] Caixa inconsistente: "Stain"/"stain", "Dark patches"/"dark patches".
- [ ] "aproximadamente 34.630 imagens" — ou "~34.600", ou o número exato sem "aproximadamente".
- [ ] Mostrar **um** caso em que a segmentação falhou.

## 📁 Organização do repo

- [x] ~~**`LatinoWare2026/artigo-overleaf.zip`**~~ — não existe mais (conferido em 22/11/2026).
- [ ] **`apresentações/Overleaf/artigo LatinoWare2026/Exemplo_do_IEEE_adaptado_para_o_Latin_Science_2026 (1)/`**
  — o `" (1)"` é marca de download repetido. É template de referência; renomear ou remover.
- [x] ~~**Três pastas chamadas "artigo"** e a convenção de nomes do topo~~ — a reorganização em
  `apresentações/` (`Overleaf/TCC`, `Overleaf/artigo de PD1`, `Overleaf/artigo LatinoWare2026`,
  `apresentacao de PD1`, `jacitec`) resolveu as duas (conferido em 22/11/2026).

---

## ✅ Resolvido em 2026-08-23

- Hartheus removido do repositório (D1); `Hartheus.md` deletado.
- `pontos-tcc.md` fundido em `decisoes.md`; `diretrizes-implementacao.md` fundido no `CLAUDE.md`;
  `auditoria.md`, `revisao-artigo.md` e `artigo-sbc.md` consolidados aqui.
- `CLAUDE.md` corrigido: afirmava que `rock_prompts.json` e `selectRocks/` eram gitignored (não
  são, estão versionados) e citava um typo `whte_liberdade` que não existe mais.
  > ⚠️ **Esta segunda metade estava errada** (visto em 09/10/2026). O typo existia: a pasta do
  > dataset era `whte_liberdade` e só o `rock_prompts.json` tinha sido corrigido, então a busca
  > nunca casava e o `evaluate.py` quebrava. Resolvido de verdade em 09/10/2026 renomeando a
  > pasta do dataset (**D9**).
- Contagem do dataset corrigida em `dataset.md`: são **14** litologias com <200 imagens, não 7.
- `apresentacao/roteiro.md` já estava com o orientador correto — o item estava desatualizado nas
  listas antigas.
- Ausência de definição operacional de falso positivo → resolvida por **D7**.
- "A calibração nunca foi demonstrada" → vira o **Experimento 1** (D5).
- "45×1 confunde duas variáveis" → resolvido pelo braço de controle (**D6**).
- "Suficiência de dados por especialista não é discutida" → virou **variável do experimento** (D6).
- Falta de statement de reprodutibilidade → resolvida por dataset público (**D9**).
