# Pendências

Caixa de entrada do que está em aberto. Decisões fechadas ficam no [`decisoes.md`](decisoes.md);
o estado de cada parte do sistema, no [`roadmap.md`](roadmap.md).

Regra da casa: item fechado sai daqui. Se ele deixou um fato que precisa ser lembrado, o fato vai
para o documento certo (decisão, dataset, arquitetura). O histórico completo está no git; a
versão anterior a esta reorganização é a do commit `fb24729`.

Última atualização: 28/11/2026

---

## Por onde retomar

➡️ **Amanhã (29/11/2026):** continuar a **revisão do TCC em sessões** (ver *Texto do TCC →
Revisão em sessões*). Primeiro, a sessão rápida de estrutura, discutindo as 6 marcas da segunda
passada; depois, a de fatos (números) e a de citações. Pendentes da revisão de 28/11: a figura do
Cap. 1 e a figura do aplicativo da auditoria (em *Melhorias aceitas ou a decidir*). Sugestão de
calendário até a entrega de 02/12: 29/11 estrutura + fatos; 30/11 citações + consistência; 01/12
escrita e compilação final.

**Plano do Henrique (22/11/2026), nesta ordem:**

1. tratar as pendências que faltam, uma a uma;
2. rever o texto do TCC parágrafo por parágrafo com o Claude (bom momento para a skill
   `humanizer`, usando só a parte que tira vícios de texto de IA: o TCC continua em terceira
   pessoa e tom acadêmico);
3. mandar uma versão ao Rafael, ainda sem os resultados da auditoria (ele não pediu nem deu data);
4. o Henrique faz os julgamentos dele na auditoria.

**Prazos (confirmados em 26/11/2026):** versão escrita para a banca em **02/12/2026**;
apresentação e defesa em **09/12 e 10/12/2026**. Publicação até fevereiro de 2027 (informada em
19/11).

**Ideias e análises da sessão de 25/11:** ver [`reflexao.md`](reflexao.md), seção 12 (próximos
passos sugeridos). As que forem aceitas entram aqui como itens.

---

## Auditoria cega do experimento

O pacote `AI/SAM/auditoria/pacote_aria-auditoria-20261119.zip` (16,8 MB, fora do git) tem 420
marcações, 60 por estrato, de 32 das 33 chapas sorteadas do `test/` (uma chapa entrou no sorteio
mas nenhuma marcação dela foi sorteada). Em 23/11 o aplicativo passou a afastar até a chapa
inteira; desde 24/11 os dois PCs têm o mesmo `.zip` (conferido por hash: só o `index.html` mudou).
O sorteio não se refaz (ver `CLAUDE.md`).

- [x] Mandar o `.zip` para a avaliadora, **Marcelli da Fonseca Carvalho** (estudante de
  Engenharia de Minas). Ela extrai, abre o `index.html`, julga quantas conseguir e devolve o
  `.json` exportado. Enviado em 26/11.
- [ ] Gravar um vídeo curto explicando o aplicativo à Marcelli. Só como usar a ferramenta: sem
  dizer o que o sistema deveria marcar, nem o que o Henrique espera, para não enviesar o julgamento.
- [ ] Combinar com ela um prazo de devolução que caiba antes de 02/12 (ou decidir se o resultado
  entra só na versão da defesa).
- [ ] O Henrique julga a mesma amostra, separado: cada um na sua tela, sem ver nem comentar a
  resposta do outro, e sem abrir `itens.json` nem `limiares.json` antes.
- [ ] Os `.json` vão para `AI/SAM/auditoria/respostas/`; rodar `auditoria_analisar.py`.
- [ ] Rodar também as análises secundárias registradas na emenda de 25/11 da **D4** (exploratórias).
- [ ] Escrever o resultado na seção do experimento (o TODO está em `resultados.tex`).

**Previsão do Henrique, registrada antes dos julgamentos (25/11):** a Marcelli deve marcar menos
coisas como defeito do que ele.

---

## Texto do TCC

### Falta para fechar

- [ ] **Resultado do experimento**, com número; depois, a frase de resultado no resumo e no
  abstract, e a síntese da H1 na conclusão (inclusive se for negativa).
- [ ] **Data da defesa**, quando o Henrique tiver. A folha de aprovação segue comentada; o
  `\approvaldate` ainda tem um valor fictício (15/10/2026).
- [ ] **Título definitivo.** Hoje está o provisório no `macros.tex` (a versão longa, sem
  "Teacher-Student"); as opções enxutas estão em `docs/Titulo TCC.txt`. Escolhido, registrar em
  `decisoes.md`.
