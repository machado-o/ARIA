# Reflexão sobre o trabalho inteiro

Escrito em 25/11/2026, a pedido do Henrique, antes da fase de escrita. A ideia foi olhar o ARIA
de longe: de onde ele veio, por que cada decisão foi tomada, o que já temos e ainda não usamos,
e que ideias novas dá para tirar daqui.

Este arquivo não é fonte de verdade. As decisões ficam no `decisoes.md` e o estado do trabalho,
no `pendencias.md`. Aqui pode haver repetição, de propósito. Uma ideia daqui só vira decisão
quando o Henrique decide e ela é registrada lá.

Para saber o quanto confiar em cada coisa, uso quatro marcas:

- **[temos]**: o dado já existe e foi conferido;
- **[depois da auditoria]**: só se responde com os julgamentos;
- **[ideia]**: palpite ou proposta, sem dado ainda;
- **[decidido]**: já virou decisão registrada.

Um aviso honesto: quem escreveu isto ajudou a construir o trabalho e tende a gostar dele. Os
números novos foram calculados sobre os `calibracao.json`, que são dados de calibração (imagens
do `train/`). Nada do `test/`, do `itens.json` ou do `limiares.json` foi aberto.

---

## 1. A caminhada

O TCC começou em 20/05/2026. Em junho veio o artigo do PD1, escrito antes de quase todas as
decisões de hoje. Por isso existe a regra de que `apresentações/` não é fonte de verdade (D13).

A grande virada foi em 23/08. Nesse dia o projeto recomeçou: as imagens de calibração foram
apagadas, a numeração das decisões foi refeita, a startup saiu do texto (D1), o dataset passou a
ser descrito como público (D9) e, mais importante, o problema mudou. Antes era "detectar
defeitos melhor". Passou a ser "o critério do que é defeito não está escrito em lugar nenhum, e
vamos escrevê-lo" (D3).

Em 26/09 a regra do joelho foi fixada (D17), antes da primeira calibração. Na mesma data veio a
varredura sem GPU (D18) e a definição do braço único por regra, e não por média (D5). Foi isso que
tornou a H1 testável de verdade: ela pode dar errado.

Em 01/10 a primeira rocha foi calibrada, e o Henrique já subiu os três limiares acima da regra.
Entre 02 e 06/10 o Xception foi reproduzido e apareceu o vazamento do split (96,72% contra
99,92%). Em 07 e 08/10 surgiu a dúvida sobre as rochas movimentadas, se dá para marcá-las direito.
Em 09 e 10/10 vieram os contornos sem ponte (D21), o quarto braço (descoberto pelo próprio
Henrique, revisando) e a sonda `white stain`, criada porque faltava palavra.

Em 20/10 a faixa A ficou calibrada: o Henrique ficou acima da regra nas 45 sondas, e em 4 rochas
escreveu que pareciam faltar sondas. Em 22/10, a Jacitec. Em 06/11, a recusa da LatinoWare, com
um parecer pedindo exatamente o que faltava: testar a hipótese com dados. Em 19/11 a auditoria
cega substituiu o conjunto-ouro, e o pacote foi sorteado e congelado. Em 23/11 o Experimento 2
saiu, e o trabalho ficou com uma hipótese só.

O padrão dessa caminhada: toda vez que uma promessa era grande demais, ela foi trocada por uma
que dava para cumprir. "Reduzir falsos positivos" virou "tornar o critério explícito".
"Especialistas" virou "uma avaliadora de fora". "45 modelos" virou "trabalho futuro". Alguém pode
ler isso como mudar o alvo de lugar. A defesa é que cada mudança tem data, e a data é sempre
anterior ao resultado que poderia ter motivado a mudança.

---

## 2. A ideia central, e um detalhe bonito

Em uma frase: o ARIA não acaba com a arbitrariedade de decidir o que é defeito. Ele tira essa
decisão da cabeça do inspetor e a põe num arquivo que qualquer um pode ler, discutir e mudar com
registro.

