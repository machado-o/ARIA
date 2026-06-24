# Artigo SBC — entrega PD1

> Artigo científico no template **SBC**, entrega de **Projeto de Diplomação I (PD1)**.
> Distinto da monografia do TCC. Fonte da verdade técnica/metodológica continua nos demais
> `.md` (`decisoes.md`, `arquitetura.md`, `dataset.md`, `pontos-tcc.md`); aqui mora só o que é
> específico desta entrega.
>
> Última atualização: 2026-06-24

---

## O que é

Artigo de 10–12 páginas consolidando Proposta, Fundamentação teórica, Metodologia e Resultados
iniciais do ARIA, mais apresentação. Autor: **Henrique Machado de Oliveira**; orientador (PD1):
**Everson Scherrer Borges**. Conteúdo portado/condensado do `Overleaf/TCC/textuais/Texto Inicial.tex`
e dos `docs/*.md` — a verdade do projeto está nos `.md`, não no `.tex` antigo.

## Onde mora

```
Overleaf/artigo/
├── main.tex          # o artigo (article 12pt, sbc-template)
├── referencias.bib   # bibliografia consolidada (32 refs reais)
├── sbc-template.sty  # estilo SBC
├── sbc.bst           # estilo de bibliografia SBC
└── figuras/          # 6 imagens da demo ice_leke
```

A monografia do TCC vive em paralelo em `Overleaf/TCC/` (template IFES, `iftex.cls`). As duas
entregas convivem no mesmo projeto Overleaf, sincronizado com o GitHub (`machado-o/ARIA`, branch
`main`).

## Gotchas do template SBC (não redescobrir)

- **`\citeonline` NÃO existe no SBC** — é comando do `abntex2` (monografia). No artigo, usar só
  `\cite{...}` (parentético) ou escrever o nome do autor no texto. `\citeonline` causa "Undefined
  control sequence".
- **Sem ambiente de keywords** — o `sbc-template.sty` só define `abstract` e `resumo`. Keywords
  não são exigidas; foram **removidas** porque estouravam o limite de **10 linhas** do
  abstract/resumo. Se um evento exigir, readicionar manualmente.
- **Legendas:** regra SBC = curta centralizada, **multilinha justificada** (0,8 cm). É o padrão do
  `sbc-template`; **não** forçar `\captionsetup{justification=centering}`. Fonte da legenda
  (Helvetica 10pt bold) já vem do estilo.
- **Sem linha "Fonte:"** nas legendas (isso é ABNT, não SBC). Figuras próprias do autor são
  atribuídas no texto (ex.: "A Figura X, elaborada pelo autor, ...").
- **Bloco de autor:** Henrique e Everson lado a lado, sem rótulo "Orientador:"; ambos com
  `\inst{1}`; e-mails dos dois no `\email{}`. Endereço usa "--" (en-dash), padrão do template.
- **Limites:** abstract e resumo ≤ 10 linhas cada, na 1ª página. As **referências contam** no
  limite de 10–12 páginas.
- **Não há LaTeX local** — compilar no Overleaf. Em conflito de sync, o GitHub é a fonte da
  verdade; o mais limpo é reimportar do GitHub.

## Estrutura atual

Introdução (contexto+valor / problema / proposta / pergunta / objetivos / organização) ·
Fundamentação (CNN, segmentação, SAM, Teacher-Student, YOLO, Indústria 4.0) · Trabalhos
Relacionados (AVI por setor / rochas / lacuna) · Metodologia (tipo de pesquisa, conjunto de dados,
calibração do SAM por litologia, protocolo experimental 45×1, avaliação, ferramentas) · Resultados
Iniciais (DeepStoneAI — Xception 99,21% — e demo SAM ice_leke) · Considerações Parciais.

Floats: 3 figuras (arquitetura em TikZ, ice_leke combinado, ice_leke decomposto) + 4 tabelas
(anomalias, calibração por grupo, arquiteturas DeepStoneAI, e a do protocolo se aplicável).

## Status

Estrutura e conteúdo completos e em conformidade com o template. Em ~11 páginas. Refino de texto
em andamento com o Henrique. Pendências soltas → `pendencias.md`.
