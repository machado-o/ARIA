# Dataset — ARIA

## Visão geral

| Característica | Valor |
|---|---|
| Total de imagens | **34.630** (train 24.263 · val 5.214 · test 5.153) |
| Litologias | 45 |
| Origem | **Conjunto público no Kaggle:** *Chapas polidas de rochas ornamentais*, de `joovictorcostaaraujo` — [kaggle.com/datasets/joovictorcostaaraujo/chapas-polidas-de-rochas-ornametais](https://www.kaggle.com/datasets/joovictorcostaaraujo/chapas-polidas-de-rochas-ornametais) |
| Constituição | O autor **não** constituiu o banco: selecionou, caracterizou e pré-processou um conjunto existente (**D9**) |
| Desbalanceamento | Natural, não equalizado — e tratado como **variável do experimento** (**D6**) |

> ⚠️ O `.EXT` do slug no Kaggle tem um typo de origem (`ornametais`, sem o "n"). Ao citar, usar a
> URL exata acima — encurtá-la ou "corrigi-la" quebra o link.

- [ ] **TODO:** confirmar se o DeepStoneAI usou este mesmo conjunto. Se sim, vira citação
  obrigatória (ver `pendencias.md`).

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

## Litologias movimentadas — as mais difíceis de julgar

Registro do autor, feito durante a seleção manual das vagas (**D17**): rochas de padrão
movimentado, em que é mais difícil dizer o que é defeito e o que é desenho da pedra. A lista é
**observação do autor** — nenhuma das quatro teve a classificação petrográfica confirmada (ver a
pesquisa abaixo); o que se decidiu fazer com essas litologias está na **D20**.

> **Sobre o termo.** O autor as chamou primeiro de "exóticas". Em 07/10/2026 o termo passou a
> ser **"movimentadas"** (**D20**): "exótico" é categoria comercial do setor, ligada a raridade
> e preço, e não descreve a dificuldade observada. "Exótico" só aparece abaixo quando o assunto
> é o termo de mercado.

A lista cresce conforme a seleção avança, e por enquanto só cobre a faixa A.

| Litologia | Faixa | Situação na seleção | Anotado em |
|---|---|---|---|
| shadow_white | A | ✅ 4/4 — pulada em 03/10/2026, selecionada em 08/10/2026 | 03/10/2026 |
| san_francisco_green | A | ✅ 4/4 — pulada em 07/10/2026, selecionada em 08/10/2026 | 07/10/2026 |
| white_mirage | A | ✅ 4/4 selecionadas, mesmo sendo movimentada | 07/10/2026 |
| golden_storm | A | ✅ 4/4 selecionadas, mesmo sendo movimentada | 08/10/2026 |

**As quatro estão selecionadas.** As duas que tinham sido puladas foram feitas em 08/10/2026
**sem a opinião de especialista** — a ajuda foi pedida na faculdade e até essa data não veio, e a
**D20** já havia decidido que ela não bloqueia a calibração. O autor registrou que a seleção
dessas duas **foi difícil**. É isso que a calibração precisa medir: nas quatro movimentadas, o
limiar escolhido pelo autor é o elo frouxo, e o critério escrito de cada `calibracao.json` deve
dizer que a marcação saiu sem conferência de quem conhece rocha.

### Por que isto é um tópico, e não só um atraso

Nas litologias comuns o autor olha a chapa e consegue dizer o que marcaria. Nas movimentadas, não:
o desenho natural da pedra já tem manchas, veios e contrastes fortes, e a mesma feição pode ser
o que valoriza a chapa ou o que a desclassifica. A marcação fica **mais pessoal** — depende mais
de quem olha do que da imagem.

A dúvida do autor, registrada como ele a colocou (07/10/2026): **não se sabe se é realmente
possível marcar uma rocha dessas de forma correta.**

Onde isso encosta no desenho do trabalho:

- **D3 (fronteira arbitrária).** A D3 já diz que não existe um "certo" absoluto, e que a
  contribuição é tornar o critério explícito. As movimentadas são o caso-limite: aqui o autor não
  consegue nem formar o critério sozinho. Leitura a confirmar — a pergunta talvez não seja "dá
  para marcar certo?", e sim "dá para escrever um critério que outra pessoa aplicaria igual?".
- **D17 (calibração).** A vaga `descoberta` e o limiar de trabalho dependem do julgamento do
  autor. Numa movimentada, esse julgamento é o elo fraco: o `calibracao.json` sai, mas com um
  critério escrito em que o próprio autor confia menos.
- **D7 (conjunto-ouro).** O gabarito é anotado pelo autor. Se ele não sabe o que é defeito numa
  litologia, o IoU dela mede concordância com uma anotação incerta. O plano da Fase 2 usa 10 das
  11 litologias da faixa A — e 3 das 11 já estão nesta lista.
- **D5 (braço calibrado pelo autor).** A divergência entre o limiar da regra e o do autor tende
  a significar outra coisa numa movimentada: menos "onde a curva engana", mais dúvida de quem ajusta.

O que foi decidido sobre isso está na **D20**: as movimentadas são calibradas como as demais, e a
opinião externa é buscada em paralelo. O que segue em aberto está em `pendencias.md` →
*Litologias movimentadas*.

### Existe critério para "exótica"? — pesquisa de 07/10/2026

**Resumo: "exótico" é palavra de mercado, sem critério mensurável. O conceito técnico que
descreve a dificuldade observada aqui é outro — rocha *movimentada*, em oposição a *homogênea*.**

**1. "Exótico" no setor é categoria comercial, definida por lista e por valor.**

- Chiodi Filho (2007, p. 37) fala nos *"denominados 'materiais exóticos', que abrangem granitos
  pegmatóides e pegmatitos, granitos infiltrados (oxidados), quartzitos coloridos, rochas de
  derivação vulcânica, jaspes, cherts, silexitos, conglomerados, brechas sedimentares e
  tectônicas, além de itabiritos e xistos diversos"*. É uma enumeração de tipos de rocha, não uma
  regra.
- O Informe ABIROCHAS 05/2018 trata as *"rochas exóticas, de alto valor agregado"* (p. 6) como
  grupo de exportação, *"com destaque para pegmatitos e rochas quartzíticas"* (p. 12), e diz que o
  Espírito Santo se destaca por *"granitos homogêneos, especialmente amarelos, verdes e negros,
  bem como de mármores e alguns poucos materiais exóticos"* (p. 30).
- Nenhuma das fontes lidas dá um limite ou um teste: o termo fala de raridade, preço e tipo
  geológico. **Não diz nada sobre ser difícil de marcar.**

**2. O critério técnico que existe: homogêneo × movimentado.**

Meyer (2003), citado por Camargo, Artur e Silveira (2015, p. 920): *"o padrão textural e
estrutural classificam os materiais rochosos em dois grupos: os homogêneos e os movimentados"*.
Os homogêneos têm *"estruturas isotrópicas, sem orientação mineral definida"*; os movimentados
*"apresentam algum tipo de estrutura ou textura definida pela concentração ou orientação
preferencial de seus constituintes minerais"* — bandamento, foliação, estruturas migmatíticas.

É o que mais se aproxima do que o autor chamou de exótico: a chapa tem desenho próprio, e é esse
desenho que se confunde com defeito. Três ressalvas:

- a definição é petrográfica e foi escrita para "granitos" (rochas silicáticas); não é uma medida
  tirada da imagem;
- foi lida em segunda mão — a dissertação de Meyer (2003) **não foi consultada**; citar exige
  buscar o original ou usar *apud*;
- nenhuma fonte foi encontrada classificando `shadow_white`, `san_francisco_green` ou
  `white_mirage`. Sites de fornecedores descrevem o *Verde San Francisco* como granito de ondas e
  estrias intensas, o que bate com "movimentado", mas é texto de venda, não fonte.

**3. Medir pela imagem é possível, mas não há régua pronta para chapa polida.**

- Há uma linha de pesquisa em caracterização estética de chapas por análise de imagem (Univ. de
  Bolonha), com medidas de densidade, cor e geometria de veios a partir de variogramas e
  morfologia matemática. **Só o resumo foi visto** — o texto não abriu.
- Silva et al. (2025) propõem uma medida de heterogeneidade textural por entropia em
  subvolumes, validada contra 4 especialistas em 175 amostras. É microtomografia de rocha de
  reservatório, não chapa ornamental: vale como método análogo, não como régua aplicável.

**O que saiu da pesquisa:**

- **decidido em 07/10/2026 (D20):** o termo do trabalho é **"movimentada"**, não "exótica" —
  "exótica" tem sentido comercial estabelecido (preço e raridade) e alguém do setor pode
  contestar o uso;
- **em aberto:** a lista acima continua sendo julgamento do autor. Para virar recorte de resultado, o critério
  precisa ser aplicável por outra pessoa: ou a classificação petrográfica vinda de quem conhece
  rocha (a mesma opinião externa já pedida), ou uma medida de imagem, que seria decisão nova.

**Fontes**

- CHIODI FILHO, C. *Situação atual e perspectivas brasileiras no setor de rochas ornamentais e de
  revestimento.* III Congresso Brasileiro de Rochas Ornamentais, cap. 2, 2007. CETEM —
  <https://mineralis.cetem.gov.br/bitstream/cetem/1298/1/III_Congresso_Br%20RO%2017-41.pdf>
- ABIROCHAS. *O setor brasileiro de rochas ornamentais.* Informe 05/2018 —
  <https://abirochas.com.br/wp-content/uploads/2022/01/Informe_05_2018_Setor_de_Rochas_Ornamentais_c.pdf>
- CHIODI FILHO, C.; CHIODI, D. K. *O setor de rochas ornamentais no Brasil.* In: *Tecnologia de
  rochas ornamentais*. CETEM/MCTI, 2014, p. 493–526 —
  <https://mineralis.cetem.gov.br/bitstream/cetem/1739/1/CCL00180014Cap10LivroRochas.pdf>
- CAMARGO, J. L.; ARTUR, A. C.; SILVEIRA, L. L. L. *Utilização de ensaios tecnológicos como
  auxílio na interpretação do polimento de rochas ornamentais.* Geociências (UNESP), v. 34, n. 4,
  p. 919–937, 2015 —
  <https://periodicos.rc.biblioteca.unesp.br/index.php/geociencias/article/download/10587/6979/56488>
- MEYER, A. P. *Influência da petrografia no comportamento tecnológico de rochas ornamentais do
  Complexo Socorro (SP) e maciço Pedra Branca (MG).* Dissertação (Mestrado), UNESP Rio Claro,
  2003. **Não consultada** — referência tirada de Camargo et al. (2015).
- SILVA, L. C. V. et al. *Entropy-based measure of rock sample heterogeneity derived from micro-CT
  images.* 2025 — <https://arxiv.org/abs/2502.01665>
- Caracterização estética de chapas por análise de imagem (Univ. de Bolonha), só resumo —
  <https://cris.unibo.it/handle/11585/60081>

> ⚠️ Os trechos entre aspas foram conferidos no texto dos PDFs em 07/10/2026. O que está marcado
> como "só resumo" ou "não consultada" **não pode ser citado** antes de ser lido.

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
| `white stain` | manchas brancas que o `light spot` não pega | em avaliação (`san_francisco_green`) |

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
   As que o autor achou movimentadas ao selecionar as vagas estão em *Litologias movimentadas*,
   acima.

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
