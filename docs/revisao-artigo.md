# Revisão do artigo SBC + apresentação PD1

> Levantamento de pontos de melhoria feito em **2026-07-01**. Nada foi alterado ainda —
> este arquivo é a lista de trabalho para aplicar as mudanças depois.
>
> Método: o artigo (`Overleaf/artigo/main.tex`) foi lido primeiro **como um revisor externo**,
> ignorando o conhecimento do projeto (Fase 1); depois relido **cruzando com as fontes internas**
> (`decisoes.md`, `arquitetura.md`, `dataset.md`, `pontos-tcc.md`) para achar o que o projeto tem
> e o artigo não conta (Fase 2). Por fim, checagem da pasta `apresentacao/`.
>
> Prioridade sugerida no fim do arquivo.

---

## Fase 1 — Leitura "cega" (só o texto, ignorando o projeto)

Impressão geral: escrita madura, registro formal uniforme, boa progressão, honesta sobre o
estágio preliminar. Os pontos abaixo são de **rigor científico e consistência**, não de redação
básica.

### Conteúdo / rigor

- [ ] **F1.1 — A calibração é afirmada, mas nunca demonstrada (nem qualitativamente).**
  O texto diz que calibrar prompts/limiares "converte um modelo genérico em segmentador
  especializado" (§Fundamentação, §Calibração), mas as figuras mostram só o resultado já
  calibrado. Falta o contraste *default × calibrado* na mesma chapa. Sem ele, não há evidência
  de que a calibração fez diferença. **Maior retorno sobre esforço: um par de figuras
  (mesma imagem, config `default` vs calibrada).**
- [ ] **F1.2 — O desenho "45 × 1" confunde duas variáveis.** O texto afirma que a comparação
  "isola a variável da hierarquia" (§Protocolo Experimental), mas o pipeline especialista muda
  simultaneamente (a) nº de modelos (45 vs 1) **e** (b) prompts calibrados vs genéricos. Se o
  ARIA vencer, não dá para atribuir o ganho só à hierarquia. Opções: reconhecer que é um
  "tratamento composto", ou acrescentar um braço intermediário (1 modelo generalista treinado
  com prompts calibrados). A frase "isola exatamente" está forte demais.
- [ ] **F1.3 — "Falsos positivos" (núcleo da H1) não tem definição operacional.** A H1 gira em
  torno de reduzir falsos positivos, mas o Protocolo de Avaliação só define mAP e IoU — que não
  são taxa de falso positivo. Como o *ground truth* vem do próprio SAM, falta dizer **como** um
  falso positivo será medido concretamente.
- [ ] **F1.4 — Velocidade/FPS é vendida o tempo todo e nunca é avaliada.** A Fundamentação dedica
  subseção a YOLO/Edge/FPS e o "Tipo de Pesquisa" promete medir velocidade, mas o Protocolo de
  Avaliação só tem mAP e IoU. Incluir FPS na avaliação **ou** reduzir o discurso de tempo real.
- [ ] **F1.5 — Suficiência de dados por especialista não é discutida.** O artigo usa o
  desbalanceamento natural como motivação e, logo depois, propõe 45 modelos treinados só nas
  imagens da sua litologia — litologias raras terão pouquíssimos exemplos. Esse tensionamento
  fica sem resposta.
- [ ] **F1.6 — mAP "sobre N classes" contradiz a rotulagem binária.** A metodologia diz que tudo
  vira uma classe única, mas a Equação de mAP soma AP sobre N classes. Com uma classe, mAP = AP.
  Esclarecer o que é N (classes de anomalia? litologias? thresholds de IoU?).
- [ ] **F1.7 — A seção de Resultados só mostra acertos.** Nenhuma leitura crítica de onde a
  segmentação falhou/super-segmentou/perdeu feição. Mostrar **um** caso imperfeito aumenta a
  credibilidade.

### Consistência / copidesque

- [ ] **F1.8 — Abstract (EN) × Resumo (PT) divergem.** O inglês cita "the *ice leke* lithotype";
  o português omite o litótipo. Devem ser traduções fiéis.
- [ ] **F1.9 — Caixa inconsistente dos termos de prompt.** "Stain" vs "stain", "Dark patches" vs
  "dark patches", "crack". Tabela 1 em minúsculas; figuras e texto misturam. Padronizar.
- [ ] **F1.10 — "aproximadamente 34.630 imagens"** — "aproximadamente" + número exato é
  contraditório. Usar "~34.600" ou "34.630" (sem "aproximadamente").
- [ ] **F1.11 — Tabela 1 lista 5 anomalias; a Figura 3 mostra 4** (falta *light spot*), sem
  explicação para o leitor. (Ver F2.4 — a explicação existe no projeto.)
- [ ] **F1.12 — Sem statement de reprodutibilidade** (disponibilidade de código/dataset, versão
  dos modelos, hiperparâmetros). Aceitável em WIP, mas uma frase ajudaria.

### Escopo

- [ ] **F1.13 — A subseção "Adoção Tecnológica e Indústria 4.0" (TAM, Difusão, Sociotécnica)**
  soa acoplada num artigo de visão computacional. Você já se protege ("referencial de apoio"),
  mas dilui o foco. Considerar enxugar para 2–3 linhas.

---

## Fase 2 — O que o projeto tem e o artigo não conta

Cruzando com as fontes internas. Ausências que deixam partes do artigo incompletas ou imprecisas.

- [ ] **F2.1 — É SAM3, não "SAM" v1. ⚠️ (mais importante)** `arquitetura.md` deixa claro que o
  Professor é **SAM3 via Ultralytics**, mas o artigo escreve só "SAM" e cita `kirillov2023`
  (SAM v1, 2023) — modelo diferente do que roda. Nomear "SAM3" e ajustar a citação/versão. É o
  ponto mais atacável por um revisor da área. (Propagar também para a apresentação — ver A.2.)
