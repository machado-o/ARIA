# Pendências — ARIA

> Caixa de entrada de itens soltos. Marcos de desenvolvimento ficam no
> [`roadmap.md`](roadmap.md); decisões fechadas, em [`decisoes.md`](decisoes.md).
>
> Consolida o que antes estava espalhado em `auditoria.md`, `revisao-artigo.md` e
> `artigo-sbc.md` (os três foram removidos em 2026-08-23).
>
> Última atualização: 2026-08-23

---

## 🔴 Bloqueadores — dependem do Henrique

- [ ] **Confirmar a data real de entrega/defesa com o Rafael.** Hoje o plano assume 01/10 como
  entrega final (cenário mais apertado). Se for só a prévia, a Fase 2 ganha fôlego.
- [ ] **Confirmar se o DeepStoneAI usou este mesmo dataset.** Se sim, vira citação obrigatória.
- [ ] **Contato do especialista do setor** para a preferência pareada cega (D7). Precisa de ~30
  minutos dele, não mais.
- [ ] **Versão final submetida ao Latinoware** — o `main.tex` do repo diverge do que foi enviado
  ao JEMS. Henrique envia quando sair o resultado (14/09).

---

## 🧩 Código

> ✅ Os três bugs de desbloqueio (**Fase 0**) foram corrigidos e verificados em 2026-08-23.

- [ ] **Selecionar as 4 imagens da faixa A** (**D17**). `selectRocks/` foi zerado: **0 de 180
  vagas**, sendo 44 da faixa A. `python rock_viewer.py` conduz na ordem certa.
- [ ] **Terminar o `calibrator.py`** — mostrar as 4 vagas lado a lado e escolher o limiar pelo
  conjunto. Núcleo pronto e testado em `sam_cache.py`; falta a interface. Fazer **depois** da
  primeira litologia completa, para construir contra dados reais.
- [ ] **Fixar o X da regra de limiar** (TODO da **D17**) depois da primeira litologia.

---

## ✍️ Escrita — aplicar quando revisarmos `Overleaf/` (D13)

> ⚠️ Nada aqui é urgente **agora**. `Overleaf/`, `LatinoWare2026/` e `apresentacao/` só serão
> revisados depois que `docs/` estiver estável. Esta lista existe para não perder o que já foi
> diagnosticado.

### Erros factuais

- [ ] **Orientador errado no artigo SBC** — `Overleaf/artigo/main.tex:17` e `:22` ainda listam
  Everson Scherrer Borges. Rafael Silva Guimarães orienta a pesquisa. Diagnosticado em 01/07.
- [ ] **Ficha catalográfica contradiz o próprio arquivo** — `Overleaf/TCC/macros.tex:43` cita
  "Borges, Everson Scherrer" enquanto o `\orientador` na linha 17 já é Rafael. E as tags são do
  template (Criptografia, IoT, Nuvem).
- [ ] **"Constituir e pré-processar um banco de imagens"** — o autor não constituiu o banco
  (D9). Trocar por "selecionar, caracterizar e pré-processar um conjunto público".
- [ ] **O artigo nunca diz "SAM3"** — 25 ocorrências de "SAM", zero de "SAM3", citando o paper do
  SAM v1 (2023), que é outro modelo. O short paper do Latinoware **já está correto**; é portar de
  volta. Mesma correção nos slides 5, 6, 7 e 10.
- [ ] **Typo no título** — "Redes Neurais **Convulacionais**" (`macros.tex:3`) → Convolucionais.
- [ ] **`\approvaldate{01}{Agosto}{2026}`** já passou. `\local{Cachoeiro de itapemirim}` em
  minúscula. `\palavraschave` ainda é "Palavra Chave 1".

### Alinhar com as decisões novas

- [ ] **O argumento do veio natural sai** (D3) — o texto diz que o ARIA existe para evitar que um
  veio vire defeito, o que contradiz o código (a sonda `vein` está ativa em tudo). O eixo passa a
  ser a arbitrariedade da marcação manual.
- [ ] **"45 especialistas" vira estratificação por faixa** (D6), e "a comparação isola exatamente
  a variável da hierarquia" sai — é superafirmação (o braço de controle é a correção).
- [ ] **Purgar todas as menções ao Hartheus** (D1) nas três pastas.
- [ ] **A justificativa do colapso binário muda** (D2) — de "os embeddings do CLIP não são
  confiáveis" para "as sondas são chaves de recall, não rótulos semânticos".
