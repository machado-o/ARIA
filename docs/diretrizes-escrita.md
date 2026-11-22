# Diretrizes de Escrita — TCC ARIA

> Contrato de comportamento para a escrita do TCC em LaTeX (Overleaf, sincronizado via Git).
> Cláusulas numeradas. Em caso de conflito, **o que o Henrique disser na conversa vence.**
>
> Última atualização: 2026-11-22

---

## 1. Princípios de estilo

1.1. Português acadêmico (TCC brasileiro), **3ª pessoa**, voz ativa quando possível.

1.2. Sem emojis. Sem fórmulas de preenchimento ("neste capítulo veremos...", "resultados
satisfatórios foram obtidos").

1.3. Se a informação cabe em **tabela**, gerar tabela; se em **equação**, `\begin{equation}`;
se em **lista**, `itemize`/`enumerate`. Evitar parágrafo corrido onde o template prevê
estrutura. Ressalva: o corpo argumentativo (introdução, discussão) é prosa — listas servem
para fatos enumeráveis, não para substituir o raciocínio.

1.4. **Tempo verbal — o de TCC, não o de proposta.** O trabalho está feito: a metodologia vai
no presente ou no passado ("o limiar é escolhido pela regra", "o classificador foi treinado") e os
resultados, no passado ("obteve-se", "a segmentação identificou"). O futuro fica só para
*Trabalhos futuros*. Não misturar os dois para o mesmo fato. (Até 22/11/2026 esta cláusula pedia
a metodologia no futuro — regra do PD1, quando o texto era proposta.)

1.5. **Formatação numérica (pt-BR):** vírgula como separador decimal (mAP de 0,85; IoU de 0,72)
e ponto como separador de milhar (34.630 imagens). Unidades com espaço antes (60 FPS, 10 ms).

---

## 2. Fidelidade aos fatos (inegociável)

2.1. **Nunca inventar fatos sobre o sistema.** Métricas, configurações, resultados, detalhes
de arquitetura, nomes de classes — tudo vem dos `.md` de contexto (`decisoes.md`,
`arquitetura.md`, `dataset.md`) ou do Henrique.

2.1.1. **`apresentações/` NÃO é fonte de verdade** (**D13**). É saída desatualizada, escrita
antes das decisões atuais. Nunca copiar um fato de lá.

2.2. Se faltar um dado real (ex.: "descreva os resultados do YOLO" antes de existirem), **não
usar placeholder genérico**: inserir um `TODO` explícito e perguntar. Lacuna honesta > frase
vazia que soa bem.

2.3. Se algo que o modelo "sabe" sobre SAM/YOLO/CLIP/qualidade industrial conflitar com os
`.md` ou com o Henrique, **os `.md` e o Henrique vencem.**

2.4. Incertezas do sistema são parte do projeto. Surgindo algo não documentado, **perguntar** —
não resolver por conta própria.

2.5. **Tom: o texto não diminui o próprio trabalho** (pedido do Henrique, 19/11/2026). Limitação
entra como **escopo** ou **decisão de desenho**, em poucas linhas, e de preferência ligada a um
trabalho futuro, nunca como autocrítica ("o elo mais frágil", "o trabalho reconhece que...",
"não é demonstrado", "não foi possível"). Não se lista como limitação o que é escolha
deliberada (ex.: rotulagem binária, **D2**). Não se conta o que foi tentado e não deu certo quando
isso não muda nenhuma conclusão (ex.: "a opinião de especialista foi pedida e não veio"). O que
continua inegociável é a seção 2: nada se inventa, e um furo que mude uma conclusão é levado ao
Henrique para decidir junto, não resolvido em silêncio.

---

## 3. Escopo (ver `decisoes.md`)

3.1. **Aprendizado Ativo** (**D11**) e **rotulagem multi-classe** (**D12**) só aparecem em
**Trabalhos Futuros** — nunca como contribuição desta versão.

3.2. O eixo do trabalho é a **arbitrariedade da marcação manual** (**D3**), e a contribuição é
tornar esse critério explícito e parametrizado. **Não** escrever "reduzir falsos positivos" como
tese central — falso positivo é medido (**D7**), não é o enunciado.

3.3. São **dois** experimentos: os quatro braços do Professor — limiar único, regra por litologia
com todas as sondas, regra com as sondas do autor, limiar do autor (**D5**) — e Alunos especialistas ×
generalista × controle, estratificados por faixa de volume (**D6**). Nunca escrever "45
especialistas" sem a estratificação, nem afirmar que a comparação "isola a variável da
hierarquia" — é superafirmação, e o braço de controle existe justamente por causa disso.

3.4. As sondas (`crack`, `vein`...) **não são rótulos semânticos** (**D2**). Nunca escrever que o
sistema "identifica fissuras" ou "distingue veio de trinca" — ele marca regiões que responderam a
uma sonda.

3.5. Toda decisão metodológica citada no texto deve bater com `decisoes.md`. Em dúvida,
consultar lá antes de escrever.

---

## 4. Formato LaTeX

4.1. **O alvo é a monografia** (`apresentações/Overleaf/TCC/`): `iftex.cls` + `macros.tex` e
citações `abntex2-alf`. O artigo SBC de PD1 (`apresentações/Overleaf/artigo de PD1/`) foi entregue
em junho de 2026 e é saída antiga (**D13**); se algum dia voltar a ser editado, lembrar que ele usa
`sbc-template.sty` + `sbc.bst` e `\cite` — **nunca** `\citeonline` (é comando do `abntex2`; no SBC
gera "Undefined control sequence"). Saída sempre em **LaTeX puro** pronto pro Overleaf — sem markdown, sem blocos
` ```latex `.

4.2. Citações como `\cite{TODO-chave}` quando a referência ainda não existe no `.bib`; o
Henrique preenche depois (ou pedimos pra popular `bibliografia.bib`).

4.3. Fórmulas e métricas (mAP, IoU, FPS) viram `\begin{equation}` formal.

4.4. Antes de escrever uma seção nova, conferir o trecho correspondente da monografia
(`apresentações/Overleaf/TCC/textuais/`, `apresentações/Overleaf/TCC/pre_textuais/`) para casar
com a estrutura existente.

4.5. **Mecânica de citação na monografia (abntex2-alf, autor-data):** usar `\citeonline{chave}` quando o autor
é sujeito da frase ("segundo \citeonline{...}, ...") e `\cite{chave}` para citação parentética
ao fim da ideia. Citação direta com mais de três linhas vai em ambiente de recuo, sem aspas; até
três linhas, entre aspas no corpo. Enquanto a referência não existe no `.bib`, usar
`\cite{TODO-chave}` (ver 4.2).

4.6. **Floats sempre completos:** toda figura, tabela ou quadro deve ter `\caption` descritiva,
`\label` no padrão (`fig:`, `tab:`, `quad:`, `eq:`), ser **referenciada no texto** antes de
aparecer ("a Figura \ref{...} ilustra...") e indicar a **fonte** via `\source`/`\legend`
(ABNT — "Fonte: elaborado pelo autor" quando própria). Nenhum float órfão.

    ⚠️ No `iftex.cls`, o `\legend{#1}` já imprime "Fonte: #1." — escrever
    `\legend{elaborado pelo autor}` (ou `\legend{elaborado pelo autor. Nota: ...}`), nunca
    `\legend{Fonte: ...}`, que sai "Fonte: Fonte: ...". Corrigido no texto em 06/11/2026.

---

## 5. Fluxo de trabalho

Para cada pedido de escrita:

5.1. Confirmar em 1–2 linhas **o que entendi** que vou escrever.

5.2. Listar dúvidas em aberto, se houver, e esperar resposta — ou o OK explícito.

5.3. Só então produzir o LaTeX. Se o pedido for vago ("escreva a introdução"), fazer 5.1–5.2 e
esperar. **Não despejar texto.**

---

## 6. Transparência de edição (preferência do Henrique)

6.1. **Todo edit no `.tex` vem acompanhado de um resumo explícito do que mudou** — qual
parágrafo foi reescrito, qual seção foi adicionada/removida, o que foi realinhado.

6.2. Em dias que o Henrique pedir, detalhar frase a frase. **No mínimo, sempre um resumo** —
nunca uma edição silenciosa.

6.3. Como a sincronia Overleaf↔Git é bidirecional: se o Henrique editou um arquivo no Overleaf,
ele dá `pull` antes; evitar editar o mesmo arquivo dos dois lados ao mesmo tempo (conflito de
merge).

---

## 7. Terminologia, siglas e estrangeirismos

7.1. **Terminologia canônica:** o termo padrão para os defeitos superficiais é **"anomalia"**.
"Irregularidade" e "avaria" podem ser usados pontualmente para evitar repetição, mas "anomalia"
é a referência — não tratar "defeito"/"avaria"/"anomalia" como conceitos distintos sem
necessidade. (O título provisório, de 19/11/2026, já usa "anomalias"; o título final ainda está
em aberto — ver `pendencias.md`.)

7.2. **Nomenclatura (D1):** **ARIA** nomeia o pipeline/método, e é o único nome de sistema no
texto. O projeto é isolado — **nenhuma** menção a plataforma, produto ou empresa.

7.3. **Siglas:** definir por extenso na primeira ocorrência, com a sigla entre parênteses —
"Redes Neurais Convolucionais (CNN)" — e usar só a sigla depois. Na monografia, registrar cada
sigla em `apresentações/Overleaf/TCC/pre_textuais/siglas.tex` (o artigo SBC não usa
lista de siglas).

7.4. **Estrangeirismos:** termos em língua estrangeira sempre em itálico (`\textit{}`) —
\textit{Deep Learning}, \textit{pseudo-labels}, \textit{crack}, \textit{Edge Computing}.

---

## 8. Onde está a verdade

| Preciso de... | Olhar em |
|---|---|
| Decisão fechada, hipóteses, experimentos, métricas | `decisoes.md` |
| Como o sistema funciona (técnico) | `arquitetura.md` |
| Dados, litologias, faixas de volume, sondas | `dataset.md` |
| Estado atual / próximos passos | `roadmap.md` |
| Coisas pendentes a corrigir/escrever | `pendencias.md` |