- [ ] **Uma frase sobre a `white stain`** não ter sido admitida na `san_francisco_green`, a rocha em
  que ela nasceu. Não é contradição (quem decide é a vaga de descoberta), mas a banca pode
  perguntar. A frase é do Henrique.
- [ ] **Epígrafe de Box e Draper** (*Empirical Model-Building and Response Surfaces*, 1987):
  conferir a página na fonte (~p. 424).

### Conferir no Overleaf

O Overleaf é ligado ao GitHub (`machado-o/ARIA`), mas não puxa sozinho: commit novo só aparece lá
depois de *Menu → GitHub → Pull*.

- [ ] Puxar o que está no git.
- [ ] Ver se o título provisório cabe na capa.
- [ ] Ver se as figuras (arquitetura e as quatro capturas de tela) cabem na página.
- [ ] Ver se o Apêndice A cabe agora: em 25/11 a tabela foi dividida em duas (parte 1 e parte 2),
  porque 45 linhas num float só não quebram de página.
- [ ] Conferir as figuras novas de 26/11 (as 4 imagens de calibração, a curva com o joelho, o
  gráfico regra × autor, os 3 exemplos no capítulo 4 e o Apêndice B com as 11 rochas). Compilado
  localmente: 78 páginas, sem erro.
- [ ] Ler a seção *Adjustment and Anchoring* de Tversky e Kahneman (1974), citada desde 26/11 na
  ferramenta de calibração (ancoragem do controle no valor da regra).

### Revisão em sessões (plano de 28/11/2026)

O Henrique revisa o texto com o Claude em sessões separadas, cada uma olhando uma coisa só. As
marcas de cada sessão vão para `revisao/marcas/` (importáveis no `revisao/revisao_pdf.html`). O
Claude gera as marcas com `revisao/marcar.py` (achados em `.json` → marcas sobre o PDF; precisa do
PyMuPDF, que não está no venv: instalar com `pip install --target <pasta temporária> pymupdf` e
apontar o `PYTHONPATH` para ela). As posições valem para o PDF compilado do mesmo commit; se o
texto mudou, o `revisao/mapear.py` ainda acha cada marca no `.tex` pelo trecho.

1. [x] **Estrutura** (28/11). 20 marcas, todas tratadas, com a opinião do Henrique em cada uma.
   Mudou: Introdução com lista de **Contribuições** (1.6) e objetivo 2 reescrito; Cap. 2 sem o
   parágrafo dos prompts contextuais, YOLO logo depois de Professor–Aluno, kappa definido em
   Métricas; Cap. 3 com a subseção "Litotipos de padrão movimentado" em Conjunto de Dados e uma
   seção nova **"Estágio 2 — Professor"** (configuração, "Do contorno ao polígono" e as Sondas);
   Cap. 4 na ordem do Cap. 3 (classificador primeiro), a 4.4 só com as medições dos contornos;
   Cap. 5 retoma a pergunta, os objetivos e as contribuições, ganha **"Escopo e Limitações"** e
   os trabalhos futuros em ordem; "escore" virou "confiança" em todo o texto; resumo com o
   classificador antes da calibração. Marcas: `revisao/marcas/claude_estrutura_2026-11-28.json`.
   - [ ] **Segunda passada de estrutura** (28/11, feita pelo Claude sobre o texto já mudado): 6
     marcas, ainda **não discutidas**, em `revisao/marcas/claude_estrutura2_2026-11-28.json`.
     Compilar o PDF deste commit e importar. Resumo: (a) objetivo 1 promete "pré-processar", mas
     só houve o rename da pasta; (b) contribuição 5 e resumo dizem "duas ferramentas", e o
     aplicativo da auditoria é a terceira; (c) a abertura do Protocolo (3.6) e a da nova 3.5
     repetem a ideia de adaptação sem mexer nos pesos; (d) talvez a Varredura (3.8) vire
     subseção do Estágio 2; (e) agrupar 4.2–4.4 numa seção "Verificações do Professor"; (f) mover
     o comentário TODO do resultado da H1, na conclusão, para depois do parágrafo da pergunta de
     pesquisa. O Henrique quer ainda uma sessão rápida de estrutura, por segurança.
2. [ ] **Fatos: números** — cada número, data e contagem conferido em `docs/`, nos
   `calibracao.json`, nos `runs/` e no código. Conferir em especial o que entrou em 28/11: as
   imagens com "cerca de 1.300 × 800 pixels" (amostra de 693 imagens, tamanhos variam). A frase
   "o autor observou que a maior parte das chapas tem a matriz limpa" (3.6 e 3.11.1) foi
   **confirmada pelo Henrique em 28/11**: no `rock_viewer`, alguns litotipos tinham várias
   imagens seguidas com anomalias (o mesmo bloco com defeito), mas no geral predominava a matriz
   limpa.