O detalhe bonito **[temos]**: o jeito como o próprio TCC foi feito segue a mesma ideia. O
`decisoes.md` faz com as decisões de pesquisa o que o `calibracao.json` faz com os limiares. Cada
um guarda o valor escolhido, o porquê e a data. Quando algo muda, a versão antiga fica lá. Quando
algo estava errado, está escrito "estava errado". Isso cabe num parágrafo da metodologia e já
responde à pergunta "como sei que vocês não ajustaram tudo depois de ver o resultado?".

E quem é o "Professor", de verdade? No desenho é o SAM3. Mas quem diz ao SAM3 o que marcar é o
Henrique: 4 imagens, um slider por sonda e uma frase por rocha. O critério inteiro da faixa A coube
em 45 números e 11 frases. O SAM3 é a mão; o critério é humano. Dizer isso deixa claro que o
trabalho não "deixa a IA decidir o que é defeito".

---

## 3. As decisões, olhadas de novo

Para cada decisão importante: por que foi tomada, o que ganhou, o que custou sem que se
percebesse na hora, e como a banca pode questionar.

**Projeto separado da startup (D1).** Evitou conflito de interesse. Custo: perde o argumento "uma
empresa usa isto". Se perguntarem se alguém do setor usaria, a resposta vem da importância do
setor no ES, não da empresa.

**Sondas não são rótulos (D2).** Não se afirma o que não foi verificado; por isso o rótulo é um só
(anomalia). Custo: o nome `crack` continua soando como "trinca", e o leitor vai ler assim. A
resposta para "por que chamar de crack?" é que a palavra é a chave que faz o modelo reagir, não
uma descrição do que foi achado.

**O problema é a arbitrariedade (D3).** Nasceu de uma contradição: o texto antigo dizia que o ARIA
evitava marcar veio natural, e a sonda `vein` estava ligada em todas as rochas. Ganho: uma tese que
não depende de existir um gabarito perfeito. Custo: fica mais difícil mostrar uma vitória simples
em número.

**Braço único feito pela mesma regra (D5).** Evitou montar um adversário fraco de propósito e
evitou um resultado que sairia certo "por conta". Custo pouco lembrado: o "único" foi calculado
sobre as 11 rochas da faixa A, não sobre as 45. A legenda tem de dizer isso.

**Auditoria cega (D7).** Saiu porque desenhar polígonos à mão não tinha data para terminar. Ganho:
avaliação em horas, com uma pessoa de fora. Custo: não mede a borda das marcações e não enxerga o
que nenhuma sonda marcou (seção 6).

**Uma imagem de descoberta e três de limiar (D17).** Uma imagem só estava resolvendo dois problemas
que pedem imagens opostas. Custo: as sondas saem de uma chapa só, e o quarto braço existe para
medir quanto isso custa.

**A regra do joelho (D17).** É mecânica e igual para todas as rochas. Custo: ela só olha o formato
da curva de contagem, não o que está sendo marcado. Daí o Henrique ter discordado dela nas 45
sondas (seção 4).

**Calibrar as movimentadas mesmo assim (D20).** Tirá-las exigiria um critério de exclusão que não
existe. Custo: quem disse que são movimentadas foi o Henrique, e isso é declarado.

**Experimento 2 para o futuro (D6).** Sem um gabarito para o YOLO, medi-lo contra o próprio SAM só
mostraria que ele copia bem. Custo: o título fala em pseudo-rotulagem e o Aluno não foi treinado.
A resposta é que o Professor gera os rótulos, e treinar o Aluno é o passo seguinte.

Um custo escondido que merece uma frase no texto **[temos]**: o calibrador abre cada sonda no valor
da regra, e o Henrique partiu sempre dali para cima. Em psicologia isso se chama ancoragem
(Tversky e Kahneman, 1974): quem começa num número tende a ficar perto dele. Isso quer dizer duas
coisas. A diferença de 3,3 vezes provavelmente seria maior sem a âncora, o que fortalece o
resultado. E a semelhança entre os dois limiares (item 4.1) pode ser, em parte, efeito da âncora.

