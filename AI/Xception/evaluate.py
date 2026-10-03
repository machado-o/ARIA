"""evaluate — mede o classificador de litologia num split (docs/decisoes.md D19).

Produz runs/<nome>/metricas_<split>.json com:
    acurácia · acurácia balanceada (média dos recalls) · F1 macro
    precisão / recall / F1 / suporte por classe
    matriz de confusão (linha = classe real, coluna = prevista)
    lista de erros (arquivo, real, previsto, confiança)

O F1 macro e a acurácia balanceada pesam igual as 45 classes — a acurácia simples é
dominada pela faixa A e esconde as litologias raras, que são justamente onde o DeepStoneAI
errava.

**O test/ se avalia UMA vez.** Avaliar no teste, ajustar e avaliar de novo transforma o teste
em validação, e o número deixa de valer. Por isso o script recusa sobrescrever
metricas_test.json; `--forcar` existe só para quando a primeira tentativa falhou por motivo
técnico — e isso deve ser registrado.

Uso (de AI/Xception/):
    python evaluate.py --split val         # à vontade, durante o desenvolvimento
    python evaluate.py                     # test/, uma vez, ao final
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from common import (DATASET_DIR, MODELS_DIR, RUNS_DIR, SEED, TAMANHO, Rochas,
                    carregar_checkpoint, dispositivo_padrao, listar_amostras)


def argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--nome", default=f"xception_{TAMANHO}")
    p.add_argument("--split", choices=("val", "test"), default="test")
    p.add_argument("--lote", type=int, default=32)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--limite", type=int, default=0, help="só N imagens (teste de fumaça)")
    p.add_argument("--forcar", action="store_true",
                   help="sobrescreve metricas_test.json (só por falha técnica — registrar)")
    p.add_argument("--dir-runs", type=Path, default=RUNS_DIR)
    p.add_argument("--dir-modelos", type=Path, default=MODELS_DIR)
    return p.parse_args()


def metricas(reais: np.ndarray, previstos: np.ndarray, classes: list[str]) -> dict:
    n = len(classes)
    confusao = np.zeros((n, n), dtype=np.int64)
    np.add.at(confusao, (reais, previstos), 1)

    acertos = np.diag(confusao).astype(float)
    suporte = confusao.sum(1).astype(float)            # quantas imagens de cada classe
    previstas = confusao.sum(0).astype(float)          # quantas vezes cada classe foi prevista
    with np.errstate(divide="ignore", invalid="ignore"):
        recall = np.where(suporte > 0, acertos / suporte, np.nan)
        precisao = np.where(previstas > 0, acertos / previstas, 0.0)
        f1 = np.where(precisao + recall > 0, 2 * precisao * recall / (precisao + recall), 0.0)

    presentes = suporte > 0                            # com --limite, alguma classe pode faltar
    por_classe = {
        c: {"precisao": float(precisao[i]), "recall": float(recall[i]),
            "f1": float(f1[i]), "suporte": int(suporte[i])}
        for i, c in enumerate(classes) if presentes[i]
    }
    return {
        "n": int(len(reais)),
        "acuracia": float(acertos.sum() / len(reais)),
        "acuracia_balanceada": float(np.nanmean(recall[presentes])),
        "f1_macro": float(f1[presentes].mean()),
        "classes_com_erro": int((recall[presentes] < 1.0).sum()),
        "por_classe": por_classe,
        "matriz_confusao": confusao.tolist(),
    }


def main() -> None:
    args = argumentos()
    dir_run = args.dir_runs / args.nome
    saida = dir_run / f"metricas_{args.split}.json"
    if args.split == "test" and saida.exists() and not args.forcar:
        raise SystemExit(
            f"{saida} já existe: o test/ se avalia uma vez só (ver docstring). "
            f"Use --split val para iterar, ou --forcar se a avaliação anterior falhou.")

    dispositivo = dispositivo_padrao()
    modelo, ck = carregar_checkpoint(args.dir_modelos / f"{args.nome}.pt", dispositivo)
    classes = ck["classes"]
    amostras = listar_amostras(args.split, classes)
    if args.limite:
        amostras = random.Random(SEED).sample(amostras, min(args.limite, len(amostras)))
    print(f"── {args.nome} · {args.split}/ · {len(amostras)} imagens · checkpoint da fase "
          f"{ck['fase']} época {ck['epoca']} (val_loss {ck['val_loss']:.4f}) ──")

    dados = DataLoader(Rochas(amostras, aumentar=False), batch_size=args.lote,
                       shuffle=False, num_workers=args.workers, pin_memory=True)
    probs = []
    amp = dispositivo.type == "cuda"
    with torch.inference_mode():
        for x, _ in dados:
            x = x.to(dispositivo, non_blocking=True)
            with torch.autocast(device_type=dispositivo.type, dtype=torch.bfloat16, enabled=amp):
                logits = modelo(x)
            probs.append(logits.float().softmax(1).cpu())
    probs = torch.cat(probs).numpy()
    reais = np.array([r for _, r in amostras])
    previstos = probs.argmax(1)

    resultado = metricas(reais, previstos, classes)
    resultado["erros"] = [
        {"arquivo": caminho.relative_to(DATASET_DIR).as_posix(),
         "real": classes[r], "previsto": classes[p], "confianca": float(probs[i, p])}
        for i, ((caminho, r), p) in enumerate(zip(amostras, previstos)) if r != p
    ]
    resultado["checkpoint"] = {k: ck[k] for k in ("fase", "epoca", "val_loss", "val_acc",
                                                  "salvo_em")}
    resultado["split"] = args.split
    resultado["limite"] = args.limite
    resultado["avaliado_em"] = datetime.now().isoformat(timespec="seconds")

    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"  acurácia            {resultado['acuracia']:.4f}")
    print(f"  acurácia balanceada {resultado['acuracia_balanceada']:.4f}")
    print(f"  F1 macro            {resultado['f1_macro']:.4f}")
    print(f"  classes com erro    {resultado['classes_com_erro']} de "
          f"{len(resultado['por_classe'])}")
    piores = sorted(resultado["por_classe"].items(), key=lambda kv: kv[1]["recall"])[:5]
    print("  piores recalls:     " + " · ".join(f"{c} {m['recall']:.3f}" for c, m in piores))
    print(f"✔ {saida}")


if __name__ == "__main__":
    main()