- [ ] **F2.2 — Os class_ids já são gerados; só são colapsados (D2).** O artigo diz que a
  multiclasse é "extensão futura", mas não conta que `inference.py` **já produz** IDs por prompt
  (`vein=0, crack=1, Stain=2, Dark patches=3, light spot=4`), colapsados para 0 antes do treino.
  Isso muda a leitura de "trabalho futuro caro" para "porta já aberta, sem reprocessar o dataset".
- [ ] **F2.3 — Por que *ice leke*? Porque é uma rocha exótica/difícil.** `dataset.md` lista
  *ice leke* entre as texturas "muito fora do padrão, dificultando a generalização" (junto de
  kalahari e quartzito_venom). Dizer isso transforma a demo num **teste de estresse deliberado** —
  o resultado zero-shot fica mais impressionante. Hoje a escolha do litótipo parece arbitrária.
- [ ] **F2.4 — A ausência de *light spot* na Figura 3 tem explicação.** *ice leke* é rocha clara;
  pela própria estratégia de calibração, rochas claras usam *dark patches* e não *light spot*
  (que é para rochas escuras). Uma frase fecha o furo de F1.11.
- [ ] **F2.5 — O split train/val/test existe e não é mencionado.** `dataset.md` registra splits
  train/val/test. Um protocolo experimental precisa dizer como os dados são particionados.
- [ ] **F2.6 — Existe ferramental de calibração** (`rock_viewer.py`, `calibrator.py` Streamlit).
  A metodologia descreve a calibração iterativa de forma abstrata; mencionar a ferramenta dá
  concretude/reprodutibilidade ao "inspecionando as máscaras até satisfatória".
- [ ] **F2.7 — A alegação sobre prompts contextuais tem lastro no paper do CLIP.** O artigo
  apresenta "frases contextuais desambiguam melhor" como hipótese dos autores; `arquitetura.md`
  mostra que é achado do paper do CLIP (o template `"a photo of a [X]"` supera `"X"` em zero-shot).
  Atribuir explicitamente transforma especulação em extrapolação fundamentada.

---

## Apresentação (`apresentacao/` — roteiro + HTML)

- [ ] **A.1 — Orientador inconsistente entre 4 lugares. ⚠️ CRÍTICO.** A troca Everson → **Rafael
  Silva Guimarães** foi feita na capa do HTML (commit "Coordenador") e na fala do slide 1 do
  roteiro (commit "rafael"), mas ficaram para trás:
  - `apresentacao/roteiro.md` **linha 4** (cabeçalho) ainda diz "Everson Scherrer Borges";
  - `Overleaf/artigo/main.tex` **linha 17** (autor) e **linha 22** (`eversonborges@gmail.com`)
    ainda usam Everson.

  Papéis (confirmado 2026-07-01): **Rafael Silva Guimarães** = orientador do TCC (orienta a
  pesquisa); **Everson Scherrer Borges** = professor da disciplina PD1 (avalia a entrega).
  **Decisão:** vai o **Rafael** no artigo (o bloco de autor lista quem orienta a pesquisa);
  a apresentação já está certa, falta alinhar `roteiro.md` linha 4 e `main.tex` linhas 17/22.
  Confirmar com o Everson se a disciplina exige listar o professor como coautor.
- [ ] **A.2 — "SAM" vs "SAM3" na apresentação** — mesma questão de F2.1; propagar a correção
  para os slides 5, 6, 7, 10 e para a fala do roteiro quando ajustar o artigo.
- [ ] **A.3 — "isola a hierarquia" repete a superafirmação de F1.2.** Slide 8 do HTML e a fala do
  slide 8 do roteiro afirmam que a comparação "isola exatamente a variável — a hierarquia".
  Provável pergunta de banca; alinhar com a decisão tomada em F1.2.
- [ ] **A.4 — Caixa "stain"/"Stain" no HTML** — os chips do slide 10 usam minúsculas
  (`stain`, `dark patches`) enquanto o card JSON do slide 7 usa "Stain"/"Dark patches".
  Cosmético; alinhar junto de F1.9.
- [x] **A.5 — Robustez do HTML checada** — navegação, escala responsiva (`fit`), lógica de reveal
  do slide 10 (máscara entra após ~0,85 s, clique alterna), barra de progresso e
  `prefers-reduced-motion` estão corretos. O checklist do roteiro já cobre testar offline/fontes
  na máquina da banca. Nenhum bug funcional encontrado.

Observações positivas: o número "≈34,6 mil" nos slides é mais limpo que o "aproximadamente 34.630"
do artigo (ver F1.10); o mapa de tempo (10:10) e a contagem de 12 slides estão coerentes.

---

## Prioridade sugerida (ordem de retorno sobre esforço)

1. **A.1** — corrigir o orientador nos 4 lugares (imprecisão factual, custo baixo).
2. **F2.1 / A.2** — SAM → SAM3 no artigo e na apresentação.
3. **F1.1** — figura `default × calibrado` (a evidência que falta).
4. **F1.2 / A.3** — reconhecer o tratamento composto do "45×1" (honestidade metodológica).
5. **F1.3 + F1.4** — definir medição de falsos positivos e incluir FPS no protocolo.
6. **F2.3 + F2.4 + F2.5** — ice_leke como rocha difícil, explicar ausência de light_spot, citar
   o split (tudo já está no projeto).
7. Restante (F1.6–F1.13, F2.2, F2.6, F2.7, A.4) — refino de texto.
