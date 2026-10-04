# Pendências — ARIA

> Caixa de entrada de itens soltos. Marcos de desenvolvimento ficam no
> [`roadmap.md`](roadmap.md); decisões fechadas, em [`decisoes.md`](decisoes.md).
>
> Consolida o que antes estava espalhado em `auditoria.md`, `revisao-artigo.md` e
> `artigo-sbc.md` (os três foram removidos em 2026-08-23).
>
> Última atualização: 2026-10-02

---

## 🔴 Bloqueadores — dependem do Henrique

- [ ] **Confirmar a data real de entrega/defesa com o Rafael.** Em 26/09/2026 o Henrique passou
  **15/10/2026** como estimativa ("deve ser até dia 15"), e o plano passou a usar essa data. Ela
  **não veio do orientador** — enquanto não for confirmada, todo o cronograma está apoiado numa
  suposição. É a pendência mais barata de resolver e a que mais muda o plano: uma mensagem.
- [x] ~~**Confirmar se o DeepStoneAI usou este mesmo dataset.**~~ — sim, confirmado em
  2026-10-02 pelo artigo do SBAI (**D9**). Citação obrigatória.
- [ ] **Contato do especialista do setor** para a preferência pareada cega (D7). Precisa de ~30
  minutos dele, não mais.
- [ ] **Versão final submetida ao Latinoware** — o `main.tex` do repo diverge do que foi enviado
  ao JEMS. Henrique envia quando sair o resultado (14/09).

---

## 🧩 Código

> ✅ Os três bugs de desbloqueio (**Fase 0**) foram corrigidos e verificados em 2026-08-23.

- [x] ~~**Calibrar `siena_white` no calibrador**~~ — feito em 2026-10-01 (`calibracao.json`).
  Primeira litologia calibrada de fato: **1 de 45**. Entraram 3 sondas — `vein`, `Stain` e
  `Dark patches`.
- [ ] **Observar: o autor divergiu da regra nas 3 sondas da `siena_white`**, e sempre para cima
  (limiar de trabalho ≈ 2× o joelho: `vein` 0,145 → 0,335; `Stain` 0,203 → 0,414;
  `Dark patches` 0,235 → 0,397). Critério escrito: subir até a vaga típica parar de marcar matriz
  limpa. Uma litologia não é padrão, mas se a divergência se repetir na faixa A é o achado que a
  **D17** prevê (*"onde a curva engana"*) — e a direção bate com o "na dúvida, cortar mais
  apertado".
- [ ] **➡️ PRÓXIMA AÇÃO — selecionar as 4 imagens das outras litologias da faixa A** (**D17**).
  Estado: **16 de 180 vagas** — `siena_white` 4/4, `nevada_black` 4/4 (02/10), `ubatuba_green`
  4/4 e `ipanema_beige` 4/4 (03/10), as três últimas a calibrar; faltam **28 vagas** na faixa A.
  **`shadow_white` foi pulada em 03/10**: é difícil julgar o que é defeito nela, e o Henrique vai
  pedir ajuda na faculdade. Enquanto isso, a seleção segue em `itaunas_white` — o `rock_viewer.py`
  sem argumento para sempre na `shadow_white`, então chamar pelo nome
  (`rock_viewer.py itaunas_white`).
- [ ] **Decidir o que fazer com o resultado do Xception no `test/`** (**D19**, 03/10/2026).
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
- [x] ~~**Rever a vaga típica de `nevada_black`, `ubatuba_green` e `ipanema_beige`**~~ — revista
  em 2026-10-03. A típica tinha sido escolhida, em algumas, como "chapa com defeito em quantidade
  média"; a regra é a chapa **mais comum** da rocha, limpa se a rocha costuma ser limpa. É ela
  que impede o limiar de descer demais, porque mostra se ele marca matriz limpa. Revisão: só a
  `ubatuba_green` mudou (`train/175` → `train/2031`); nas outras duas a maioria das chapas tem
  mesmo algum defeito, e a escolha já seguia a regra. Para refazer uma vaga: apagar o arquivo
  dela e rodar `rock_viewer.py <rocha>`, que reabre só a vaga vazia.
- [x] ~~**Terminar o `calibrator.py`**~~ — feito em 2026-09-26: 3 abas (descoberta / limiar /
  fechar), um slider com as 4 previews simultâneas sobre o cache do `sam_cache.py`, curva de
  limiar com o joelho marcado como sugestão, e critério de texto obrigatório para salvar.
- [x] ~~**Fechar a regra de limiar**~~ — fechada em 2026-09-26 na **D17**: opção (b), joelho da
  curva em escala log, sem parâmetro livre.
- [ ] **Decidir o que fazer com a ponte entre contornos do `masks.xyn`** — medição e opções em
  `roadmap.md` → Fase 3.0. Decisão metodológica, não de código.

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
  e o orientador certo; `\local`, `pprovaldate` e palavras-chave preenchidos.
- [x] TAM / Difusão de Inovações / Teoria Sociotécnica **fora** (**D16**) — as três entradas
  ficaram no `.bib` sem citação, o que o bibtex simplesmente ignora.
