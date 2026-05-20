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

**Decisão atual: Opção A — binário (anomalia genérica, `class_id = 0`).**

O `inference.py` já atribui class_ids por prompt via `CLASS_ID_MAP` (`crack→1`, `vein→0`, `Stain→2`, etc.), mas as anotações geradas serão normalizadas para `class_id = 0` antes do treinamento YOLO. Motivação: os labels multi-classe são tão confiáveis quanto os embeddings CLIP no domínio de rochas — e isso não foi validado. Usar class_ids distintos como ground truth assumiria que o SAM distingue fissura de veio corretamente, o que é uma afirmação não verificada.

**Opção B — multi-classe: prevista, mas fora do escopo desta entrega.**
Se houver tempo, o objetivo é treinar o YOLO com os class_ids originais (`crack`, `vein`, `Stain`, `Dark patches`, `light spot`) e comparar com o modelo binário. Isso requer ou validação humana de uma amostra das anotações SAM, ou uma justificativa explícita de que os labels são tratados como pseudorrótulos. Registrado como evolução desejada, não limitação permanente.

**Impacto na metodologia:** A seção de Metodologia deve explicar a escolha binária como decisão deliberada (não omissão), e mencionar multi-classe como extensão natural na seção de Trabalhos Futuros.

---

## Desafios do Dataset

1. **Desbalanceamento natural:** Algumas classes têm muito mais imagens que outras. Reflexo real da indústria.
2. **Variabilidade intra-classe:** Mesmo tipo de rocha pode ter aparência muito diferente (lote, iluminação, acabamento).
3. **Subjetividade das anomalias:** O que é defeito em uma rocha pode ser característica estética em outra.
4. **Ausência de ground truth padronizado:** Não há anotações humanas preexistentes — o SAM está gerando as primeiras anotações.
5. **Rochas exóticas:** Algumas classes (kalahari, ice_leke, quartzito_venom) têm texturas muito fora do padrão, dificultando a generalização.

---

## Status de Calibração

Para cada tipo de rocha: (1) selecionar imagem representativa via `rock_viewer.py` → `selectRocks/`; (2) rodar `inference.py` e ajustar prompts/limiares em `rock_prompts.json` até o resultado ser satisfatório; (3) salvar resultado validado em `samples/`.

| Status | Rochas | Observação |
|---|---|---|
| **Calibrado e validado** | `ice_leke` | Resultado salvo em `results/`; cópia em `samples/` como demonstração |
| **Imagem selecionada, prompts pendentes** | `giallo_fiorito`, `giallo_maracana` | Imagem em `selectRocks/`, calibração não concluída |
| **Pendentes** | 42 rochas restantes | Sem imagem selecionada nem prompts calibrados |

**`samples/`** — pasta de demonstração, contém apenas o resultado do ice_leke. Não é o destino dos resultados de calibração; todos os outputs do `inference.py` vão para `results/`.

A calibração completa (45/45) é pré-requisito para gerar as anotações SAM do pipeline especialista e executar a comparação com o baseline.

---

## Formato das Anotações (Output SAM → Input YOLO)

```
<class_id> <x1> <y1> <x2> <y2> ... <xN> <yN>
```

- Coordenadas normalizadas (0–1 em relação às dimensões da imagem)
- Um polígono por linha
- Compatível com formato de segmentação de instâncias do YOLO
