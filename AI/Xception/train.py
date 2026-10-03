"""train — treina o classificador de litologia (docs/decisoes.md D19).

Duas fases, como no notebook do DeepStoneAI:

    1. base congelada, só a cabeça treina ........ Adam lr 1e-4, até 15 épocas
    2. fine-tuning das 50 últimas camadas ........ Adam lr 1e-5, até 10 épocas

Os "callbacks" do Keras estão reimplementados com a MESMA semântica (o
ReduceLROnPlateau do PyTorch conta paciência com um a mais e usa limiar relativo):

    ReduceLROnPlateau(val_loss, factor=0.5, patience=3, min_delta=1e-4 absoluto)
    EarlyStopping(val_loss, patience=5, restore_best_weights=True)
    ModelCheckpoint(val_loss, save_best_only=True)

Ambos zeram a contagem no início de cada fase, como no Keras, e a fase 2 começa dos melhores
pesos da fase 1. O checkpoint salvo é o de MENOR val_loss entre as duas fases — é ele que o
evaluate.py e o roteador usam.

Só lê train/ e val/. O test/ é do evaluate.py, uma vez, no final.

Uso (de AI/Xception/):
    python train.py                     # treino completo → models/xception_480.pt
    python train.py --limite 64 --fase1-epocas 1 --fase2-epocas 1 --nome smoke ...
"""

from __future__ import annotations

import argparse
import json
import random
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import timm
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from common import (DESVIO, MEDIA, MODELO_TIMM, MODELS_DIR, RUNS_DIR, SEED, TAMANHO,
                    Rochas, contar_treinaveis, criar_modelo, definir_fase,
                    dispositivo_padrao, duracao_para_texto, listar_amostras, listar_classes,
                    modo_treino, semear_worker)

FASES = (
    # nome,        lr,    épocas (padrão)
    ("congelada", 1e-4, 15),
    ("finetune",  1e-5, 10),
)
PACIENCIA_LR = 3
FATOR_LR = 0.5
DELTA_LR = 1e-4
PACIENCIA_PARADA = 5
ADAM_EPS = 1e-7          # epsilon padrão do Adam no Keras (o do PyTorch é 1e-8)


def argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--nome", default=f"xception_{TAMANHO}",
                   help="nome do run: runs/<nome>/ e models/<nome>.pt")
    p.add_argument("--fase1-epocas", type=int, default=FASES[0][2])
    p.add_argument("--fase2-epocas", type=int, default=FASES[1][2])
    p.add_argument("--lote", type=int, default=32)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--limite", type=int, default=0,
                   help="usa só N imagens por split (teste de fumaça). 0 = tudo")
    p.add_argument("--sem-amp", action="store_true",
                   help="desliga a precisão mista bf16 (mais lento, fp32 puro)")
    p.add_argument("--dir-runs", type=Path, default=RUNS_DIR)
    p.add_argument("--dir-modelos", type=Path, default=MODELS_DIR)
    return p.parse_args()


def semear(semente: int) -> None:
    random.seed(semente)
    np.random.seed(semente)
    torch.manual_seed(semente)


def carregador(amostras, aumentar: bool, args, embaralhar: bool) -> DataLoader:
    gerador = torch.Generator().manual_seed(SEED)
    return DataLoader(Rochas(amostras, aumentar), batch_size=args.lote, shuffle=embaralhar,
                      num_workers=args.workers, pin_memory=True,
                      persistent_workers=args.workers > 0, worker_init_fn=semear_worker,
                      generator=gerador)


def rodar_epoca(modelo, dados, dispositivo, amp: bool, otimizador=None) -> tuple[float, float]:
    """Uma passada. Com otimizador = treino; sem = validação. Devolve (loss, acurácia)."""
    treinando = otimizador is not None
    if treinando:
        modo_treino(modelo)
    else:
        modelo.eval()
    criterio = nn.CrossEntropyLoss(reduction="sum")
    soma_loss, acertos, total = 0.0, 0, 0
    with torch.set_grad_enabled(treinando):
        for x, y in dados:
            x = x.to(dispositivo, non_blocking=True).contiguous(memory_format=torch.channels_last)
            y = y.to(dispositivo, non_blocking=True)
            with torch.autocast(device_type=dispositivo.type, dtype=torch.bfloat16, enabled=amp):
                logits = modelo(x)
            loss = criterio(logits.float(), y)
            if treinando:
                otimizador.zero_grad(set_to_none=True)
                (loss / len(y)).backward()
                otimizador.step()
            soma_loss += loss.item()
            acertos += (logits.argmax(1) == y).sum().item()
            total += len(y)
    return soma_loss / total, acertos / total


def salvar_checkpoint(caminho: Path, modelo, classes, meta: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "state_dict": modelo.state_dict(),
        "classes": classes,
        "modelo_timm": MODELO_TIMM,
        "tamanho": TAMANHO,
        "media": MEDIA,
        "desvio": DESVIO,
        **meta,
    }, caminho)


