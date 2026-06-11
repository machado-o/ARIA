# Dataset — ARIA

## Visão Geral

| Característica | Valor |
|---|---|
| Total de imagens | ~34.630 |
| Classes de rocha | 45 |
| Splits | train / val / test |
| Origem | Imagens industriais reais de chapas de rochas ornamentais |
| Desbalanceamento | Natural — sem equalização artificial |
| Variabilidade | Alta — texturas, cores e padrões muito distintos entre e dentro de classes |

---

## Classes (45 tipos de rocha)

### Brancas / Claras

| Nome | Grupo |
|---|---|
| white_bellukha | Branca |
| white_ceara | Branca |
| white_cintilante | Branca |
| white_everest | Branca |
| white_extreme | Branca |
| white_himalaya | Branca |
| white_liberdade | Branca |
| white_mirage | Branca |
| white_olympus | Branca |
| white_samoa | Branca |
| white_sea | Branca |
| white_serenata | Branca |
| white_superiore | Branca |
| itaunas_white | Branca |
| shadow_white | Branca/Clara |
| siena_white | Branca/Clara |
| vitoria_white | Branca/Clara |
| naica | Clara |

### Amarelas / Bege

| Nome | Grupo |
|---|---|
| giallo_fiorito | Amarela |
| giallo_maracana | Amarela |
| golden_storm | Dourada |
| icarai_yellow | Amarela |
| maracuja_yellow | Amarela |
| solarius | Dourada |
| splendor_gold | Dourada |
| santa_cecilia | Bege/Amarela |
| santa_cecilia_light | Bege/Amarela |
| ipanema_beige | Bege |

### Verdes / Quartzitos

| Nome | Grupo |
|---|---|
| quartzito_green_da_vinci | Quartzito |
| quartzito_thannos | Quartzito |
| quartzito_venom | Quartzito |
| quartzito_verde_sauipe | Quartzito |
| san_francisco_green | Verde |
| new_caledonia | Verde |
| ubatuba_green | Verde |

### Escuras

| Nome | Grupo |
|---|---|
| nevada_black | Preta |
| sao_gabriel_black | Preta |

### Coloridas / Especiais

| Nome | Grupo |
|---|---|
| xango_red | Vermelha |
| tabaco_red | Vermelha |
| kalahari | Especial |
| perla_venato | Especial |
| ornamental | Especial |
| rocky_mountain | Especial |
| olympios | Especial |
| ice_leke | Especial |

---

## Tipos de Anomalia / Feature

O dataset contém múltiplos tipos de irregularidades superficiais. A categorização exata é um ponto em aberto (ver abaixo).

**Features utilizadas na calibração SAM:**

| Feature | Descrição | Escopo |
|---|---|---|
| `crack` | Fissuras, trincas na superfície | Principal anomalia |
| `vein` | Veios minerais / estrias naturais | Pode ser anomalia ou característica |
| `Stain` | Manchas, descoloração | Anomalia |
| `Dark patches` | Áreas escuras em rochas claras | Anomalia / oxidação |
| `light spot` | Pontos claros em rochas escuras | Anomalia |

**Nota:** O SAM demonstrou capacidade de segmentar anomalias mesmo com nomes de prompt distantes da terminologia técnica geológica. Os nomes em inglês são linguagem natural para o CLIP, não rótulos técnicos. O conjunto atual é o de trabalho desta versão — novos tipos de anomalia podem ser adicionados ao `rock_prompts.json` futuramente sem quebrar o pipeline. As anomalias não são rotuladas no treinamento YOLO (decisão binária desta versão).

---

## Rotulagem de Classes de Anomalia

A rotulagem é **binária** (`class_id = 0`) nesta versão; multi-classe é trabalho futuro. A decisão completa — justificativa (confiabilidade dos embeddings CLIP) e impacto na metodologia — é fonte única em `decisoes.md` (**D2** e **D9**).

---

## Desafios do Dataset

1. **Desbalanceamento natural:** Algumas classes têm muito mais imagens que outras. Reflexo real da indústria.
2. **Variabilidade intra-classe:** Mesmo tipo de rocha pode ter aparência muito diferente (lote, iluminação, acabamento).
3. **Subjetividade das anomalias:** O que é defeito em uma rocha pode ser característica estética em outra.
4. **Ausência de ground truth padronizado:** Não há anotações humanas preexistentes — o SAM está gerando as primeiras anotações.
5. **Rochas exóticas:** Algumas classes (kalahari, ice_leke, quartzito_venom) têm texturas muito fora do padrão, dificultando a generalização.

---

## Calibração — processo

Para cada tipo de rocha: (1) selecionar imagem representativa via `rock_viewer.py` → `selectRocks/`; (2) rodar `inference.py` e ajustar prompts/limiares em `rock_prompts.json` até o resultado ser satisfatório; (3) salvar resultado validado em `samples/`.

**`samples/`** — pasta de demonstração, contém apenas o resultado do `ice_leke`. Não é o destino dos resultados de calibração; todos os outputs do `inference.py` vão para `results/`.

A calibração completa (45/45) é pré-requisito para gerar as anotações SAM do pipeline especialista e executar a comparação com o baseline.

> Status vivo (quais rochas já calibradas) → `ROADMAP.md`.

---

## Formato das Anotações (Output SAM → Input YOLO)

```
<class_id> <x1> <y1> <x2> <y2> ... <xN> <yN>
```

- Coordenadas normalizadas (0–1 em relação às dimensões da imagem)
- Um polígono por linha
- Compatível com formato de segmentação de instâncias do YOLO
