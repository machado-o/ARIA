# Diretrizes de Implementação — ARIA

> Regras de **como eu trabalho no código**. Os **fatos** do codebase (gotchas, paths, o que é
> gitignored, branches, comandos) ficam no `../CLAUDE.md` — não repetir aqui.
> Em conflito, o que o Henrique disser na conversa vence.
>
> Última atualização: 2026-06-11

---

## 1. Como eu trabalho

1.1. **Verificar antes de afirmar que funciona** — rodar o script e observar a saída real antes
de dizer "pronto"/"corrigido". Evidência antes de afirmação.

1.2. **Decisão de arquitetura ou metodologia não se resolve no código sozinho** — alinhar com
`decisoes.md` e, se for decisão nova, perguntar ao Henrique.

1.3. **`Dataset/` é somente-leitura** — os scripts leem as imagens-fonte; nunca modificar, mover
ou apagar nada do `Dataset/`.

1.4. **Commit e push só quando o Henrique pedir.**

---

## 2. Onde está a verdade

| Preciso de... | Olhar em |
|---|---|
| Fatos do codebase, gotchas, paths, comandos, branches | `../CLAUDE.md` |
| Arquitetura detalhada do pipeline | `arquitetura.md` |
| Dataset, classes, formato de anotação | `dataset.md` |
| Decisões fechadas (rotulagem, baseline...) | `decisoes.md` |
| Próximos passos do desenvolvimento | `roadmap.md` |
