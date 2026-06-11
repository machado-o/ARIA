# Diretrizes de Escrita — TCC ARIA

> Contrato de comportamento para a escrita do TCC em LaTeX (Overleaf, sincronizado via Git).
> Cláusulas numeradas. Em caso de conflito, **o que o Henrique disser na conversa vence.**
>
> Última atualização: 2026-06-10

---

## 1. Princípios de estilo

1.1. Português acadêmico (TCC brasileiro), **3ª pessoa**, voz ativa quando possível.

1.2. Sem emojis. Sem fórmulas de preenchimento ("neste capítulo veremos...", "resultados
satisfatórios foram obtidos").

1.3. Se a informação cabe em **tabela**, gerar tabela; se em **equação**, `\begin{equation}`;
se em **lista**, `itemize`/`enumerate`. Evitar parágrafo corrido onde o template prevê
estrutura.

---

## 2. Fidelidade aos fatos (inegociável)

2.1. **Nunca inventar fatos sobre o sistema.** Métricas, configurações, resultados, detalhes
de arquitetura, nomes de classes — tudo vem dos `.md` de contexto (`arquitetura.md`,
`dataset.md`, `pontos_tcc.md`, `decisoes.md`) ou do Henrique.

2.2. Se faltar um dado real (ex.: "descreva os resultados do YOLO" antes de existirem), **não
usar placeholder genérico**: inserir um `TODO` explícito e perguntar. Lacuna honesta > frase
vazia que soa bem.

2.3. Se algo que o modelo "sabe" sobre SAM/YOLO/CLIP/qualidade industrial conflitar com os
`.md` ou com o Henrique, **os `.md` e o Henrique vencem.**

2.4. Incertezas do sistema são parte do projeto. Surgindo algo não documentado, **perguntar** —
não resolver por conta própria.

---

## 3. Escopo (ver `decisoes.md`)

3.1. **Aprendizado Ativo** (D8) e **rotulagem multi-classe** (D9) só aparecem em **Trabalhos
Futuros** — nunca como contribuição desta versão.

3.2. O experimento central é **45 especialistas × 1 generalista** (D3) — é o eixo da
metodologia e dos resultados.

3.3. Toda decisão metodológica citada no texto deve bater com `decisoes.md`. Em dúvida,
consultar lá antes de escrever.

---

## 4. Formato LaTeX

4.1. Saída em **LaTeX puro** pronto pro Overleaf — sem markdown, sem blocos ` ```latex `. Usar
os comandos/ambientes do template (`iftex.cls`, macros em `macros.tex`).

4.2. Citações como `\cite{TODO-chave}` quando a referência ainda não existe no `.bib`; o
Henrique preenche depois (ou pedimos pra popular `bibliografia.bib`).

4.3. Fórmulas e métricas (mAP, IoU, FPS) viram `\begin{equation}` formal.

4.4. Antes de escrever uma seção nova, conferir o trecho correspondente do template
(`Overleaf/textuais/`, `pre_textuais/`, etc.) para casar com a estrutura existente.

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

## 7. Onde está a verdade

| Preciso de... | Olhar em |
|---|---|
| Decisão metodológica fechada | `decisoes.md` |
| Como o sistema funciona (técnico) | `arquitetura.md` |
| Dados, classes, anomalias | `dataset.md` |
| Argumento acadêmico, hipótese, métricas, capítulos | `pontos_tcc.md` |
| Estado atual / próximos passos | `../ROADMAP.md` |
| Coisas pendentes a corrigir/escrever | `../PENDENCIAS.md` |