3. [ ] **Fatos: citações** — cada referência diz o que o texto atribui a ela? Inclui a epígrafe e
   o `.bib` (4 entradas não citadas: `diffusion_rogers2003`, `iou_mahmood2021`,
   `sociotech_trist1951`, `tam_davis1989`).
4. [ ] **Consistência** — termos (imagem × vaga, nomes dos braços, *Stain* × *stain*), remissões,
   legendas, ABNT.
5. [ ] **Escrita** — frase por frase, com atenção a palavras repetidas (pedido do Henrique).
6. [ ] **Leitura de banca** — perguntas prováveis, para a defesa.

### Melhorias aceitas ou a decidir

- [ ] **Figura no Cap. 1** (aceita na revisão de estrutura, 28/11): a mesma feição sendo defeito
  numa rocha e desenho valorizado em outra. Só imagens do `train/`. O Henrique escolhe as chapas,
  porque a figura afirma o que é defeito.
- [ ] **Figura do aplicativo da auditoria** na Seção 3.10 (aceita em 28/11). Não pode mostrar chapa
  do `test/` antes de o Henrique julgar: ou uma tela montada com chapa do `train/`, ou a figura
  entra depois dos julgamentos dele.
- [ ] **Seção 4.4 (contornos) mais rica** (ideia do Henrique, 28/11): análise qualitativa com
  figuras (marcações que acertaram ou não), segmentações sobrepostas e o que isso implica, quais
  sondas geram mais polígonos, tamanho dos polígonos. Exige análise nova sobre o cache; hoje a
  seção tem só as medições da fusão dos contornos.
- [ ] **Figuras que ainda faltam.** Feitas em 26/11 (`AI/SAM/figuras_tcc.py`): as quatro imagens de
  calibração, a curva com o joelho, regra × autor, exemplos por rocha (capítulo 4 e Apêndice B).
  Candidata que falta: um desenho dos braços que se encaixam.
- [ ] **Figura "critério único × calibrado"** sobre uma chapa da amostra. Cuidados:
  1. o braço único foi calculado sobre as 11 rochas da faixa A, não sobre as 45: a legenda diz isso;
  2. chapa do `test/` **só depois do julgamento do Henrique** (antes disso, usar `train/` ou `val/`);
  3. é ilustração, não evidência da H1: incluir também um caso de empate ou em que o calibrado piora.
- [ ] **Parágrafos sugeridos em `reflexao.md`** que ainda não entraram: o trabalho seguindo a
  própria ideia (seção 2); o esforço humano comparado ao FracStoneAI (ideia G); no máximo uma
  leitura conceitual. Entraram em 26/11: a mistura no critério único (4.3), ordem × patamar (4.1),
  a ancoragem (seção 3) e os braços que se encaixam (5.1).
- [ ] **Outros trechos de código no texto.** Hoje só o `calibracao.json` entra. Candidatos: a
  filtragem fora de linha, o joelho, os contornos (D21). O Henrique decide.
- [ ] **`fracstoneai_oliveira2026`** está com `note = {No prelo}`. Quando os anais do Latinoware
  2026 saírem no SOL/SBC, trocar por páginas e DOI.
- [ ] **Ler antes de citar:** a dissertação de Meyer (2003) e o trabalho de Bolonha sobre
  caracterização estética de chapas, ambos vistos só em segunda mão.

---

## Rochas movimentadas

O que se decidiu está na **D20**; o tópico completo, em `dataset.md`.

- [ ] **Opinião de alguém que conheça rocha** sobre as quatro movimentadas, e a classificação
  homogênea × movimentada das rochas da faixa A. Decidido em 22/11: pedir à Marcelli **depois** da
  auditoria, se ela topar mais uma tarefa.
- [ ] **Critério de pertencimento** que outra pessoa consiga aplicar: classificação petrográfica ou
  uma medida tirada da imagem. Hoje a lista é impressão do autor.
- [ ] **Registrar a tentativa com exemplo visual.** O Henrique contou (25/11) que já se tentou
  guiar o SAM por um exemplo visual, em vez de palavra, e que pareceu marcar pior. Falta escrever
  quando foi, em que rocha e como se comparou. É um resultado negativo útil para os trabalhos
  futuros sobre vocabulário.