- [ ] **Arrancar TAM / Difusão de Inovações / Teoria Sociotécnica** (**D16**) da monografia
  (subseção "Automação e Sistemas de Informação no Setor de Rochas") e do artigo (subseção
  "Adoção Tecnológica e Indústria 4.0").
- [ ] **Nenhum texto pode afirmar "calibração por litologia" nem "por grupo cromático"** enquanto
  a D15 não for fechada.
- [ ] **mAP "sobre N classes" contradiz a rotulagem binária.** Com uma classe, mAP = AP.
  Esclarecer o que é N.

### Trabalhos Relacionados — lacuna a reposicionar

- [ ] **Citar e se posicionar contra `Boxes2Pixels: Learning Defect Segmentation from Noisy SAM
  Masks`** (Lendering, Akdag e Bondarev — arXiv:2604.11162). Faz exatamente SAM → pseudo-rótulos →
  Aluno para segmentação de defeitos industriais, com estratégias de tratamento de ruído de
  máscara. **Não** faz condicionamento de prompt por litologia e **não** é no domínio de rochas
  ornamentais — a contribuição do ARIA sobrevive, mas fica mais estreita. A afirmação de "lacuna
  na literatura" precisa ser reescrita para não ser derrubada pela banca.
- [ ] Ancorar a discussão de limiar em literatura de pseudo-rotulagem (Soft Teacher, Unbiased
  Teacher): o consenso é limiar **alto** / viés de precisão, porque a rede memoriza rótulo errado.
  Ver `decisoes.md` D17.

### Refino de texto (baixa prioridade)

- [ ] Abstract (EN) cita "the *ice leke* lithotype"; o resumo (PT) omite. Devem ser fiéis.
- [ ] Caixa inconsistente: "Stain"/"stain", "Dark patches"/"dark patches", nas três pastas.
- [ ] "aproximadamente 34.630 imagens" — ou "~34.600", ou o número exato sem "aproximadamente".
- [ ] Tabela 1 lista 5 sondas, a Figura 3 mostra 4. Falta explicar: `ice_leke` é rocha clara, e
  rochas claras usam `Dark patches`, não `light spot`.
- [ ] Dizer **por que `ice_leke`**: é textura fora do padrão (`dataset.md`), o que transforma a
  demo em teste de estresse deliberado em vez de escolha arbitrária. Vale registrar também que
  ela está na **faixa D** (113 imagens) — é uma das mais pobres do dataset.
- [ ] Mencionar o split train/val/test — um protocolo experimental precisa dizer como particiona.
- [ ] Mencionar `rock_viewer.py` e `calibrator.py`: dá concretude ao "calibrar iterativamente".
- [ ] Atribuir ao paper do CLIP o achado de que prompts contextuais superam palavras isoladas —
  hoje aparece como hipótese dos autores.
- [ ] Mostrar **um** caso em que a segmentação falhou. Seção de resultados só com acertos reduz
  credibilidade.
- [ ] Título usa "avarias"; o termo canônico do projeto é "anomalia" (`diretrizes-escrita.md`
  §7.1). Há 4 títulos alternativos comentados em `macros.tex`.

### Monografia — estrutura

- [ ] **`Overleaf/TCC/main.tex` está com quase tudo comentado**: capa, ficha, resumo, sumário,
  introdução, referencial e conclusão. Só entra `Texto Inicial.tex`.
- [ ] **`introducao.tex`, `ref_teorico.tex` e `conclusao.tex` ainda contêm o texto-instrução do
  template** ("Na introdução deve-se fazer a contextualização...").
- [ ] **`bibliografia.bib` tem 0 bytes** e é o arquivo que o `main.tex` carrega — nenhuma
  referência compila. As 32 referências reais estão em `Overleaf/artigo/referencias.bib`.
- [ ] Escrever resumo (PT) e abstract (EN) reais — hoje são o texto do template.
- [ ] Escrever Trabalhos Futuros contemplando D11 e D12.
- [ ] Deletar `Overleaf/TCC/textuais/testes.tex` (demo do template).
- [ ] Inserir a figura de arquitetura (placeholder em `\label{fig:arquitetura_hartheus}` — o
  próprio nome do label precisa mudar, D1).

---

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