- [x] Boxes2Pixels citado e posicionado (§2.7) sem alegar lacuna na literatura.
- [x] "Constituir o banco" → "selecionar, caracterizar e pré-processar um conjunto público"
  (**D9**); mAP explicado como AP por causa da classe única (**D2**).

### 🟡 Monografia — em aberto

- [ ] **Citar e posicionar o TCC do Pedro Lucas Brito Moreira** (IFES, 2025, *Redes Neurais
  Convolucionais para Segmentação e Classificação de Rochas Ornamentais*, **mesmo orientador**).
  É o trabalho mais próximo do ARIA: mesmo dataset, Xception (99,21%) + YOLO de segmentação de
  defeitos com **anotação manual** e 4 classes semânticas, métricas modestas por ruído de
  anotação. O ARIA responde exatamente a esse ponto — Professor (SAM3) no lugar da anotação
  manual, critério parametrizado (**D3**), rótulo binário (**D2**). Material em
  `Projects/ARIA - Análise e Reconhecimento Inteligente de Anomalias/DeepStoneAI/`; entrada do
  `.bib` ainda não criada. Também citar o artigo do SBAI 2025 (**D9**).
  - **Números para a motivação (D3)** — vêm do **FracStoneAI** (a etapa YOLO desse trabalho,
    com artigo na LatinoWare 2026; repo em `…/FracStoneAI-main/`): YOLO11-seg sobre anotação
    manual de 4 classes em **1.088 imagens deste mesmo dataset** (conferido por hash) deu
    **mask mAP50-95 de 0,04 a 0,21**; os próprios autores apontam ruído de rótulo e defeitos
    omitidos na anotação. É o problema que o ARIA ataca, medido por um trabalho vizinho —
    usar na introdução para responder de antemão *"por que não anotar à mão e treinar o
    YOLO?"*. Fonte dos números: `docs/NEXT-STEPS.md` e `docs/Latinoware2026/Artigo/` do repo.

- [ ] **`\cite{TODO-sam3}`** em `ref_teorico.tex`: falta a referência do **SAM3**. É a única
  citação sem entrada no `.bib`.
- [ ] **Conferir a entrada `boxes2pixels_lendering2026`** — foi montada a partir do registro
  neste arquivo, não de consulta à fonte. Confirmar autores, título e número do arXiv.
- [ ] **Figura da arquitetura** — o bloco está comentado em `metodologia.tex` de propósito
  (`\includegraphics` de arquivo inexistente interrompe a compilação). Gerar a imagem, pôr em
  `figuras/` e descomentar.
- [ ] **Resumo e abstract:** acrescentar as frases de resultado e conclusão quando os
  experimentos rodarem.
- [ ] **Conclusão §5.1:** sintetizar H1 e H2 — inclusive se o resultado for negativo.
- [ ] **Banca:** `macros.tex` ainda tem "Fulana/Cicrano de Tal"; a aprovação está comentada.
- [ ] **Dedicatória, agradecimentos e epígrafe** continuam com texto do template, comentados.
- [ ] **Compilar no Overleaf.** Não há LaTeX nesta máquina — a conferência feita aqui é
  estrutural (`TCC/verificar_tex.py`: citação sem entrada, `ef` sem `\label`, ambiente
  desbalanceado, figura ausente), **não** é compilação.

### 🔴 Artigo de PD1 e LatinoWare2026 — nada feito

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

- [ ] **`LatinoWare2026/artigo-overleaf.zip`** — 5,8 MB de binário versionado duplicando o que já
  está extraído ao lado. Zip não tem diff útil e infla o histórico.
- [ ] **`LatinoWare2026/Exemplo_do_IEEE_adaptado_para_o_Latin_Science_2026 (1)/`** — o `" (1)"` é
  marca de download repetido. É template de referência; renomear ou remover.
- [ ] **Três pastas chamadas "artigo"** sem distinção no nome (SBC, IEEE, template cru).
- [ ] Convenção de nomes inconsistente no topo: `AI`, `docs`, `Overleaf`, `apresentacao`,
  `LatinoWare2026`.

---

## ✅ Resolvido em 2026-08-23

- Hartheus removido do repositório (D1); `Hartheus.md` deletado.
- `pontos-tcc.md` fundido em `decisoes.md`; `diretrizes-implementacao.md` fundido no `CLAUDE.md`;
  `auditoria.md`, `revisao-artigo.md` e `artigo-sbc.md` consolidados aqui.
- `CLAUDE.md` corrigido: afirmava que `rock_prompts.json` e `selectRocks/` eram gitignored (não
  são, estão versionados) e citava um typo `whte_liberdade` que não existe mais.
- Contagem do dataset corrigida em `dataset.md`: são **14** litologias com <200 imagens, não 7.
- `apresentacao/roteiro.md` já estava com o orientador correto — o item estava desatualizado nas
  listas antigas.
- Ausência de definição operacional de falso positivo → resolvida por **D7**.
- "A calibração nunca foi demonstrada" → vira o **Experimento 1** (D5).
- "45×1 confunde duas variáveis" → resolvido pelo braço de controle (**D6**).
- "Suficiência de dados por especialista não é discutida" → virou **variável do experimento** (D6).
- Falta de statement de reprodutibilidade → resolvida por dataset público (**D9**).
