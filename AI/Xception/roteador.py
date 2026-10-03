"""roteador — Estágio 1 do ARIA: recebe uma chapa e diz qual é a litologia (D19).

É a peça que, na Fase 4, escolhe a configuração de sondas (rock_prompts.json) e o Aluno
especialista. Por ora só classifica — a ligação com os estágios 2 e 3 vem quando eles
existirem como código de produção.

Devolve a confiança junto com a classe, e o top-3: a litologia errada leva às sondas e ao
Aluno errados, então quem chama precisa poder recusar uma classificação incerta.

Uso como módulo:
    from roteador import Roteador
    r = Roteador()                        # models/xception_480.pt
    r.classificar("chapa.jpg")            # Classificacao(litologia=..., confianca=..., top=[...])

Uso na linha de comando (de AI/Xception/):
    python roteador.py chapa1.jpg chapa2.jpg
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import torch

from common import (MODELS_DIR, TAMANHO, abrir_imagem, carregar_checkpoint,
                    dispositivo_padrao, normalizar)


@dataclass(frozen=True)
class Classificacao:
    litologia: str
    confianca: float
    top: list[tuple[str, float]]


class Roteador:
    def __init__(self, checkpoint: Path = MODELS_DIR / f"xception_{TAMANHO}.pt",
                 dispositivo: str | torch.device | None = None):
        self.dispositivo = torch.device(dispositivo) if dispositivo else dispositivo_padrao()
        self.modelo, meta = carregar_checkpoint(Path(checkpoint), self.dispositivo)
        self.classes: list[str] = meta["classes"]

    @torch.inference_mode()
    def classificar(self, caminho: str | Path, k: int = 3) -> Classificacao:
        x = normalizar(abrir_imagem(Path(caminho))).unsqueeze(0).to(self.dispositivo)
        probs = self.modelo(x).float().softmax(1)[0]
        valores, indices = probs.topk(min(k, len(self.classes)))
        top = [(self.classes[i], float(v)) for v, i in zip(valores.tolist(), indices.tolist())]
        return Classificacao(litologia=top[0][0], confianca=top[0][1], top=top)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("imagens", nargs="+", type=Path)
    p.add_argument("--checkpoint", type=Path, default=MODELS_DIR / f"xception_{TAMANHO}.pt")
    args = p.parse_args()

    roteador = Roteador(args.checkpoint)
    for img in args.imagens:
        c = roteador.classificar(img)
        alternativas = " · ".join(f"{nome} {conf:.3f}" for nome, conf in c.top[1:])
        print(f"{img.name}: {c.litologia} ({c.confianca:.3f})   [{alternativas}]")


if __name__ == "__main__":
    main()
