# Pontos do TCC — ARIA

Arquivo de talking points, argumentos centrais, justificativas e perguntas em aberto.
Atualizar conforme o TCC avança.

---

## Problema de Pesquisa

**Pergunta central:**
Uma abordagem hierárquica — onde a classificação taxonômica prévia restringe o domínio visual do segmentador — reduz falsos positivos na detecção de anomalias superficiais em rochas ornamentais em comparação a modelos generalistas monolíticos?

**Problema prático (três frentes):**
1. **Subjetividade da inspeção humana:** A inspeção manual depende da acuidade visual do operador, sendo subjetiva, propensa à fadiga e de difícil padronização.
2. **Variabilidade geológica:** Rochas ornamentais têm texturas extremamente variadas. Um modelo generalista confunde veios naturais de granito com fissuras em mármore branco, ou oxidação em quartzito verde com mancha em rocha clara.
3. **Custo e inviabilidade da anotação manual em escala:** A criação de datasets rotulados manualmente para milhares de imagens com defeitos sutis é um processo oneroso e limitante para a indústria.

---

## Hipótese Central

**H1:** Modelos especialistas hierárquicos (classificar → segmentar no domínio restrito) apresentam menor índice de falsos positivos do que modelos generalistas monolíticos para detecção de anomalias superficiais em rochas ornamentais.

---

## Tipo de Pesquisa

**Classificação:** Pesquisa aplicada, experimental, exploratória, de abordagem mista (quantitativa e qualitativa).
- **Aplicada:** resolve um problema prático do setor industrial (subjetividade e custo da inspeção manual)
- **Experimental:** manipula variáveis, arquiteturas e hiperparâmetros para observar efeitos nas métricas
- **Exploratória:** há pouca literatura sobre essa abordagem hierárquica específica no domínio de rochas ornamentais
- **Mista:** combina métricas quantitativas (mAP, IoU, FPS) com análise qualitativa das segmentações

---

## Objetivos

### Objetivo Geral
Desenvolver e validar um pipeline hierárquico de IA para automatizar o controle de qualidade de chapas na indústria de rochas ornamentais.

### Objetivos Específicos (rascunho — a refinar)
1. Implementar e integrar o classificador taxonômico (Xception) ao pipeline
2. Calibrar o modelo SAM3 para geração de anotações de anomalias para cada tipo de rocha
3. Treinar 45 modelos YOLO especializados (Student) — um por tipo de rocha — com as anotações geradas pelo SAM (Teacher)
4. Comparar a abordagem hierárquica com um baseline generalista em termos de mAP e IoU

---

## Justificativas

### Por que este problema é relevante?
- Controle de qualidade em rochas ornamentais é feito majoritariamente de forma manual no Brasil
- A inspeção visual humana é subjetiva, lenta e sujeita à fadiga
- O Brasil é um dos maiores exportadores mundiais de rochas ornamentais — qualidade impacta diretamente a competitividade
- Indústria 4.0: automação inteligente de processos de inspeção é tendência global

### Por que a abordagem hierárquica?
- Rochas têm alta variabilidade visual inter-classe — o que é anomalia em uma classe pode ser padrão em outra
- Modelos generalistas monolíticos sofrem com essa variabilidade
- A classificação prévia restringe o domínio visual → reduz ambiguidade → menos falsos positivos
- Permite especialização: cada "especialista" conhece a aparência normal daquele tipo específico

### Por que SAM como Teacher?
- SAM3 produz segmentações de alta qualidade sem anotação manual humana extensiva
- Gera anotações via prompts de linguagem natural (CLIP) — sem necessidade de especialista por imagem
- Reduz drasticamente o custo de criação de dataset rotulado
- As anotações SAM alimentam diretamente o treinamento do YOLO

### Por que YOLO como Student?
- Velocidade de inferência adequada para linha de produção (tempo real)
- Modelo compacto e eficiente (edge deployment possível)
- Treinamento supervisionado com as anotações do Teacher → knowledge distillation implícita

---

## Fundamentação Teórica — Talking Points

### Foundation Models e Zero-Shot
- **Foundation Models:** modelos treinados em larga escala com dados genéricos, capazes de realizar tarefas diversas sem retreinamento específico
- SAM é um Foundation Model: foi treinado com milhões de imagens genéricas e nunca viu rochas ornamentais — ainda assim segmenta anomalias via prompts
- **Zero-shot:** capacidade de executar uma tarefa sem treinamento específico para ela. O SAM segmenta fissuras em rochas apenas porque o operador pede em linguagem natural ("crack"), sem exemplos prévios desse domínio
- **Injeção de conhecimento de domínio:** processo de calibrar os prompts e limiares do SAM por litologia (`rock_prompts.json`), convertendo um modelo genérico em um especialista de rochas ornamentais
- **CLIP como ponte texto→imagem:** o SAM3 usa CLIP (OpenAI) para converter prompts de texto em vetores de embedding num espaço semântico compartilhado com embeddings visuais. O vetor de "crack" fica próximo de regiões visualmente similares a rachaduras — mesmo sem o modelo ter visto rochas ornamentais
- **Prompts contextuais vs. palavras simples:** o CLIP foi treinado em legendas/descrições de imagens, não em palavras isoladas. O paper original identificou que o template `"a photo of a [X]"` supera consistentemente apenas `"X"` em zero-shot. Para rochas, `"crack on a stone surface"` pode ser mais preciso que `"crack"` — desambigua contexto (veias sanguíneas vs. veios minerais, etc.). **Candidato a experimento:** comparar palavras simples vs. frases contextuais via `rock_prompts.json` + `inference.py`; potencial análise de sensibilidade nos resultados

