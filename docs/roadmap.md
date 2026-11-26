# Roadmap

Onde cada parte do sistema está, e em que ordem o trabalho anda. O porquê de cada escolha está
no [`decisoes.md`](decisoes.md); os itens soltos, no [`pendencias.md`](pendencias.md).

Última atualização: 25/11/2026

**Em uma frase:** a faixa A está selecionada e calibrada, o pacote da auditoria está pronto, e o
que falta para fechar o TCC são os julgamentos da auditoria e o texto. O Experimento 2 virou
trabalho futuro em 23/11 (**D6**).

**Prazos (19/11, ainda sem confirmação do Rafael):** defesa até dezembro de 2026; publicação até
fevereiro de 2027. Data de trabalho da versão para a banca: 01/12/2026.

---

## Estado de cada parte

| Parte | Estado |
|---|---|
| `rock_viewer.py`: seleção das 4 vagas | ✅ protocolo da D17; modo revisão numa litologia 4/4 (08/10) |
| `calibrator.py`: sondas e limiar | ✅ 3 abas, um slider, 4 previews (26/09) |
| `sam_cache.py`: varredura sem GPU | ✅ D18 |
| `verificar_d18.py`: prova da D18 | ✅ 32 de 32 idênticas, nas duas versões do ultralytics |
| `inference.py`: máscaras finais | ✅ só roda sobre litologia calibrada; grava a procedência |
| `figuras_regra_autor.py` | ✅ regra × autor na mesma chapa, do cache (20/10) |
| Seleção (`selectRocks/`) | 🟡 44 de 180 vagas: a faixa A inteira (08/10) |
| Calibração (`calibracao.json`) | 🟡 11 de 45 litologias: a faixa A inteira (20/10) |
| Auditoria (`auditoria_preparar.py` / `auditoria_analisar.py`) | 🟡 pacote pronto (19/11; app atualizado em 23/11); faltam os julgamentos |
| Classificador Xception | ✅ treinado e avaliado (96,72% no `test/`; 99,92% com sorteio por imagem); 🟡 falta ligar o roteador ao resto |
| Monografia (`apresentações/Overleaf/TCC/`) | 🟡 tudo escrito menos o resultado do experimento; compila (22/11: 60 páginas, sem erro) |
| Inferência em lote sobre o dataset (`sam_batch.py`) | ⏸️ trabalho futuro (D6) |
| Treino e avaliação do YOLO | ⏸️ trabalho futuro (D6); `AI/YOLO/` está vazio |
| Artigos de PD1 e LatinoWare | 🔴 desatualizados (D13); o da LatinoWare foi recusado (06/11) |

---

## Fase 0 — Desbloqueio ✅ (23/08/2026)

Casing do caminho do dataset corrigido (o `.gitignore` lista as duas grafias); `class_id = -1`
silencioso eliminado (a validação aborta antes de carregar o modelo); sonda exploratória não grava
mais polígono; `scratch` registrada; `rock_viewer.py` ordenando por faixa de volume.

## Fase 1 — Seleção e calibração da faixa A ✅ (20/10/2026)

Protocolo da **D17**: 4 imagens por litologia, só do `train/`, escolhidas à mão; regra do joelho
fixada antes da primeira calibração.

| Litologia | Vagas selecionadas | `calibracao.json` |
|---|---|---|
| siena_white | 08/09 | 01/10 (refeita em 09–10/10) |
| nevada_black | 02/10 | 09/10 |
| ubatuba_green | 03/10 (típica revista no mesmo dia) | 09/10 |
| ipanema_beige | 03/10 | 10/10 |
| itaunas_white | 05/10 | 10/10 |
| santa_cecilia | 06/10 | 19/10 (refeita sem `vein`) |
| white_mirage | 07/10 | 20/10 |
| golden_storm | 08/10 | 20/10 |
| white_olympus | 08/10 | 20/10 |
| shadow_white | 08/10 (pulada em 03/10) | 10/10 |
| san_francisco_green | 08/10 (pulada em 07/10) | 20/10 |

Resultado: o autor ficou acima da regra nas 45 sondas, com razão mediana de 3,3 (seção 4.5 do
TCC). A faixa B não começou.

```bash
cd AI/SAM
..\.venv\Scripts\python.exe rock_viewer.py          # próxima vaga pendente, em ordem de faixa
..\.venv\Scripts\python.exe rock_viewer.py <rocha>  # completa as vagas, ou revisa uma rocha 4/4
..\.venv\Scripts\python.exe rock_viewer.py --all    # mostra val/ e test/ só para estudo
```

## Fase 2 — O experimento: auditoria cega dos quatro braços 🟡

**D5** (os braços), **D7** (a auditoria) e **D4** (a hipótese e como ela se decide). Não exige
treino nenhum.

1. ✅ Sortear 3 chapas do `test/` por litologia calibrada (33), com semente fixa.
2. ✅ Rodar o Professor uma vez por chapa, com todas as sondas no piso, e filtrar os quatro braços
   (`unico`, `regra_todas`, `regra_autor`, `autor`) do mesmo cache (**D18**).
3. ✅ Montar o pacote: 420 itens estratificados e intercalados, sem braço, sonda, litologia nem
   score. **Não rodar o `auditoria_preparar.py` de novo** (ver `CLAUDE.md`).
4. ✅ Fixar como a H1 é decidida, antes dos julgamentos (emenda de 25/11 na D4).
5. [ ] Julgamentos: a avaliadora e o autor, separados.
6. [ ] Analisar com o `auditoria_analisar.py`: precisão e recall relativo por braço, IC 95%,
   kappa; e as análises secundárias registradas na D4.
7. [ ] Escrever o resultado no TCC.

**Entregável:** a H1 respondida, com número e figura.

## Fase 3 — Alunos especialistas × generalista ⏸️ trabalho futuro

Saiu da entrega em 23/11/2026 (**D6**). Fica o registro do que seria preciso:

- **`sam_batch.py`**: rodar o Professor sobre uma amostra de N imagens por litologia (não sobre as
  34.630) e montar `images/` + `labels/` + `data.yaml`. Usar `sam_cache.pecas_por_deteccao` (**D21**).
- **Pós-processamento do Professor**: área mínima dos fragmentos, teto de instâncias por imagem,
  simplificação de polígono.
- **Regra de divisão dos dados do Aluno** (por sequência ou por sorteio; ver `dataset.md`,
  *Sequência e blocos*).
- **Contra o que avaliar o Aluno**: medi-lo contra o próprio Professor só mostra o quanto ele copia.
- **Execução por faixa** (A, B, C, D), cada uma escrita antes da seguinte, com os três braços da D6.

## Fase 4 — Integração e fechamento

1. ✅ Reproduzir o Xception do DeepStoneAI (**D19**): estrutura em `AI/Xception/` (02/10), treino
   em 480 × 480 (03/10, ~1h10), avaliação única no `test/` (03/10), medição do vazamento com sorteio
   por imagem (04/10), decisão de reportar os dois números (06/10). Não há mais treino previsto.
2. [ ] **Roteador**: ligar o `roteador.py` (litologia + confiança + top-3) à escolha do
   `calibracao.json`. Opcional para a entrega.
3. [ ] **Teste de ponta a ponta** dos três estágios. Opcional.
4. [ ] **FPS**: só se o YOLO de demonstração for feito. Sem medição, o texto não promete tempo real.

---

## Fora do escopo (trabalhos futuros declarados)

Aprendizado ativo (**D11**); rotulagem multiclasse (**D12**); o Experimento 2 e a H2 (**D6**); as
faixas B, C e D; generalização além das 45 litologias; integração com sistemas de chão de fábrica.