---

## 4. O que já temos e o texto ainda não usa

### 4.1 A regra acerta a ordem, só erra a escala [temos]

Uma comparação ajuda: um termômetro em Celsius e outro em Fahrenheit mostram números diferentes,
mas concordam sobre qual dia foi mais quente. A regra e o Henrique são assim. Nas 45 sondas, os
limiares dos dois andam juntos (correlação de 0,71, calculada nos logaritmos), mas os do Henrique
ficam em torno de 3 vezes acima.

Então a leitura da seção 4.5 do TCC pode mudar. Em vez de "a regra errou 45 vezes", fica "a regra
acha a posição de cada sonda, e o humano define o nível". Para quem não conhece o trabalho, o que
convence é um gráfico de pontos: o limiar da regra num eixo, o do Henrique no outro, e os 45
pontos formando uma faixa inclinada. Dá para fazer só com dados de calibração.

Cuidados: a âncora (seção 3) explica parte disso; metade da variação do limiar do Henrique a
regra não prevê (a razão vai de 1,08 a 17,9); e a conta foi feita depois de ver os dados, então
entra como descrição, não como previsão confirmada.

As sondas que o Henrique mais corrigiu foram as de mancha clara: `white stain` (4,8 vezes, na
mediana) e `light spot` (4,5). As que ele menos corrigiu: `vein` (2,3) e `scratch` (2,6).

### 4.2 A imagem típica virou um "aqui não pode marcar nada" [temos]

No limiar do Henrique, a imagem típica ficou sem nenhuma marcação em 22 das 45 sondas. A sutil
ficou vazia em 11 e a forte, em 13. A ideia original era que as três imagens fossem um júri com o
mesmo peso. Na prática, a típica fez outro papel: dizia "não marque a pedra limpa". As outras duas
conferiam se o óbvio continuava sendo marcado.

O Henrique explicou o motivo: depois do beneficiamento, a maioria das chapas tem poucos defeitos.
A típica é limpa porque a chapa comum é limpa. E mesmo para ele é difícil dizer, às vezes, se algo
deveria ser marcado, o que pede uma conversa com gente da área (ideia F, seção 7).

Daí sai uma regra alternativa **[ideia]**: "o menor limiar em que a típica fica com no máximo k
marcações". Ela usa o papel de cada imagem, e não só o formato da curva. Como foi pensada depois de
ver os dados, não pode entrar no lugar da regra atual. Serve como trabalho futuro ou como análise
exploratória (seção 5).

### 4.3 Por que o critério único dá tão errado [temos]

É como a média do número do sapato da família inteira: o tamanho que sai não serve para ninguém.
Quando a regra roda sobre as 11 rochas misturadas, a curva perde o "cotovelo" e o joelho desliza
para perto de zero. Para `crack` ele cai em 0,0071, e para `Dark patches`, em 0,0167. O braço único
acaba marcando 362 regiões por chapa.

O TCC já mostra esses números, mas não explica por que acontece. E a explicação mostra uma coisa
que não depende de nenhum julgamento humano: as rochas são diferentes **para o próprio modelo**.
O limiar da regra para `crack` vai de 0,018 a 0,179 entre as rochas, dez vezes de diferença. Mesmo
que a auditoria não favoreça o calibrado, isso continua verdade.

### 4.4 Números redondos [temos]

6 dos 45 limiares do Henrique são números redondos digitados: 0,5 três vezes, 0,7, 0,35 e 0,2. Às
vezes ele não procurou o melhor valor, parou num que estava bom. O economista Herbert Simon (1956)
chamou isso de *satisficing*. Não é erro, é o jeito humano de decidir, e reforça a D3. Cabe numa
frase, se houver espaço.

