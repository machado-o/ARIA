# Dataset — ARIA

## Visão geral

| Característica | Valor |
|---|---|
| Total de imagens | **34.630** (train 24.263 · val 5.214 · test 5.153) |
| Litologias | 45 |
| Origem | **Conjunto público, obtido no Kaggle** — imagens industriais reais de chapas |
| Constituição | O autor **não** constituiu o banco: selecionou, caracterizou e pré-processou um conjunto existente (**D9**) |
| Desbalanceamento | Natural, não equalizado — e tratado como **variável do experimento** (**D6**) |

- [ ] **TODO:** preencher URL, nome e autoria do dataset no Kaggle. Sem isso a fonte não pode ser
  citada (ver `pendencias.md`).

---

## Faixas de volume — a estratificação do Experimento 2

O experimento central roda **por faixa**, da maior para a menor, e reporta resultado **por faixa**
(**D6**). Contagens reais em disco (train + val + test), verificadas em 2026-08-23.

### Faixa A — ≥ 1000 imagens · 11 litologias

| Litologia | Imagens | | Litologia | Imagens |
|---|---:|---|---|---:|
| siena_white | 4.588 | | santa_cecilia | 1.446 |
| nevada_black | 3.806 | | san_francisco_green | 1.404 |
| ubatuba_green | 2.965 | | white_mirage | 1.219 |
| ipanema_beige | 2.894 | | golden_storm | 1.185 |
| shadow_white | 1.922 | | white_olympus | 1.153 |
| itaunas_white | 1.546 | | | |

### Faixa B — 500 a 999 · 6 litologias

| Litologia | Imagens | | Litologia | Imagens |
|---|---:|---|---|---:|
| naica | 727 | | sao_gabriel_black | 610 |
| kalahari | 665 | | new_caledonia | 556 |
| vitoria_white | 619 | | perla_venato | 508 |

### Faixa C — 200 a 499 · 14 litologias

| Litologia | Imagens | | Litologia | Imagens |
|---|---:|---|---|---:|
| solarius | 470 | | giallo_maracana | 339 |
| white_ceara | 453 | | white_everest | 295 |
| quartzito_venom | 434 | | icarai_yellow | 292 |
| santa_cecilia_light | 390 | | xango_red | 280 |
| white_extreme | 388 | | ornamental | 251 |
| white_himalaya | 360 | | white_superiore | 246 |
| tabaco_red | 346 | | olympios | 209 |

### Faixa D — < 200 · 14 litologias

| Litologia | Imagens | | Litologia | Imagens |
|---|---:|---|---|---:|
| white_liberdade | 196 | | splendor_gold | 171 |
| rocky_mountain | 191 | | quartzito_thannos | 130 |
| white_cintilante | 183 | | white_bellukha | 122 |
| giallo_fiorito | 181 | | **ice_leke** | **113** |
| quartzito_green_da_vinci | 174 | | white_serenata | 109 |
| maracuja_yellow | 174 | | white_sea | 108 |
| | | | white_samoa | 106 |
| | | | quartzito_verde_sauipe | 106 |

> ⚠️ A **`ice_leke`**, litologia usada como demonstração em todo o material escrito, está na
> **faixa D** — é uma das mais pobres do conjunto (113 imagens). Vale saber disso antes de a
> banca perguntar.

---

## Agrupamento cromático

Agrupamento **provisório** (**D15**), usado pela configuração atual de sondas em
`rock_prompts.json`. Se a calibração final será por litologia ou por grupo ainda **não está
decidido** — só depois que a faixa A estiver calibrada de fato.

| Grupo | Litologias |
|---|---|
| Brancas / claras | white_bellukha, white_ceara, white_cintilante, white_everest, white_extreme, white_himalaya, white_liberdade, white_mirage, white_olympus, white_samoa, white_sea, white_serenata, white_superiore, itaunas_white, shadow_white, siena_white, vitoria_white, naica |
| Amarelas / bege / douradas | giallo_fiorito, giallo_maracana, golden_storm, icarai_yellow, maracuja_yellow, solarius, splendor_gold, santa_cecilia, santa_cecilia_light, ipanema_beige |
| Verdes / quartzitos | quartzito_green_da_vinci, quartzito_thannos, quartzito_venom, quartzito_verde_sauipe, san_francisco_green, new_caledonia, ubatuba_green |
| Escuras | nevada_black, sao_gabriel_black |
| Vermelhas | xango_red, tabaco_red |
| Especiais | kalahari, perla_venato, ornamental, rocky_mountain, olympios, ice_leke |

---

## Sondas de detecção

**Não são rótulos.** São chaves lexicais escolhidas por fazerem o CLIP+SAM3 responder a certas
assinaturas visuais; o objetivo do conjunto é **maximizar cobertura**, não classificar (**D2**).

| Sonda | Assinatura visual que costuma disparar | Escopo típico |
|---|---|---|
| `crack` | descontinuidades lineares finas e escuras | todas |
| `vein` | estrias e faixas contrastantes | todas |
| `Stain` | variação de cor em mancha difusa | todas |
| `Dark patches` | regiões escuras sobre fundo claro | rochas claras |
| `light spot` | regiões claras sobre fundo escuro | rochas escuras |
| `scratch` | riscos superficiais finos | pontual (`giallo_maracana`) |

Por isso todas as regiões recebem `class_id = 0` no treino: o projeto **não afirma** que uma
região marcada por `"crack"` é uma fissura (**D2**). Multi-classe → trabalho futuro (**D12**).

---

## Desafios

1. **Desbalanceamento** — de 106 a 4.588 imagens por litologia. Reflete a realidade industrial e,
   neste trabalho, virou variável medida (**D6**), não limitação.
2. **Variabilidade intra-classe** — mesma rocha muda de aparência conforme lote, iluminação e
   acabamento.
3. **Fronteira arbitrária** — o que é defeito numa rocha é estética em outra. É o problema central
   do TCC (**D3**), não um ruído a contornar.
4. **Ausência de ground truth** — não há anotação humana preexistente. Daí o conjunto-ouro
   anotado às cegas (**D7**).
5. **Texturas fora do padrão** — kalahari, ice_leke e quartzito_venom dificultam a generalização.

---

## Formato de anotação (saída do Professor → entrada do Aluno)

```
<class_id> <x1> <y1> <x2> <y2> ... <xN> <yN>
```

Coordenadas normalizadas (0–1), um polígono por linha, formato de segmentação de instâncias do
YOLO — sem conversão intermediária.

> **Atenção ao volume:** no único exemplo existente (`AI/SAM/samples/ice_leke.txt`) são **107
> polígonos numa única imagem**, com até 1.742 pontos cada. O pós-processamento do Professor
> (área mínima, teto de instâncias, simplificação) é etapa obrigatória antes do treino — ver
> `roadmap.md` → Fase 3.0.
