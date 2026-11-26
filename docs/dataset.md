# Dataset

## Visão geral

| | |
|---|---|
| Imagens | **34.630** (train 24.263 · val 5.214 · test 5.153) |
| Litologias | 45 |
| Origem | conjunto público do Kaggle, *Chapas polidas de rochas ornamentais*, de `joovictorcostaaraujo`: <https://www.kaggle.com/datasets/joovictorcostaaraujo/chapas-polidas-de-rochas-ornametais> |
| Quem montou | não foi o autor: ele selecionou, caracterizou e pré-processou um conjunto existente (**D9**) |
| Desbalanceamento | natural, de 106 a 4.588 imagens por litologia, não equalizado |
| Alteração local | uma pasta renomeada, `whte_liberdade` → `white_liberdade` (**D9**); refazer em toda máquina |

> O slug do Kaggle tem um typo de origem (`ornametais`, sem o "n"). Ao citar, usar a URL exata
> acima: "corrigi-la" quebra o link.

É o mesmo conjunto do DeepStoneAI (artigo do SBAI 2025), e citá-lo é obrigatório (**D9**).

---

## Faixas de volume

Agrupam as litologias pelo número de imagens (train + val + test, contado em 23/08/2026). Hoje
elas são **a ordem de trabalho da calibração**: a faixa A primeiro, e o `rock_viewer.py` entrega as
rochas nessa ordem. No Experimento 2, que virou trabalho futuro (**D6**), elas seriam também a
variável do experimento.

### Faixa A — 1.000 imagens ou mais · 11 litologias (calibradas)

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

### Faixa D — menos de 200 · 14 litologias

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

> A `ice_leke`, usada como demonstração no material antigo e em `AI/SAM/samples/`, está na faixa D:
> é uma das mais pobres do conjunto. Bom saber antes de a banca perguntar.

---

## Sequência e blocos: o que se sabe sobre as divisões

Isto saiu da investigação do classificador (**D19**, 02 a 06/10/2026) e afeta qualquer uso das
divisões `train/val/test`.

**A numeração dos arquivos segue a ordem das chapas.** Chapas seguidas são cortadas do mesmo bloco
e têm os mesmos veios. Numa sondagem grosseira (miniaturas 32 × 32, diferença absoluta média, só
cor e brilho, 5 rochas), imagens consecutivas do `train/` ficaram a 4,0 uma da outra, contra 12,5
para pares sorteados (`white_superiore`); na `ipanema_beige`, 4,0 contra 15,3.

**O `test/` de algumas rochas parece vir de outro bloco.** A `white_superiore` acertou 35 de 37 no
`val/` e 0 de 36 no `test/`. As imagens do `test/` são acinzentadas, com veios lineares e
paralelos; as do `train/` e do `val/` são brancas, com veios ramificados. O `test/` dela é mais
escuro (brilho 188, contra 213 no `train/` e 226 no `val/`) e fica mais longe do treino que o
`val/` (6,1 contra 3,0). **Isso não vale para toda rocha:** na `ipanema_beige` o `test/` está tão
perto do treino quanto o `val/` (3,2 e 3,8), e na `white_himalaya` o `val/` também está longe
(35,6; `test/` 22,6).

**O sorteio por imagem vaza.** O DeepStoneAI juntou `train/`, `valid/` e `test/` numa pasta por
rocha (`organize2.ipynb`) e sorteou por imagem (`validation_split=0.3`, seed 123), cortando a
validação ao meio em val e test (15% cada; o artigo diz 25%). Assim, chapas vizinhas das de treino
caem no teste. Agravante provável, não confirmado: `take`/`skip` sobre um dataset que reembaralha a
cada passada faz val e test se sobreporem. Com a mesma receita, o mesmo modelo dá **96,72%** no
`test/` oficial e **99,92%** com o sorteio por imagem; 70% do teste sorteado veio do `train/`
original.

**Consequências:**

- os dois números do classificador descrevem dois cenários de uso, bloco já visto e bloco novo, e
  ambos vão para o TCC (**D19**);
- calibrar só no `train/` tem custo: um fenômeno que só exista num bloco que caiu inteiro no `test/`
  não aparece na calibração (**D17**). O mesmo fato torna a auditoria mais exigente;
- quem usar este dataset com divisão aleatória por imagem vai medir resultados otimistas. Isso
  está na seção 4.4 dos resultados do TCC e é candidato a nota curta (`reflexao.md`, seção 11);
- a divisão do Aluno (por sequência ou por sorteio) ficou com o Experimento 2, como trabalho futuro.

---

## Rochas movimentadas

Registro do autor durante a seleção das vagas (**D17**): rochas de padrão movimentado, em que é
mais difícil dizer o que é defeito e o que é desenho da pedra. A lista é observação do autor;
nenhuma das quatro teve a classificação petrográfica confirmada. O que se decidiu está na **D20**.