### 4.5 "Algo que só a IA entende" [temos]

No critério da `ipanema_beige`, o Henrique anotou que precisou **baixar** o limiar para pegar a
marcação **óbvia** da chapa forte. Ou seja, a confiança do SAM3 não acompanha o que salta aos olhos
de uma pessoa. O TCC já diz que o score não é uma probabilidade de verdade. Este é o exemplo
concreto, e a auditoria permite medir isso (seção 5).

### 4.6 O vazamento do split [temos, já está no TCC]

Está na seção 4.4 dos resultados, com os dois números e a explicação: no sorteio por imagem,
chapas vizinhas do mesmo bloco caem no treino e no teste. O que dá para melhorar é o destaque: hoje
aparece como resultado do classificador. Pode virar também um aviso explícito para quem usa esse
dataset do Kaggle, numa frase da conclusão. Com tato: são dois cenários de uso (bloco conhecido e
bloco novo), não um erro de quem veio antes.

### 4.7 Problemas encontrados em bibliotecas [temos]

Três coisas que poderiam virar avisos para os projetos abertos:

- no timm 1.0.27, o `legacy_xception` calcula o dropout e joga o resultado fora;
- no ultralytics, o SAM3 chama o tokenizador do CLIP de um jeito que falha sem dar erro nenhum;
- no ultralytics, o `masks.xyn` junta contornos separados com "pontes". É escolha de projeto, não
  defeito, mas atrapalha rótulos de segmentação.

Antes de reportar, conferir se ainda acontece na versão atual de cada uma.

### 4.8 O `calibracao.json` também é um dado [temos]

São 45 pares com o valor da regra, o valor do Henrique, a contagem por imagem e uma frase
explicando. É raro ter isso: um registro de como uma pessoa corrige uma regra automática, e por quê.
Vale dizer no texto que esse registro também é um resultado do trabalho.

---

## 5. A auditoria: quem ganha, e o que ela responde de brinde

### 5.1 Quem ganha [decidido em 25/11/2026]

Faltava dizer o que acontece se a precisão apontar para um lado e o recall para o outro. É o caso
mais provável: o braço único marca 11.964 regiões e o `regra_todas`, 7.289. Quem marca mais tende a
pegar mais defeitos e também a errar mais.

As duas medidas, em palavras simples:

- **precisão**: das coisas que o braço marcou, quantas eram defeito?
- **recall relativo**: dos defeitos que algum braço encontrou, quantos este pegou?

Um braço que marca uma coisa só, e acerta, tem 100% de precisão e um recall minúsculo. Por isso
uma medida sozinha não basta.

A regra escolhida, registrada no `decisoes.md` (emenda da D4) antes de qualquer julgamento:

1. só ganha quem é melhor numa medida sem ser pior na outra;
2. se cada braço ganhar numa, a precisão desempata, e a troca aparece em números no texto;
3. se não houver diferença em nenhuma, a H1 não se confirma, e o texto mostra o intervalo de
   confiança.

Por que a precisão desempata: as marcações viram material de treino, e a rede decora o que estiver
errado. E, como o Henrique observou, defeito é raro, e com coisa rara quem marca muito erra quase
sempre. É como um alarme de incêndio que toca toda semana.

Um detalhe que vale escrever no TCC: como o Henrique ficou acima da regra nas 45 sondas, os braços
se encaixam um dentro do outro. Tudo o que o braço `autor` marca, o `regra_autor` também marca; e
tudo o que o `regra_autor` marca, o `regra_todas` também. Então é óbvio que o recall cai de um para
o outro, isso não é descoberta. A pergunta interessante nessas comparações é quanta precisão se
ganha por cada pedaço de recall perdido. Só o par `unico` × `regra_todas`, o teste da H1, tem as
duas medidas em aberto.

### 5.2 Perguntas que a auditoria responde de graça [depois da auditoria]

