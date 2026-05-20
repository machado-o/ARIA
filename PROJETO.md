# Hartheus — Contexto do Projeto

---

## O que é Hartheus

Hartheus é uma plataforma web para análise e controle de qualidade de chapas de rochas ornamentais. O sistema combina gerenciamento de imagens com segmentação semântica assistida por IA, voltado para uso industrial na linha de produção.

A plataforma é composta por quatro serviços:

```
┌──────────────────────────────────────────────────────────────┐
│                      Docker Network                          │
├────────────┬──────────────┬─────────────────┬────────────────┤
│  Frontend  │   Backend    │    Database     │  AI Service    │
│  Port 5173 │   Port 3000  │    Port 5432    │  Port 8000     │
│  React SPA │  NestJS API  │   PostgreSQL    │ Python/PyTorch │
└────────────┴──────────────┴─────────────────┴────────────────┘
```

- **Frontend** — interface de anotação assistida por IA: canvas com polígonos, zoom/pan, revisão e correção de predições do modelo
- **Backend** — API NestJS com autenticação JWT e gerenciamento de usuários
- **AI Service** — serviço Python que expõe `POST /segment` na porta 8000; o frontend chama este endpoint para obter segmentações
- **Database** — PostgreSQL com schema `hartheus`

O código da plataforma vive principalmente nas branches `main` e `dev/hartheus`.

---

## IA no Hartheus — Abordagens em desenvolvimento

O módulo de IA é o componente mais experimental do projeto. Múltiplas abordagens estão sendo pesquisadas em paralelo — cada uma em sua própria branch — antes de uma decisão sobre qual implementar na plataforma.

### Branch `ARIA` — pipeline hierárquico (Henrique — TCC)

Esta branch. Proposta e desenvolvida por Henrique como TCC de Bacharelado em Sistemas de Informação no IFES Cachoeiro de Itapemirim.

**O que é ARIA:** pipeline hierárquico de IA (Análise e Reconhecimento Inteligente de Anomalias) para controle de qualidade em rochas ornamentais. Arquitetura Teacher-Student:

```
Xception (classificador)
      ↓ identifica o tipo litológico
SAM3 (Teacher)
      ↓ gera anotações de polígonos calibradas por tipo de rocha
YOLO11-seg (Student) × 45
      ↓ 45 modelos especialistas, um por tipo — inferência rápida em produção
```

**Hipótese central:** modelos especialistas hierárquicos — onde a classificação prévia restringe o domínio visual do segmentador — reduzem falsos positivos e superam modelos generalistas monolíticos, dada a alta variabilidade visual das rochas ornamentais.

**Estado atual:** fase de calibração SAM — ajuste de prompts e limiares de confiança por tipo de rocha em `rock_prompts.json`. Pipeline roda como script batch (sem HTTP API). A integração como serviço HTTP (para plugar no frontend Hartheus via `POST /segment`) é trabalho futuro.

**Relevância para o Hartheus:** se os resultados confirmarem a hipótese, o pipeline ARIA pode substituir ou complementar o AI Service atual da plataforma. Não há garantia — o TCC é desenvolvido de forma independente, com potencial de aplicação.

---

### Branch `feat/matheus` — active-learning pipeline (Matheus)

Abordagem alternativa: loop de auto-melhoria onde o SAM3 gera anotações iniciais que treinam o YOLO, que então itera.

- Expõe `POST /pipeline/run` e `GET /pipeline/stream` via FastAPI — mais alinhado com a arquitetura atual do Hartheus
- Código em `ai/api.py` (note: esta branch renomeou `AI/` → `ai/`)

---

## Diferenças técnicas entre as branches de IA

| Aspecto | `ARIA` | `feat/matheus` |
|---|---|---|
| Diretório IA | `AI/` | `ai/` |
| Entry point | `inference.py` (batch script) | `api.py` (FastAPI) |
| Trigger | Docker CMD | `POST /pipeline/run` |
| Config | `SAM/rock_prompts.json` | `ai/config.py` |
| Abordagem | Prompts calibrados por litologia + Teacher-Student hierárquico | SAM3 → YOLO active-learning loop |
| HTTP API | Nenhuma (batch) | FastAPI + SSE |
| `POST /segment` (frontend) | Não implementado | Não implementado (endpoints diferentes) |

**Atenção:** os fluxos de inferência são fundamentalmente diferentes — não misturar código entre branches.

---

## Integração futura (trabalho futuro)

Quando o pipeline ARIA estiver completo e validado, a integração com o Hartheus exigiria expor a inferência como serviço HTTP compatível com o frontend:

```
rock_prompts.json (calibrados por tipo)
        ↓
Xception identifica tipo → seleciona prompts calibrados
        ↓
SAM3 segmenta com conhecimento de domínio
        ↓
Labels YOLO (.txt) → 45 modelos especialistas treinados
        ↓
YOLO especialista: inferência rápida → POST /segment → frontend Hartheus
```

O loop de aprendizado ativo (SAM refinando predições de baixa confiança do YOLO em produção) é trabalho futuro além do escopo do TCC.

---

## Branches do repositório

| Branch | Responsável | Propósito |
|---|---|---|
| `main` | — | Plataforma Hartheus estável |
| `dev/hartheus` | — | Integração antes de mergear na main |
| `ARIA` | Henrique | TCC — pipeline hierárquico (este repo) |
| `feat/matheus` | Matheus | Active-learning pipeline |
| `feat/henrique` | Henrique | Integração pessoal (dev/hartheus + outras) |
| `feat/arthur` | Arthur | CI/infra only |