| Litologia | Situação | Anotada em |
|---|---|---|
| shadow_white | pulada em 03/10/2026, selecionada em 08/10 | 03/10/2026 |
| san_francisco_green | pulada em 07/10/2026, selecionada em 08/10 | 07/10/2026 |
| white_mirage | selecionada mesmo sendo movimentada | 07/10/2026 |
| golden_storm | selecionada mesmo sendo movimentada | 08/10/2026 |

As duas puladas foram selecionadas sem a opinião de especialista: a ajuda foi pedida na faculdade e
não veio, e a **D20** já dizia que ela não bloqueia. O autor registrou que a seleção delas foi
difícil. **Nenhuma litologia teve conferência de especialista**, nem as movimentadas, nem as
demais (Henrique, 23/11/2026). Os critérios escritos nos `calibracao.json` não foram retocados
para dizer isso: eles são o registro datado do que o autor escreveu ao calibrar.

O primeiro nome que o autor usou foi "exóticas". Em 07/10/2026 passou a ser **"movimentadas"**
(**D20**), porque "exótico" é categoria comercial (raridade e preço) e não descreve a dificuldade.

### Por que isto é um tópico, e não só um atraso

Nas rochas comuns, o autor olha a chapa e sabe o que marcaria. Nas movimentadas, o desenho natural
já tem manchas, veios e contrastes fortes, e a mesma feição pode valorizar uma chapa ou
desclassificá-la. A marcação depende mais de quem olha. A dúvida do autor, como ele a colocou em
07/10/2026: **não se sabe se é realmente possível marcar uma rocha dessas de forma correta.**

Onde isso encosta no desenho do trabalho:

- **D3:** é o caso-limite da fronteira arbitrária. Talvez a pergunta certa não seja "dá para marcar
  certo?", e sim "dá para escrever um critério que outra pessoa aplicaria igual?".
- **D17:** a vaga de descoberta e o limiar do autor dependem do julgamento dele, e nas movimentadas
  ele mesmo confia menos nesse julgamento.
- **D7:** a amostra da auditoria cobre as 11 rochas da faixa A, inclusive estas quatro. A
  concordância entre a avaliadora e o autor tende a ser menor aqui, e isso é medida da D3, não
  defeito da avaliação.
- **Resultado já em mãos (seção 4.5 do TCC):** a razão autor/regra não separa os grupos (mediana
  3,15 nas movimentadas contra 3,58 nas demais), mas os critérios escritos sim: "falta sonda" em 3
  das 4 movimentadas, contra 1 das 7 demais. A dificuldade está em **o que** marcar, não em
  **quanto**.

### Existe critério para "exótica"? Pesquisa de 07/10/2026

"Exótico" é palavra de mercado, sem critério mensurável. O conceito técnico que descreve a
dificuldade observada aqui é outro: rocha **movimentada**, em oposição a **homogênea**.

**"Exótico" no setor é categoria comercial, definida por lista e por valor.** Chiodi Filho (2007,
p. 37) fala nos *"denominados 'materiais exóticos', que abrangem granitos pegmatóides e pegmatitos,
granitos infiltrados (oxidados), quartzitos coloridos, rochas de derivação vulcânica, jaspes,
cherts, silexitos, conglomerados, brechas sedimentares e tectônicas, além de itabiritos e xistos
diversos"*: uma enumeração, não uma regra. O Informe ABIROCHAS 05/2018 trata as *"rochas exóticas,
de alto valor agregado"* (p. 6) como grupo de exportação, *"com destaque para pegmatitos e rochas
quartzíticas"* (p. 12), e diz que o Espírito Santo se destaca por *"granitos homogêneos,
especialmente amarelos, verdes e negros, bem como de mármores e alguns poucos materiais exóticos"*
(p. 30). Nenhuma fonte lida dá um limite ou um teste, e nenhuma fala em dificuldade de marcar.

**O critério técnico que existe: homogêneo × movimentado.** Meyer (2003), citado por Camargo, Artur
e Silveira (2015, p. 920): *"o padrão textural e estrutural classificam os materiais rochosos em
dois grupos: os homogêneos e os movimentados"*. Os homogêneos têm *"estruturas isotrópicas, sem
orientação mineral definida"*; os movimentados *"apresentam algum tipo de estrutura ou textura
definida pela concentração ou orientação preferencial de seus constituintes minerais"* (bandamento,
foliação, estruturas migmatíticas). É o que mais se aproxima do que o autor percebeu: a chapa tem
desenho próprio, e é esse desenho que se confunde com defeito. Ressalvas:

- a definição é petrográfica, escrita para granitos, e não é uma medida tirada da imagem;
- foi lida em segunda mão: a dissertação de Meyer não foi consultada (no TCC, a definição vai
  atribuída a Meyer via Camargo et al.);
- nenhuma fonte classifica `shadow_white`, `san_francisco_green` ou `white_mirage`. Sites de
  fornecedores descrevem o Verde San Francisco como granito de ondas e estrias intensas, o que bate
  com "movimentado", mas é texto de venda.