Todas usam os mesmos julgamentos, sem pedir nada a mais da Marcelli. Ficaram registradas na mesma
emenda, como exploratórias, para que não pareçam pescaria nos dados depois.

- **A confiança do SAM3 bate com o "sim" humano?** Se não bater, fica explicado por que o limiar
  precisa de uma pessoa (item 4.5).
- **Você e a Marcelli colocam os braços na mesma ordem?** Em sistemas de busca, Voorhees (2000)
  mostrou que avaliadores discordam bastante em itens soltos, mas costumam concordar sobre qual
  sistema é melhor. Se acontecer aqui, a conclusão da H1 não depende de quem julgou.
- **O kappa é menor nas movimentadas?** É o teste mais direto de que a arbitrariedade cresce quando
  a pedra tem desenho próprio.
- **O "não sei" aparece mais nas movimentadas?** O script conta o "não sei" mas o descarta. A taxa
  dele já é uma medida de onde fica difícil julgar.
- **A zona cinzenta.** Entre o limiar da regra e o do Henrique ficam marcações que a regra aceita e
  ele recusou. Previsão: é ali que vão se juntar os "não sei" e as discordâncias.
- **Uma curva inteira de limiares.** Como os braços se encaixam, qualquer limiar entre o da regra e
  o do Henrique gera marcações que já foram julgadas. Dá para estimar a precisão de vários limiares,
  e não só dos quatro braços: o do Henrique ficou perto do melhor ponto? Existe um fator único que
  funcione em todas as rochas? Os intervalos vão ser largos, porque cada estrato tem 60 itens.
- **Precisão por sonda.** Palpite: a `Dark patches` erra mais. Em todas as rochas em que entrou, o
  Henrique a pôs acima de 0,26, o piso mais alto entre as sondas, como se ela reagisse ao desenho da
  própria pedra.
- **Quanto do critério é gosto pessoal.** A precisão do braço `autor` julgada pelo Henrique contra a
  julgada pela Marcelli. A diferença mede quanto do limiar dele vale para outra pessoa.
- **Quanto erro o Henrique tolera.** Com a curva "confiança × sim", dá para calcular algo como "no
  limiar dele, para cada X defeitos encontrados ele aceitava 1 marcação errada". Em economia isso é
  preferência revelada: a escolha mostra um valor que ninguém disse em voz alta.

---

## 6. O que a auditoria não consegue ver

A avaliadora só julga o que alguma sonda marcou. Um defeito que nenhuma palavra fez o SAM3 achar
nem aparece na tela. Então a auditoria não testa a hipótese do vocabulário (a ideia de que faltam
palavras para nomear o que a natureza e o beneficiamento produzem).

Para o TCC isso basta: a hipótese fica apoiada nos critérios escritos do Henrique (4 das 11 rochas),
na criação da `white stain` e no "o que, e não quanto" da seção 4.5. Uma forma honesta de dizer:

> O limiar resolve o "quanto"; a palavra limita o "o quê". E esse limite aparece mais nas rochas
> que têm desenho próprio.

---

## 7. Ideias novas

Aqui o objetivo foi arriscar. Algumas são fortes, outras são só faíscas.

**A. Chapas vizinhas são fatias do mesmo bloco [ideia, a mais original].** Os arquivos seguem a
ordem do corte, e já foi medido que imagens seguidas são parecidas. Um veio da chapa 100 deve
aparecer quase no mesmo lugar na 101. Um risco de polimento, não, porque nasce em cada chapa. Daí
sai um teste sem gabarito: o que continua de uma chapa para a outra é da pedra; o que some é do
beneficiamento, ou invenção do SAM. Isso encosta direto na pergunta da D3, feição natural ×
defeito. Antes de qualquer coisa, conferir se as fotos estão alinhadas o bastante para comparar
posições.
*Henrique (25/11):* uma mudança brusca também pode ser troca de bloco. Então o teste só vale
dentro de um mesmo bloco, e o salto de semelhança entre imagens seguidas (já medido: 4,0 entre
vizinhas, 12,5 entre sorteadas) serviria primeiro para achar onde um bloco termina.

