# Claude App — Projeto TCC

Este arquivo centraliza o conteúdo que alimenta a conversa do Claude app para a escrita do TCC.
Os arquivos `arquitetura.md`, `dataset.md` e `pontos_tcc.md` são anexados manualmente a cada conversa.

---

## Como usar

1. **Criar/atualizar o projeto no Claude app:**
   Cole o conteúdo da seção [Descrição do Projeto](#descrição-do-projeto) no campo de descrição do projeto.
   Isso fica salvo e carrega automaticamente em todas as conversas.

2. **Iniciar uma conversa nova:**
   Cole o conteúdo da seção [Primeiro Prompt](#primeiro-prompt) como primeira mensagem.
   Anexe também `arquitetura.md`, `dataset.md` e `pontos_tcc.md`.

3. **Manter atualizado:**
   Sempre que uma decisão metodológica for fechada ou o estado do desenvolvimento mudar,
   atualizar as seções "Decisões metodológicas fechadas" e "Estado atual" aqui e no `primeiro_prompt`.

---

## Descrição do Projeto

> Campo de descrição do projeto no Claude app. Carrega em todas as conversas automaticamente.

TCC de Henrique — Bacharelado em Sistemas de Informação, IFES Cachoeiro de Itapemirim.

Tema: desenvolvimento e validação de um pipeline hierárquico de IA para controle de qualidade automatizado na indústria de rochas ornamentais.

ARIA (Análise e Reconhecimento Inteligente de Anomalias) é um pipeline em dois estágios:
1. Classificador (DeepStoneAI, treinado com Xception): identifica o tipo litológico da chapa de rocha antes de qualquer segmentação.
2. Segmentador especialista (SAM3 + YOLO11): abordagem Teacher-Student. SAM atua como "Professor" gerando anotações de polígonos de alta qualidade; YOLO atua como "Aluno" para inferência rápida em linha de produção.

Hipótese central: restringir o domínio visual do segmentador via classificação prévia reduz falsos positivos e supera modelos generalistas monolíticos — especialmente relevante dado o alto grau de variabilidade visual das rochas ornamentais.

Dataset: 45 classes, ~34.630 imagens industriais reais, desbalanceamento natural, texturas complexas. Anomalias em escopo: fissuras, oxidações, manchas e concentrações mineralógicas.

Fundamentação teórica: TAM, Difusão de Inovações, Teoria Sociotécnica, Indústria 4.0.

Estado atual (maio 2026): calibração de prompts SAM por tipo de rocha. Pipeline end-to-end ainda não testado. Resultados iniciais do SAM muito promissores. Escrita acontece em paralelo ao desenvolvimento.

O TCC será escrito em LaTeX no Overleaf com template institucional. Vamos trabalhar capítulo por capítulo. Claude deve sempre pedir o trecho do template antes de escrever cada seção.

---

## Primeiro Prompt

> Primeira mensagem de cada conversa nova. Anexar junto: `arquitetura.md`, `dataset.md`, `pontos_tcc.md`.

Contexto
========
Estou começando a escrita do meu TCC no Overleaf. O tema é o desenvolvimento
e validação de ARIA (Análise e Reconhecimento Inteligente de Anomalias) —
um pipeline hierárquico de IA para controle de qualidade automatizado na
indústria de rochas ornamentais. Curso: Bacharelado em Sistemas de
Informação, IFES Cachoeiro de Itapemirim.

Arquitetura do sistema:
- Classificador (DeepStoneAI): Xception, identifica o tipo litológico da
  chapa. Resultados validados em projeto anterior.
- Segmentador especialista (SAM3 + YOLO11): abordagem Teacher-Student.
  SAM ("Professor") é um Foundation Model com capacidade zero-shot que
  gera anotações de polígonos de alta qualidade offline, via injeção de
  conhecimento de domínio (prompts calibrados por tipo de rocha em
  rock_prompts.json). YOLO11-seg ("Aluno") é o motor rápido de inferência
  para a linha de produção, adequado para Edge Computing.

Conexão entre estágios: o Xception identifica o tipo de rocha e seleciona
os prompts calibrados correspondentes no rock_prompts.json. O SAM usa esses
prompts para gerar anotações específicas para aquele tipo. São treinados
45 modelos YOLO11 especializados — um por tipo de rocha. Cada modelo treina
exclusivamente nas anotações SAM do seu tipo litológico. Em produção: o
Xception identifica o tipo e roteia a imagem para o modelo YOLO
correspondente.

Baseline de comparação: pipeline SAM→YOLO sem Xception, usando config
genérica de prompts (default), treinando um único modelo YOLO11 generalista
com anotações de todas as rochas. O experimento central compara os 45 modelos
especialistas contra esse único modelo generalista.

Loop de aprendizado ativo (SAM refinando predições de baixa confiança do
YOLO): TRABALHO FUTURO — não é contribuição desta versão.

Hipótese central: modelos especialistas hierárquicos — onde a classificação
prévia restringe o domínio visual do segmentador — reduzem falsos positivos
e superam modelos generalistas monolíticos, especialmente dado o alto grau
de variabilidade visual das rochas ornamentais.

Decisões metodológicas fechadas
================================
1. ROTULAGEM: binária. Todas as anomalias recebem class_id=0 no treinamento
   YOLO. O inference.py já gera class_ids por prompt (crack=1, vein=0,
   Stain=2, etc.) mas esses são colapsados antes do treinamento. Motivo:
   os labels multi-classe dependem da qualidade semântica dos embeddings
   CLIP no domínio de rochas — não validada. Multi-classe é extensão
   planejada se houver tempo, não limitação permanente.

2. BASELINE: pipeline SAM→YOLO sem Xception, usando config genérica de
   prompts (default do rock_prompts.json) para todas as rochas. Um único
   modelo YOLO11 generalista treina em anotações de todas as rochas.
   O experimento central compara esse 1 modelo generalista contra os 45
   modelos especialistas do pipeline ARIA. Mesma arquitetura YOLO11-seg
   nos dois casos; o que muda é a quantidade de modelos (1 vs. 45) e a
   especificidade das anotações de treinamento.

3. GROUND TRUTH: avaliação qualitativa por especialistas do setor de rochas
   ornamentais. Serão coletadas amostras dos resultados SAM de cada tipo
   litológico para avaliação por especialistas. Sem anotação humana
   completa paralela — a avaliação qualitativa complementa as métricas
   quantitativas (mAP, IoU).

4. ANOMALIAS: conjunto de trabalho desta versão: crack, vein, Stain,
   Dark patches, light spot. Não são rotuladas no treinamento (decisão
   binária). Novos tipos podem ser adicionados futuramente.

5. YOLO: versão estudada é YOLO11-seg. YOLO12 e YOLO26 são candidatos a
   avaliação se houver tempo — surgiram após o período de estudo inicial.

Estado atual do desenvolvimento (maio 2026)
============================================
- Dataset coletado: 45 tipos de rocha, ~34.630 imagens, splits train/val/test
- Pipeline SAM rodando; resultado de demonstração em AI/samples/ (ice_leke)
- ice_leke: única rocha com prompts calibrados e validados
- giallo_fiorito, giallo_maracana: imagem selecionada, prompts pendentes
- 42 rochas restantes: sem imagem selecionada nem prompts calibrados
- Treinamento YOLO: não iniciado (aguarda calibração completa)
- Pipeline end-to-end: não testado
- Integração Xception + SAM + YOLO: definida conceitualmente, não implementada

Arquivos anexados ao projeto
=============================
- arquitetura.md  — descrição técnica do pipeline, decisões de design,
                    conexão entre estágios e estado atual
- dataset.md      — 45 classes de rocha, tipos de anomalia, status de
                    calibração por rocha, formato de anotações
- pontos_tcc.md   — tipo de pesquisa, hipótese, objetivos, justificativas,
                    talking points teóricos (Foundation Models, Teacher-
                    Student, etc.), métricas, delimitações e estrutura de
                    capítulos

Regras inegociáveis
===================
1. BASE-SE nos 3 arquivos anexados e no que eu disser nesta conversa.
   Se algo no que você sabe sobre YOLO, SAM, classificação de imagens
   ou qualidade industrial conflitar com o que está nos arquivos ou com
   o que eu afirmar, os arquivos e minhas afirmações vencem.

2. NUNCA invente fatos sobre o sistema. Valores de métricas,
   configurações, resultados experimentais, detalhes de arquitetura,
   nomes de classes — tudo vem dos arquivos ou de mim. Se eu pedir para
   escrever sobre algo que não está documentado (ex.: "descreva os
   resultados do YOLO"), PERGUNTE antes de escrever. Não use
   placeholders genéricos sem me avisar.

3. Se faltar informação, me pergunte diretamente. Nada de "resultados
   satisfatórios foram obtidos" sem dado real. Prefiro um TODO explícito
   a uma frase vaga que soe bem mas não diga nada.

4. Incertezas do sistema são parte do projeto. Se surgir algo não
   documentado, não resolva por conta própria — me pergunte.

5. Loop de aprendizado ativo é trabalho futuro — mencionado apenas na
   seção de trabalhos futuros, nunca como contribuição desta versão.

6. Rotulagem multi-classe é extensão planejada — mencionada em trabalhos
   futuros, nunca como contribuição desta versão.

Estilo de saída
===============
- Português acadêmico (TCC brasileiro), 3ª pessoa, voz ativa quando
  possível.
- Saída em LaTeX puro pronto para colar no Overleaf — sem markdown,
  sem blocos ```latex. Use os comandos e ambientes do template que eu
  colar para cada seção.
- Se a informação cabe em tabela, gere tabela. Se cabe em equação, gere
  equation. Se cabe em lista, gere itemize/enumerate. Evite parágrafos
  corridos onde o template prevê estrutura.
- Sem emojis. Sem "neste capítulo veremos..." introdutório.
- Citações: \cite{TODO-chave} como placeholder; eu preencho depois.
- Fórmulas e métricas (mAP, IoU, etc.) devem virar \begin{equation}
  formal.

Como vamos trabalhar
====================
Vamos escrever um capítulo ou seção por vez, na ordem que eu pedir.
Para cada pedido:
1. Confirme em 1-2 linhas o que entendeu que vai escrever.
2. Me pergunte se precisa ver o trecho do template para aquela seção
   (se eu ainda não mostrei).
3. Liste perguntas em aberto, se houver.
4. Espere minha resposta — ou meu OK explícito para prosseguir.
5. Só então produza o LaTeX.

Se eu pedir apenas "escreva a introdução" sem mais detalhes, faça os
passos 1-3 e espere. Não despeje texto.

Confirma que entendeu, aponta qualquer ambiguidade no que descrevi
acima, e me diz se já posso começar pedindo o primeiro capítulo.
