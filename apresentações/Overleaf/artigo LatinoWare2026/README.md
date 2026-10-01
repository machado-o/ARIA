# Latin.Science 2026 — submissão do ARIA

> Trilha acadêmica do **23º Latinoware** (8ª edição do Latin.Science).
> Levantamento feito em **2026-08-14**. Fonte: <https://latinoware.org/latinscience2026/>

---

## Datas (o primeiro prazo de cada linha é o original, riscado no site; o segundo é o vigente)

| Etapa                                                    | Prazo vigente                       |
| -------------------------------------------------------- | ----------------------------------- |
| Submissão do artigo (JEMS3)                             | **14/08/2026 — *hard deadline***  |
| Notificação aos autores                                 | 14/09/2026                          |
| Versão final + Termo de Autorização de Publicação    | 02/10/2026                          |
| Apresentação (presencial)                               | 14–16/10/2026                      |

Local: Grand Carimã Resort & Convention Center, Foz do Iguaçu (PR).
Submissão: **JEMS3** — <https://jems3.sbc.org.br/latin.science> · contato: latin.science@latinoware.org
Anais publicados no **portal SOL/SBC**.

## Modalidades

| Modalidade      | Páginas | Definição do CFP                                                                 |
| --------------- | -------- | ---------------------------------------------------------------------------------- |
| **Full paper**  | 6–10    | "trabalhos **concluídos** sobre pesquisas realizadas"                            |
| **Short paper** | 3–4     | "trabalhos **ainda não concluídos**, com ideias relevantes e resultados preliminares" |

## Decisão: **short paper**

O ARIA está em andamento — 1 das 45 litologias calibrada, validação qualitativa, sem mAP/IoU, hipótese central (H1) ainda não testada. Isso é, literalmente, a definição de short paper do evento. O full paper fica para quando existir a comparação quantitativa 45×1.

## Regras que valem para a submissão

- **Revisão cega**: nada de nomes, afiliações ou e-mails no PDF submetido. Autores entram só na versão final.
- **Idioma**: português, espanhol ou inglês. Se PT/ES, exige-se **abstract em inglês + resumo no idioma do texto**, e os títulos dos elementos obrigatórios traduzidos.
- **Seções obrigatórias**: Título, Abstract, Palavras-chave, Introdução, (outras seções), **Resultados e Discussão**, **Conclusões**, **Agradecimentos**, **Referências** (+ **Resumo** se em PT).
- **Declaração sobre uso de IA generativa** — obrigatória, conforme Portaria CNPq nº 2.664/2026.
- **Formato**: PDF, template oficial. Times New Roman 10, A4, margens: superior 2 cm, inferior 2,5 cm, laterais 1,6 cm (o `IEEEtran` do template já resolve isso; o `geometry` do preâmbulo é o que gera o espaço do cabeçalho — **não mexer**).
- **Tópicos de interesse** cobertos: IA e Machine Learning, Desenvolvimento de Software, Tecnologias Emergentes, Segurança, Governança de TI, Inclusão Digital, Open Hardware, Games.

## Arquivos

```
LatinoWare2026/
├── README.md                                   ← este arquivo
├── Exemplo_do_IEEE_adaptado_para_o_Latin_Science_2026 (1)/   ← template original baixado do site
└── artigo/                                     ← a submissão
    ├── main.tex          # short paper, IEEEtran 10pt conference, versão CEGA
    ├── referencias.bib   # herdado de Overleaf/artigo/
    ├── IEEEtran.cls, IEEEtran.bst
    ├── headerimg.png, footerimg.png
    └── figs/             # figuras da demo ice_leke + logo2026
```

O artigo do PD1 (template SBC, ~11 páginas) continua intacto em `Overleaf/artigo/` — esta é uma versão derivada e condensada, não uma substituição.

## Chave de anonimização (cega ↔ final)

Uma linha só controla as duas versões, em `main.tex`:

```latex
\finalfalse   % versão CEGA — é esta que vai para o JEMS
\finaltrue    % versão FINAL — pós-aceite, restaura tudo
```

O que a chave alterna, via o comando `\blind{<cego>}{<final>}`:

| Local                        | Versão cega                     | Versão final                                       |
| ---------------------------- | -------------------------------- | --------------------------------------------------- |
| Bloco de autor               | "ID do artigo Latin.Science: …" | nomes, afiliação e e-mails                         |
| Introdução (§I)             | omitido                          | "…núcleo inteligente da plataforma industrial Hartheus" |
| Trabalhos Relacionados (§II) | omitido                          | "…ambos desenvolvidos no mesmo campus desta pesquisa" |
| Agradecimentos               | só o título + nota de omissão | texto real (Ifes Campus Cachoeiro + empresas do setor) |

Para anonimizar um trecho novo, envolva com `\blind{}{texto que só aparece na versão final}` — não apague o texto.

## Gotchas do template IEEE do Latin.Science

- O `\iffinal` do template original chama `\cmtid` **sem defini-lo** — quebra a compilação na versão cega. Em `main.tex` o comando já está definido; basta preencher com o ID do JEMS.
- `\DeclareGraphicsExtensions` do template não inclui `.jpg` — corrigido em `main.tex` (as figuras da demo são JPG).
- O template não carrega `babel`; sem ele a hifenização sai com padrões do inglês. `main.tex` carrega `[brazil]{babel}`, o que **inverte o rótulo do primeiro abstract** — por isso há um `\renewcommand{\abstractname}{Abstract}` explícito antes do resumo em inglês.
- Cabeçalho e rodapé são imagens posicionadas por TikZ com `remember picture` → **compilar duas vezes** (ou o Overleaf resolve sozinho no segundo passe).

## Checklist antes de submeter

- [ ] Compilar no Overleaf e conferir: **entre 3 e 4 páginas**, referências incluídas
- [ ] Preencher a **Declaração de uso de IA** (`[FERRAMENTA]`, `[FINALIDADE]`, `[ETAPA]`)
- [ ] Preencher `\cmtid` com o ID do JEMS (ou remover a linha)
- [ ] Confirmar que `\finalfalse` está ativo (versão cega) — nenhum nome, instituição ou "Hartheus" no PDF
- [ ] Conferir metadados do PDF (o Overleaf não injeta autor, mas vale checar)
- [ ] Submeter o **PDF** no JEMS3 antes de 23h59 de 14/08/2026
- [ ] Se aceito: trocar para `\finaltrue`, preencher nome/e-mail do orientador, enviar versão final + Termo de Autorização até 02/10/2026, e garantir inscrição + apresentação presencial em Foz do Iguaçu
