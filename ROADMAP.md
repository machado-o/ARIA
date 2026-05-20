# Roadmap — ARIA Pipeline

Próximos passos do desenvolvimento, em ordem cronológica de execução.

---

## 1. Reconstruir `calibrator.py`

UI interativa de calibração de prompts. Pré-requisito prático para completar as 42 rochas pendentes com eficiência — sem ela o ciclo é editar JSON à mão → rodar `inference.py` → abrir `results/` manualmente.

---

## 2. Completar seleção de imagens representativas (42 rochas)

Selecionar uma imagem representativa por rocha via `rock_viewer.py` para as 42 rochas ainda sem seleção em `selectRocks/`.

Estado atual:
- `ice_leke` — calibrado e validado
- `giallo_fiorito`, `giallo_maracana` — imagem selecionada, calibração pendente
- 42 rochas — sem imagem selecionada

---

## 3. Completar calibração de prompts (45 rochas)

Calibrar prompts e limiares de confiança em `rock_prompts.json` para cada tipo de rocha. Rodar `inference.py` e validar os resultados em `results/` até o resultado ser satisfatório.

---

## 4. Rodar inferência SAM em batch (45 rochas)

Com todos os prompts calibrados, rodar `inference.py` uma vez para gerar as anotações finais de todas as 45 rochas. Os `.txt` gerados em `results/` (formato YOLO segmentation) são o input direto do treinamento YOLO — sem conversão de formato.

---

## 5. Validação qualitativa por especialistas

Coletar amostras dos resultados SAM de cada tipo litológico e submetê-las à avaliação de especialistas do setor de rochas ornamentais. O objetivo é confirmar que as segmentações identificam anomalias reais do ponto de vista industrial, complementando as métricas quantitativas.

---

## 6. Implementar YOLO — treinamento

Implementar `YOLO/train.py` consumindo os `.txt` de `results/` como dataset de treinamento.

Treinar dois pipelines em paralelo para o experimento central do TCC:
- **45 modelos especialistas** — um por tipo de rocha, cada um treinando exclusivamente nas anotações SAM do seu litótipo
- **1 modelo generalista** (baseline) — treinando em anotações de todas as rochas com config genérica de prompts (`default`)

---

## 7. Avaliar e comparar pipelines

Avaliar os dois pipelines (especialista × generalista) com as métricas do TCC:
- mAP e IoU nos conjuntos de validação e teste
- FPS (viabilidade para linha de produção em tempo real)
- Análise qualitativa comparada com a validação dos especialistas

---

## 8. Integrar Xception ao pipeline

O classificador Xception (DeepStoneAI) já foi treinado e validado em projeto anterior nas 45 classes. Integrar como primeiro estágio do pipeline ARIA: recebe a imagem → identifica o tipo litológico → seleciona os prompts calibrados correspondentes em `rock_prompts.json` → roteia para o modelo YOLO especialista.

---

## 9. Testar pipeline end-to-end

Validar o pipeline completo: Xception → SAM (prompts calibrados por tipo) → YOLO especialista → saída de polígonos. Primeiro teste integrado dos três estágios.

---

## Fora do escopo desta versão

- **API FastAPI** — expor o pipeline como serviço `POST /segment` para integração com o frontend Hartheus. Trabalho futuro pós-TCC.
- **Loop de aprendizado ativo** — SAM refinando predições de baixa confiança do YOLO em produção. Trabalho futuro.
- **Rotulagem multi-classe** — treinar YOLO com class_ids distintos por tipo de anomalia. Extensão planejada se houver tempo; requer validação humana das anotações SAM.