**A hipótese do autor sobre o vocabulário** (20/10/2026): buscar anomalias por palavras teria um
limite, porque não há palavras para todas as formas que a natureza, a lavra e o beneficiamento
produzem. Os dados apontam nessa direção (autor acima da regra nas 45 sondas, "parece faltar
sonda" em 4 critérios, a `white stain` criada por falta de palavra), e a forma honesta de dizer é:
o limiar resolve o "quanto"; a palavra limita o "o quê", e o limite aparece mais nas rochas com
desenho próprio. A auditoria **não** testa isso, porque só julga o que alguma sonda marcou; a
hipótese fica apoiada nos critérios escritos.

---

## Código (tudo opcional para a entrega)

- [ ] **YOLOE** como braço extra, sem treino, com as mesmas sondas (ideia de 06/11, depois da
  Jacitec). Daria número só com uma auditoria nova, porque o pacote de 19/11 não se refaz. Antes,
  conferir se o ultralytics de cada máquina tem o YOLOE.
- [ ] **Um YOLO generalista como demonstração** de que o pipeline fecha (figuras SAM × YOLO e
  FPS), sem hipótese.
- [ ] **A curva da regra deveria contar peças, e não detecções?** Em aberto na **D21**, com a
  primeira medição. Hoje conta detecções, e a forma da regra está fechada desde 26/09.

Do Experimento 2, agora trabalho futuro (**D6**), ficam sem prazo: o `sam_batch.py`, a área mínima
dos fragmentos, a regra de divisão dos dados do Aluno (por sequência ou por sorteio) e contra o que
ele seria avaliado.

---

## Artigo de PD1 e artigo da LatinoWare

Os dois continuam desatualizados (**D13**) e nada foi feito neles. O da LatinoWare foi recusado
(06/11/2026); esta lista só importa se houver nova submissão.

Divergências conhecidas: orientador antigo; "SAM" onde é SAM3; "constituir o banco de imagens"
(**D9**); "45 especialistas" sem estratificação (**D6**); o argumento do veio natural (**D3**);
menções à startup (**D1**); TAM, Difusão de Inovações e Teoria Sociotécnica (**D16**); uma lacuna na
literatura que o Boxes2Pixels derruba. Detalhes menores: o abstract cita "ice leke" e o resumo não;
caixa inconsistente em "Stain"/"stain"; "aproximadamente 34.630 imagens"; falta mostrar um caso em
que a segmentação falhou. O material da monografia pode ser portado quando chegar a vez.

O parecer da LatinoWare (submissão #34865) foi encerrado pelo Henrique em 19/11: não orienta mais o
trabalho. A crítica principal, a hipótese sem teste com dados, é a que a auditoria responde.

---

## Organização do repositório

- [ ] Renomear ou remover
  `apresentações/Overleaf/artigo LatinoWare2026/Exemplo_do_IEEE_adaptado_para_o_Latin_Science_2026 (1)/`
  (o " (1)" é marca de download repetido; é template de referência).

---

## Registro do que já foi resolvido

Só os marcos, para orientar quem procura no git. Os fatos que importam estão nos documentos.

| Data | O quê | Onde ficou |
|---|---|---|
| 23/08 | Recomeço: decisões renumeradas, `selectRocks/` zerado, bugs de desbloqueio (casing, `class_id = -1`) | D1–D17, `roadmap.md` |
| 26/09 | Calibrador pronto; regra do joelho fechada; monografia reestruturada | D17, D18 |
| 02–06/10 | Xception reproduzido; os dois números (96,72% e 99,92%) | D19, `dataset.md` (sequência e blocos) |
| 08/10 | Faixa A selecionada (44 vagas) | `roadmap.md` |
| 09/10 | Contornos sem ponte; `rock_prompts.json` esvaziado | D21, D15 |
| 10/10 | Quarto braço; `white stain` registrada | D5, D8 |
| 19/10 | Conferência pós-bug de 10/10 (a `santa_cecilia` refeita sem `vein`) | `CLAUDE.md` |
| 20/10 | Faixa A calibrada: autor acima da regra nas 45 sondas | `resultados.tex`, seção 4.5 |
| 22/10 | Prévia na Jacitec (correu bem; daí a ideia do YOLOE) | `apresentações/jacitec/` |
| 06/11 | Monografia compilada pela primeira vez; LatinoWare recusada; conjunto-ouro condicional | D7 |
| 19/11 | Auditoria cega no lugar do conjunto-ouro; seção 4.5 e Apêndice A; passada de tom | D7, D4 |
| 22/11 | Versões do texto de 06/11 e 19/11 juntadas (a de 06/11 está no commit `e402f75`) | git |
| 23/11 | Experimento 2 e H2 viram trabalho futuro; agradecimentos | D6 |
| 24/11 | Epígrafe e banca (Everson e Igor) no `macros.tex` | `macros.tex` |
| 25/11 | Regra de decisão da H1; `reflexao.md`; apêndice dividido; documentos reorganizados | D4 |
| 26/11 | Revisão do TCC inteiro; regra da H1 na metodologia; 6 figuras novas e Apêndice B | `figuras_tcc.py` |