**Medir pela imagem é possível, mas não há régua pronta para chapa polida.** Há uma linha de
pesquisa em caracterização estética de chapas por análise de imagem (Univ. de Bolonha), com
variogramas e morfologia matemática, da qual só o resumo foi visto. Silva et al. (2025) propõem uma
medida de heterogeneidade textural por entropia, validada contra 4 especialistas em 175 amostras,
mas é microtomografia de rocha de reservatório: método análogo, não régua aplicável.

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
  Complexo Socorro (SP) e maciço Pedra Branca (MG).* Dissertação (Mestrado), UNESP Rio Claro, 2003.
  **Não consultada** (referência tirada de Camargo et al., 2015).
- SILVA, L. C. V. et al. *Entropy-based measure of rock sample heterogeneity derived from micro-CT
  images.* 2025 — <https://arxiv.org/abs/2502.01665>
- Caracterização estética de chapas por análise de imagem (Univ. de Bolonha), só resumo —
  <https://cris.unibo.it/handle/11585/60081>

> Os trechos entre aspas foram conferidos no texto dos PDFs em 07/10/2026. O que está marcado como
> "só resumo" ou "não consultada" não pode ser citado antes de ser lido.

---

## Sondas de detecção

Não são rótulos. São palavras escolhidas porque fazem o CLIP + SAM3 reagir a certas aparências; o
objetivo do conjunto é cobrir o máximo de regiões anômalas, não classificá-las (**D2**). O cadastro
(id e cor) mora em `AI/SAM/sondas.py` (**D8**).

| Sonda | Aparência que costuma disparar |
|---|---|
| `crack` | descontinuidades lineares finas e escuras |
| `vein` | estrias e faixas contrastantes |
| `Stain` | variação de cor em mancha difusa |
| `Dark patches` | regiões escuras sobre fundo claro |
| `light spot` | regiões claras sobre fundo escuro |
| `scratch` | riscos superficiais finos |
| `white stain` | manchas brancas que a `light spot` não pega |

Em quantas litologias cada sonda entrou está em `arquitetura.md`. A ideia antiga de que
`Dark patches` seria "para rochas claras" e `light spot` "para rochas escuras" foi desmentida pelas
calibrações da faixa A: quem decide é a imagem de descoberta de cada rocha, não a cor.

Por isso todas as regiões recebem `class_id = 0` no treino: o projeto não afirma que uma região
marcada por `crack` é uma fissura (**D2**). Multiclasse é trabalho futuro (**D12**).

---

## Agrupamento por cor (só registro)

Era o que a configuração antiga do `rock_prompts.json` seguia, antes de ela ser apagada
(09/10/2026). Nada no código usa isto. A calibração é **por litologia**, não por grupo de cor
(**D15**, 22/11/2026).

| Grupo | Litologias |
|---|---|
| Brancas / claras | white_bellukha, white_ceara, white_cintilante, white_everest, white_extreme, white_himalaya, white_liberdade, white_mirage, white_olympus, white_samoa, white_sea, white_serenata, white_superiore, itaunas_white, shadow_white, siena_white, vitoria_white, naica |
| Amarelas / bege / douradas | giallo_fiorito, giallo_maracana, golden_storm, icarai_yellow, maracuja_yellow, solarius, splendor_gold, santa_cecilia, santa_cecilia_light, ipanema_beige |
| Verdes / quartzitos | quartzito_green_da_vinci, quartzito_thannos, quartzito_venom, quartzito_verde_sauipe, san_francisco_green, new_caledonia, ubatuba_green |
| Escuras | nevada_black, sao_gabriel_black |
| Vermelhas | xango_red, tabaco_red |
| Especiais | kalahari, perla_venato, ornamental, rocky_mountain, olympios, ice_leke |

---

## Desafios do conjunto

1. **Desbalanceamento:** de 106 a 4.588 imagens por litologia. Reflete a realidade industrial e
   define a ordem de calibração.
2. **Variação dentro da mesma rocha:** muda com o bloco, a iluminação e o acabamento (ver
   *Sequência e blocos*).
3. **Fronteira arbitrária:** o que é defeito numa rocha é estética em outra. É o problema central do
   TCC (**D3**), não um ruído a contornar.
4. **Sem gabarito:** não há anotação humana preexistente. Daí a auditoria cega (**D7**).
5. **Texturas fora do padrão:** kalahari, ice_leke e quartzito_venom, além das movimentadas.

---

## Formato de anotação (saída do Professor, entrada do Aluno)

```
<class_id> <x1> <y1> <x2> <y2> ... <xN> <yN>
```

Coordenadas normalizadas (0 a 1), um polígono por linha, formato de segmentação do YOLO. Desde a
**D21**, cada contorno solto de uma detecção é uma linha própria.

> No único exemplo antigo (`AI/SAM/samples/ice_leke.txt`) são **107 polígonos numa imagem**, com até
> 1.742 pontos cada, gerados antes do protocolo atual. Treinar um Aluno exigiria pós-processamento
> (área mínima, teto de instâncias, simplificação), que ficou com o Experimento 2 (**D6**).
