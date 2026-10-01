# Pendências — ARIA

> Caixa de entrada de itens soltos. Marcos de desenvolvimento ficam no
> [`roadmap.md`](roadmap.md); decisões fechadas, em [`decisoes.md`](decisoes.md).
>
> Consolida o que antes estava espalhado em `auditoria.md`, `revisao-artigo.md` e
> `artigo-sbc.md` (os três foram removidos em 2026-08-23).
>
> Última atualização: 2026-09-26

---

## 🔴 Bloqueadores — dependem do Henrique

- [ ] **Confirmar a data real de entrega/defesa com o Rafael.** Em 26/09/2026 o Henrique passou
  **15/10/2026** como estimativa ("deve ser até dia 15"), e o plano passou a usar essa data. Ela
  **não veio do orientador** — enquanto não for confirmada, todo o cronograma está apoiado numa
  suposição. É a pendência mais barata de resolver e a que mais muda o plano: uma mensagem.
- [ ] **Confirmar se o DeepStoneAI usou este mesmo dataset.** Se sim, vira citação obrigatória.
- [ ] **Contato do especialista do setor** para a preferência pareada cega (D7). Precisa de ~30
  minutos dele, não mais.
- [ ] **Versão final submetida ao Latinoware** — o `main.tex` do repo diverge do que foi enviado
  ao JEMS. Henrique envia quando sair o resultado (14/09).

---

## 🧩 Código

> ✅ Os três bugs de desbloqueio (**Fase 0**) foram corrigidos e verificados em 2026-08-23.

- [ ] **➡️ PRÓXIMA AÇÃO — calibrar `siena_white` no calibrador.** As 4 vagas estão selecionadas
  e o cache das 6 sondas já está capturado; é só abrir e decidir. É o gargalo de tudo o que vem
  depois: sem uma litologia calibrada de verdade não dá para fechar a regra de limiar, e sem a
  regra não dá para calibrar as outras 44.
  `cd AI/SAM && .venv\Scripts\python.exe -m streamlit run calibrator.py`
- [ ] **Selecionar as 4 imagens das outras litologias da faixa A** (**D17**). Estado: **4 de 180
  vagas** — `siena_white` 4/4, faltam **40 vagas** na faixa A. `python rock_viewer.py` conduz na
  ordem certa.
- [x] ~~**Terminar o `calibrator.py`**~~ — feito em 2026-09-26: 3 abas (descoberta / limiar /
  fechar), um slider com as 4 previews simultâneas sobre o cache do `sam_cache.py`, curva de
  limiar com o joelho marcado como sugestão, e critério de texto obrigatório para salvar.
- [ ] **Fechar a regra de limiar** (TODO da **D17**): escolher entre (a) baseada em anotação e
  (b) joelho validado pelo ouro, e fixar o parâmetro. Depende da `siena_white` calibrada.
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