def escrever_json(caminho: Path, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    args = argumentos()
    semear(SEED)
    dispositivo = dispositivo_padrao()
    amp = dispositivo.type == "cuda" and not args.sem_amp
    torch.backends.cudnn.benchmark = True

    classes = listar_classes()
    treino = listar_amostras("train", classes)
    valid = listar_amostras("val", classes)
    if args.limite:
        rng = random.Random(SEED)
        treino = rng.sample(treino, min(args.limite, len(treino)))
        valid = rng.sample(valid, min(args.limite, len(valid)))

    dir_run = args.dir_runs / args.nome
    caminho_modelo = args.dir_modelos / f"{args.nome}.pt"
    print(f"── {args.nome} · {len(classes)} classes · treino {len(treino)} · val {len(valid)}"
          f" · {TAMANHO}×{TAMANHO} · lote {args.lote} · {dispositivo}"
          f"{' · bf16' if amp else ''} ──")

    config = {
        "decisao": "D19",
        "modelo_timm": MODELO_TIMM, "tamanho": TAMANHO, "media": MEDIA, "desvio": DESVIO,
        "lote": args.lote, "seed": SEED, "amp_bf16": amp, "limite": args.limite,
        "fases": [{"nome": n, "lr": lr, "epocas": e} for (n, lr, _), e in
                  zip(FASES, (args.fase1_epocas, args.fase2_epocas))],
        "reduce_lr": {"fator": FATOR_LR, "paciencia": PACIENCIA_LR, "min_delta": DELTA_LR},
        "early_stopping": {"paciencia": PACIENCIA_PARADA, "restaura_melhor": True},
        "adam_eps": ADAM_EPS,
        "n_treino": len(treino), "n_val": len(valid), "classes": classes,
        "versoes": {"torch": torch.__version__, "timm": timm.__version__},
        "gpu": torch.cuda.get_device_name(0) if dispositivo.type == "cuda" else None,
        "inicio": datetime.now().isoformat(timespec="seconds"),
        "checkpoint": str(caminho_modelo),
    }
    escrever_json(dir_run / "config.json", config)

    dados_treino = carregador(treino, aumentar=True, args=args, embaralhar=True)
    dados_val = carregador(valid, aumentar=False, args=args, embaralhar=False)

    modelo = criar_modelo(len(classes)).to(dispositivo).to(memory_format=torch.channels_last)

    historico, melhor_global = [], float("inf")
    for (fase, lr, _), n_epocas in zip(FASES, (args.fase1_epocas, args.fase2_epocas)):
        definir_fase(modelo, fase)
        base, topo = contar_treinaveis(modelo)
        print(f"\n▶ fase {fase}: lr {lr:g} · até {n_epocas} épocas · "
              f"treináveis base {base:,} + cabeça {topo:,}")
        otimizador = torch.optim.Adam([p for p in modelo.parameters() if p.requires_grad],
                                      lr=lr, eps=ADAM_EPS)

        melhor_fase, melhores_pesos = float("inf"), None
        melhor_lr = float("inf")
        espera_lr = espera_parada = 0
        for epoca in range(1, n_epocas + 1):
            t0 = time.perf_counter()
            loss_tr, acc_tr = rodar_epoca(modelo, dados_treino, dispositivo, amp, otimizador)
            loss_va, acc_va = rodar_epoca(modelo, dados_val, dispositivo, amp)
            dt = time.perf_counter() - t0
            lr_atual = otimizador.param_groups[0]["lr"]

            # ModelCheckpoint(save_best_only) — vale entre as duas fases
            salvou = loss_va < melhor_global
            if salvou:
                melhor_global = loss_va
                salvar_checkpoint(caminho_modelo, modelo, classes, {
                    "fase": fase, "epoca": epoca, "val_loss": loss_va, "val_acc": acc_va,
                    "salvo_em": datetime.now().isoformat(timespec="seconds")})

            # EarlyStopping(restore_best_weights) — por fase
            if loss_va < melhor_fase:
                melhor_fase, espera_parada = loss_va, 0
                melhores_pesos = {k: v.detach().clone() for k, v in modelo.state_dict().items()}
            else:
                espera_parada += 1

            # ReduceLROnPlateau — por fase, delta absoluto, reduz ao atingir a paciência
            if loss_va < melhor_lr - DELTA_LR:
                melhor_lr, espera_lr = loss_va, 0
            else:
                espera_lr += 1
                if espera_lr >= PACIENCIA_LR:
                    for g in otimizador.param_groups:
                        g["lr"] *= FATOR_LR
                    espera_lr = 0

            historico.append({"fase": fase, "epoca": epoca, "lr": lr_atual,
                              "loss": loss_tr, "acc": acc_tr,
                              "val_loss": loss_va, "val_acc": acc_va,
                              "segundos": round(dt, 1), "checkpoint": salvou})
            escrever_json(dir_run / "historico.json", historico)
            print(f"  {fase} {epoca:2d}/{n_epocas} · loss {loss_tr:.4f} acc {acc_tr:.4f} · "
                  f"val_loss {loss_va:.4f} val_acc {acc_va:.4f} · lr {lr_atual:.1e} · "
                  f"{duracao_para_texto(dt)}{'  ✓ checkpoint' if salvou else ''}")

            if espera_parada >= PACIENCIA_PARADA:
                print(f"  parada antecipada: {PACIENCIA_PARADA} épocas sem melhorar val_loss")
                break

        if melhores_pesos is not None:
            modelo.load_state_dict(melhores_pesos)       # restore_best_weights

    config["fim"] = datetime.now().isoformat(timespec="seconds")
    config["melhor_val_loss"] = melhor_global
    escrever_json(dir_run / "config.json", config)
    print(f"\n✔ melhor val_loss {melhor_global:.4f} → {caminho_modelo}")
    print(f"  próximo passo: python evaluate.py --nome {args.nome}")


if __name__ == "__main__":
    main()