**B. Defeito é uma relação, não uma propriedade da chapa [ideia].** A mesma chapa tem defeito para
um cliente e não tem para outro. O arquivo de limiares poderia ser o perfil de cada cliente: o
comprador manda o critério dele e o sistema marca de acordo. A arbitrariedade deixa de ser problema
e vira uma função do sistema. Boa frase para a conclusão.
*Henrique (25/11):* o mercado resiste a pensar assim, porque esses "defeitos" mudam o preço da
chapa. Uma saída é o perfil do cliente apontar para as classes comerciais que o setor já usa, em
vez de dizer "para você isto não é defeito".

**C. Mostrar em vez de dizer [ideia].** Quando falta palavra, o SAM3 também aceita um exemplo
visual: você aponta "isto aqui" e ele procura coisas parecidas. Seria o caminho natural para o
"parece faltar sonda". Wittgenstein tem uma frase sobre isso: o que não se pode dizer, se pode
mostrar. Falta conferir se a versão do ultralytics usada aceita esse tipo de entrada.
*Henrique (25/11):* isso já foi tentado e pareceu marcar pior. Fica para um trabalho futuro mais
aprofundado. Esse resultado negativo ainda não está registrado em nenhum documento (quando, em
que rocha, como foi comparado), e vale uma linha no `pendencias.md`.

**D. O Henrique consegue repetir o próprio critério? [temos um pouco, o resto é ideia].** Já existe
um começo: a `siena_white` foi recalibrada uma semana depois, e a `Stain` foi de 0,414 para 0,392,
quase igual. Recalibrar 2 ou 3 rochas de novo, sem olhar os valores antigos, mediria se a mesma
pessoa é coerente com ela mesma. Junto com o kappa, a arbitrariedade fica dividida em duas partes:
entre pessoas, e dentro da mesma pessoa ao longo do tempo. Custa uns 30 minutos e usa só o `train/`.
*Henrique (25/11):* descartada. Com as mesmas imagens, a mesma mentalidade e o slider partindo da
marcação da IA, o resultado seria o mesmo. O caso da `siena_white` já basta como uma frase.

**E. A zona cinzenta [depois da auditoria].** Já descrita na seção 5.2. Se as discordâncias se
concentrarem entre os dois limiares, a regra e o humano estão marcando as duas pontas da mesma
faixa de dúvida.
*Previsão do Henrique (25/11, antes dos julgamentos):* a Marcelli deve marcar menos coisas como
defeito do que ele. Se acontecer, a precisão de todos os braços cai quando julgada por ela, mas a
ordem entre os braços pode continuar a mesma (seção 5.2).

**F. O especialista só olha o difícil [ideia].** Em vez de pedir a um geólogo que veja tudo, mandar
só os itens em que o Henrique e a Marcelli discordaram ou responderam "não sei". Gasta pouco tempo
dele, exatamente onde o julgamento dele faz diferença.

**G. Quanto esforço humano o ARIA pede [temos].** O FracStoneAI desenhou polígonos à mão em 1.088
imagens de 4 rochas. O ARIA definiu o critério de 11 rochas com 44 imagens, 45 números e 11 frases.
Não é a mesma coisa, porque a qualidade das marcações do ARIA ainda vai ser medida. Mas a diferença
de esforço é enorme e merece uma frase.
*Henrique (25/11):* "foi realmente muito mais fácil chegar a algum lugar usando uma IA para gerar
as marcações". Entra no texto como esforço, não como qualidade, até a auditoria medir a qualidade.