### Deep Learning e Segmentação de Instâncias
- SAM (Segment Anything Model): Foundation Model com prompting por texto via CLIP
- YOLO: historicamente focado em detecção; versões recentes suportam segmentação de polígonos; otimizado para Edge Computing
- Xception: arquitetura depthwise separable convolutions; resultados validados em DeepStoneAI
- Transfer learning: modelos pré-treinados (ImageNet) adaptados ao domínio de rochas
- Teacher-Student: conceito de destilação de conhecimento — modelo pesado (SAM) treina modelo leve (YOLO)

### Controle de Qualidade Industrial com IA
- Contextualizar inspeção visual automatizada (automated visual inspection — AVI)
- Comparar com outras aplicações industriais: defeitos em tecido, solda, vidro, metais
- Métricas-chave: mAP (mean Average Precision), IoU (Intersection over Union)
- Desafio da anotação: subjetividade humana vs. consistência do modelo

### Indústria 4.0
- Digitalização de processos produtivos
- Integração de IA em linhas de produção
- Contexto brasileiro: setor de rochas ornamentais no ES (Vitória/Cachoeiro)

### Sistemas de Informação e Adoção de Tecnologia
**Nota: referencial teórico de apoio — não é capítulo de análise nem objetivo principal do TCC.**
- **TAM (Technology Acceptance Model):** utilidade percebida e facilidade de uso como determinantes de adoção
- **Difusão de Inovações (Rogers):** como a tecnologia de inspeção automatizada se difunde no setor
- **Teoria Sociotécnica:** impacto do sistema nos processos humanos da fábrica — operadores, qualidade, gestão

---

## Métricas e Avaliação

### Quantitativas
- **mAP (mean Average Precision):** métrica padrão para detecção e segmentação
- **IoU (Intersection over Union):** sobreposição entre máscara predita e ground truth
- **Precisão e Recall por classe de anomalia**
- **FPS (quadros por segundo):** valida viabilidade do YOLO para linha de produção em tempo real

### Qualitativas
- **Validação por especialistas:** amostras dos resultados SAM de cada tipo litológico serão avaliadas por especialistas do setor de rochas ornamentais. O objetivo é verificar se as segmentações identificam anomalias reais do ponto de vista industrial — não gerar ground truth pixel a pixel.
- **Ponto importante:** mAP e IoU são sensíveis à qualidade da anotação. Como o ground truth é gerado pelo próprio SAM (sem anotação humana paralela), a comparação quantitativa entre Teacher e Student é válida, mas deve ser contextualizada. A validação qualitativa por especialistas complementa a análise quantitativa.
- A subjetividade das anotações é parte da discussão metodológica — não um problema a esconder.

### Baseline para comparação

Definição do baseline e do experimento central (45 especialistas × 1 generalista) → fonte única em `decisoes.md` (**D3**).

---

## Decisões Metodológicas

As questões metodológicas originalmente em aberto (rotulagem, integração dos estágios, baseline, ground truth, escopo de anomalias, versão do YOLO, nome, identidade ARIA/Hartheus) foram **fechadas** e migradas para a fonte única `decisoes.md`. Novas pendências ficam em `PENDENCIAS.md`.

---

## Delimitações e Limitações (a mencionar no TCC)

- Loop de aprendizado ativo: trabalho futuro
- Dataset desequilibrado: reflexo da realidade industrial, não equalizado artificialmente
- Validação humana das anotações SAM: qualitativa, por amostragem, feita por especialistas do setor — sem anotação humana completa paralela
- Generalização além das 45 classes: não testada
- Integração com sistemas ERP / SCADA da fábrica: fora do escopo
- **Rotulagem multi-classe:** esta versão usa anomalia binária. Classificação por tipo de anomalia (`crack`, `vein`, `Stain`...) é extensão planejada — o `inference.py` já produz os class_ids, falta validação e treinamento YOLO multi-classe.

---

## Estrutura de Capítulos (rascunho)

1. Introdução
   - Contexto industrial (setor de rochas ornamentais no Brasil)
   - Problema: inspeção manual, subjetividade, escala
   - Hipótese e objetivos
   - Estrutura do trabalho

2. Fundamentação Teórica
   - Deep Learning para visão computacional (CNN, segmentação)
   - SAM, YOLO, Xception
   - Teacher-Student / Knowledge Distillation
   - Controle de qualidade automatizado
   - Indústria 4.0
   - TAM, Difusão de Inovações, Teoria Sociotécnica

3. Trabalhos Relacionados
   - Inspeção automatizada em pedras/minerais
   - Aplicações de SAM em domínios industriais
   - Pipelines hierárquicos em visão computacional

4. Metodologia
   - Dataset e sua construção
   - Fase 1: Classificação (Xception)
   - Fase 2: Geração de anotações (SAM Teacher)
   - Fase 3: Treinamento YOLO (Student)
   - Protocolo de avaliação e métricas

5. Resultados e Discussão
   - Resultados do classificador
   - Resultados do segmentador SAM (exemplos qualitativos)
   - Resultados do YOLO treinado
   - Comparação hierárquico vs. generalista
   - Análise qualitativa vs. quantitativa

6. Conclusão
   - Contribuições
   - Limitações
   - Trabalhos Futuros (loop ativo, integração ERP, novas classes)