**H. Contar o que ninguém achou [ideia].** A ecologia estima quantos peixes há num lago capturando,
marcando, soltando e capturando de novo: a sobreposição entre as duas capturas diz o tamanho total
(captura-recaptura). A engenharia de software usa o mesmo truque para estimar quantos bugs dois
revisores deixaram passar. Aqui, a sobreposição entre sondas diferentes daria uma estimativa dos
defeitos que nenhuma sonda viu. É aproximada, porque as sondas não são independentes, mas é um jeito
de dar número à hipótese do vocabulário.

**I. O CLIP fala o inglês da internet; o inspetor fala o português da pedreira [ideia].** Os nomes
que o setor usa para cada defeito talvez não tenham uma tradução que o modelo entenda. Um glossário
do setor, traduzido e testado como sonda, seria um trabalho futuro concreto.
*Henrique (25/11):* o ideal seria um SAM treinado para entender conceitos geológicos, feito por
um engenheiro de IA junto com quem conhece rocha. O ARIA pode ser o primeiro passo desse caminho:
as marcações do Professor revisadas por especialistas viram o conjunto de dados para ensinar o
próprio modelo de fundação. Isso fecha um ciclo com o aprendizado ativo (D11).

**J. Regra × padrão [leitura, a que eu mais recomendo].** No direito existe uma distinção antiga
(Kaplow, 1992). Uma regra é escrita antes: "velocidade máxima de 80 km/h". Um padrão é julgado caso
a caso: "dirija com prudência". O inspetor trabalha por padrão. O ARIA transforma isso em regra.
Ganha-se previsibilidade e a chance de conferir depois; perde-se nos casos de fronteira. É uma troca
conhecida e estudada, e isso dá peso à tese.

**K. Sabemos mais do que conseguimos dizer [leitura].** É a frase de Polanyi (1966) sobre
conhecimento tácito, e é quase o que os critérios dizem com "parece faltar sonda": o Henrique sabe o
que marcaria, mas não tem a palavra. Fica bem como uma frase na conclusão, não como argumento.

**L. A regra olha a forma; a pessoa olha o conteúdo [leitura].** O joelho vê o formato da curva de
contagem. O Henrique vê se o que foi marcado é pedra limpa ou não. Nenhuma regra que só conta
marcações consegue saber se a coisa contada é defeito, porque "defeito" não está na contagem. Isso
vale para qualquer escolha automática de limiar sem gabarito.

**M. O preço de escrever o critério [leitura].** Escrever o critério o deixa visível, mas também o
congela. O inspetor ajusta o julgamento ao cliente e ao lote; o arquivo, não. É a crítica filosófica
mais forte à tese. A resposta: o arquivo pode mudar, só que muda com registro. E o registro regra ×
autor mostra que o julgamento humano continua lá, agora visível.

Nenhuma dessas leituras deve ser citada sem ler a fonte. E vale usar no máximo duas no texto, para
não virar ensaio.

---

## 8. As contribuições, da mais firme para a menos

1. O protocolo de calibração, com regra fixa, separação descoberta/limiar e critério escrito (D17).
   Já no texto.
2. A prova de que varrer o limiar sem GPU dá exatamente o mesmo resultado (D18), em duas versões da
   biblioteca. Já no texto.
3. A divergência regra × autor: 45 de 45, cerca de 3,3 vezes. Já no texto.
4. O critério único desaba quando as rochas são misturadas, o que mostra que elas são diferentes
   para o modelo (4.3). O número está no texto; o porquê, não.
5. O vazamento do split no dataset público (4.6). No texto, com pouco destaque.
6. O desenho de uma auditoria barata: um julgamento vale para todos os braços que contêm a
   marcação, e qualquer começo da lista já é amostra válida. Está descrito, mas não é apresentado
   como contribuição, e serviria a outras pessoas.
7. A regra acerta a ordem, o humano define a escala (4.1). Fora do texto.
8. O registro de calibração como dado sobre julgamento humano (4.8). Fora do texto.
9. O "o que, e não quanto" nas rochas movimentadas. No texto, apoiado em 4 critérios escritos.
10. A H1, quando a auditoria for julgada.

---

## 9. Perguntas que a banca deve fazer

- *"A hipótese mudou três vezes."* Sempre antes do dado que poderia motivar a mudança, e cada
  mudança tem data no `decisoes.md`.
- *"O autor calibrou e também julgou."* Por isso a referência é a Marcelli. A diferença entre os
  dois é medida, e isso é parte do resultado.
- *"Por que não desenhar polígonos?"* Custava tempo sem prazo, e a H1 compara braços, o que a
  auditoria responde.
- *"Recall relativo não é recall."* Certo, e o texto diz isso. Ele serve para ordenar os braços.
- *"Se o autor rejeitou a regra 45 vezes, a regra não serve."* Ela acerta a ordem (4.1) e é o
  controle mecânico que torna visível o ajuste humano.
- *"O critério único foi feito para perder."* Ele usa a mesma regra, muda só o conjunto de dados, e
  o desenho aceita que o resultado seja negativo.
- *"Três chapas por rocha bastam?"* Para comparar braços nas mesmas chapas, sim, e o intervalo de
  confiança mostra a incerteza.
- *"Calibrou no `train/` e testou num `test/` que pode ser de outro bloco. Não é injusto?"* É mais
  exigente, não injusto: mostra se o critério funciona em chapas que a calibração não viu.
- *"Por que a `white stain` não entrou justamente na rocha em que nasceu?"* Ainda sem resposta
  escrita. Falta uma frase do Henrique.

---

## 10. Coisas desatualizadas encontradas nos documentos

Todas foram corrigidas na reorganização dos documentos de 25/11/2026: a §3.3 das diretrizes (dois
experimentos), a D4 (a H2 sem aviso de que saiu), a D5 ("vem antes do Experimento 2"), o título das
faixas no `dataset.md`, o Aluno no presente no `arquitetura.md`, a Fase 2/3 do `roadmap.md` e o
`README.md`, que ainda descrevia dois experimentos e cinco sondas.

Continua aberta só uma, no TCC: a metodologia não diz como a H1 é decidida. A regra já está
registrada (emenda de 25/11 na D4) e falta passá-la para o texto (`pendencias.md`, seção da
auditoria).

---

## 11. Publicação até fevereiro de 2027

1. **O artigo principal**: critério escrito, regra × autor e a H1 com a auditoria. É o TCC resumido,
   e responde à principal crítica da LatinoWare. Depende dos julgamentos.
2. **Uma nota curta sobre o vazamento do split** no dataset do Kaggle: duas tabelas e um argumento.
   Não depende de nada que falta. Pede cuidado com quem veio antes (mesmo grupo e mesmo orientador);
   talvez convidá-los, em vez de corrigi-los.
3. **O método** (varredura sem GPU, calibrador, auditoria) como artigo de ferramenta. Fraco sozinho,
   forte como parte do primeiro.

Qual revista ou evento, e se o Rafael topa, é conversa do Henrique com ele.

---

## 12. Próximos passos sugeridos

1. Mandar o `.zip` para a Marcelli.
2. Pôr na metodologia do TCC a regra de quem ganha a H1 (seção da auditoria no `pendencias.md`).
3. Na escrita, pelo ganho de cada coisa: o porquê de o critério único desabar (4.3); a regra acerta
   a ordem, com o gráfico de pontos (4.1); uma frase sobre a âncora (seção 3); os braços que se
   encaixam (5.1); o trabalho que segue a própria ideia (seção 2); no máximo uma leitura conceitual
   (J); a frase sobre a `white stain`.
4. Corrigir os documentos da seção 10.
5. Depois da auditoria: as análises da seção 5.2, começando pela ordem dos braços entre os dois
   avaliadores e pela curva de limiares.
6. Se sobrar tempo: recalibrar 2 ou 3 rochas às cegas (D), os avisos para as bibliotecas (4.7) e a
   nota sobre o vazamento.
