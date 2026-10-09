"""common — peças compartilhadas do classificador de litologia (docs/decisoes.md D19).

Reprodução, em PyTorch + timm, do Xception do DeepStoneAI (SBAI 2025), cuja receita está
num notebook Keras sem pesos salvos. Este módulo concentra tudo o que treino, avaliação e
roteador precisam enxergar igual: caminhos, classes, modelo, congelamento e transformações.

Equivalências com o Keras que NÃO são óbvias — e por que estão como estão:

1. **"Últimas 50 camadas" do Keras → módulos do timm.** O Keras conta camada por camada
   (ativação, BN e `add` contam; SeparableConv2D é uma camada só). Contando de trás para
   frente no `keras.applications.Xception(include_top=False)`:
       block14 (6) + block13 com o resíduo 1×1 (10) + blocks 12, 11, 10 (3 × 10)
       + os 4 últimos do block9 (sepconv3_act, sepconv3, sepconv3_bn, add)      = 50
   No timm o bloco N do Keras é o `blockN-1` (o block1 do Keras é o tronco conv1/conv2).
   Então: conv3/bn3/conv4/bn4, block12, block11, block10, block9 e o final de block8.
   `definir_fase()` confere isso contra a conta feita à mão (12.168.304 parâmetros)
   e aborta se o mapeamento divergir.

2. **BatchNorm sempre em modo de inferência.** O notebook chama `base_model(x,
   training=False)`; no Keras isso mantém o BN usando as médias do ImageNet mesmo quando a
   camada está destravada no fine-tuning — gamma/beta treinam, as médias móveis não mudam.
   `modo_treino()` reproduz isso: o modelo entra em train() (para o Dropout da cabeça), mas
   todo BN volta para eval().

3. **Normalização: [-1, 1], e não [0, 1].** Os pesos do Xception (porte dos pesos do Keras)
   esperam `preprocess_input` do Xception, que leva a imagem para [-1, 1]. O notebook
   original só dividia por 255 — entrada fora da escala que os pesos conhecem. Corrigido e
   declarado na D19.

4. **Augmentation do Keras 3, em semântica.** RandomRotation(0.2) é fração de 2π (±72°);
   RandomZoom(0.2) amostra z em [-0,2; 0,2] e a imagem aparece escalada por 1/(1+z); os dois
   preenchem a borda por REFLEXÃO, e não com preto. RandomContrast(0.2) usa a média de cada
   canal da própria imagem.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import numpy as np
import timm
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import Dataset
from torchvision.transforms.v2 import functional as TF

# ─────────────────────────────────────────────────────────────────────────────
# Caminhos e constantes
# ─────────────────────────────────────────────────────────────────────────────

AQUI = Path(__file__).resolve().parent
DATASET_DIR = AQUI.parent / "dataset"          # AI/dataset — SOMENTE LEITURA
MODELS_DIR = AQUI.parent / "models"            # pesos (fora do git: *.pt)
RUNS_DIR = AQUI / "runs"                        # config, histórico e métricas (no git)

SPLITS = ("train", "val", "test")

MODELO_TIMM = "legacy_xception.tf_in1k"         # o mesmo Xception do Keras, pesos ImageNet
TAMANHO = 480                                   # D19: 480 × 480, sem ampliar para 1080
MEDIA = (0.5, 0.5, 0.5)                         # (x - 0,5) / 0,5  →  [-1, 1]
DESVIO = (0.5, 0.5, 0.5)
SEED = 123                                      # a mesma do notebook original

# Augmentation (Keras: RandomRotation(0.2), RandomZoom(0.2), RandomContrast(0.2))
ROTACAO_MAX_GRAUS = 0.2 * 360.0
ZOOM_FATOR = 0.2
CONTRASTE_FATOR = 0.2

# Conta feita à mão sobre o Keras (ver docstring, item 1): parâmetros da base que ficam
# treináveis no fine-tuning. Serve de prova de que o mapeamento de camadas está certo.
TREINAVEIS_BASE_FINETUNE = 12_168_304


# ─────────────────────────────────────────────────────────────────────────────
# Classes e dataset
# ─────────────────────────────────────────────────────────────────────────────

def listar_classes(dataset_dir: Path = DATASET_DIR) -> list[str]:
    """As 45 litologias, em ordem alfabética — a mesma ordem que o Keras usava.

    Aborta se os três splits não tiverem exatamente as mesmas classes: um índice de classe
    trocado entre treino e teste não dá erro nenhum, só resultado errado.
    """
    por_split = {}
    for split in SPLITS:
        pasta = dataset_dir / split
        if not pasta.is_dir():
            raise FileNotFoundError(f"split não encontrado: {pasta}")
        por_split[split] = sorted(p.name for p in pasta.iterdir() if p.is_dir())
    referencia = por_split["train"]
    for split, classes in por_split.items():
        if classes != referencia:
            faltam = set(referencia) ^ set(classes)
            raise ValueError(f"classes de {split}/ divergem de train/: {sorted(faltam)}")
    return referencia


def listar_amostras(split: str, classes: list[str],
                    dataset_dir: Path = DATASET_DIR) -> list[tuple[Path, int]]:
    """(caminho, índice da classe) de todas as imagens de um split, em ordem estável."""
    amostras = []
    for idx, classe in enumerate(classes):
        for arq in sorted((dataset_dir / split / classe).iterdir()):
            if arq.is_file() and arq.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp"):
                amostras.append((arq, idx))
    return amostras


PROTOCOLOS = ("original", "aleatorio")
FRACAO_TREINO_ALEATORIO = 0.7                   # notebook: validation_split=0.3


def amostras_por_protocolo(protocolo: str, classes: list[str],
                           dataset_dir: Path = DATASET_DIR
                           ) -> dict[str, list[tuple[Path, int]]]:
    """As amostras de train/val/test segundo o protocolo de divisão.

    'original': os splits do jeito que vêm em AI/dataset/.

    'aleatorio': o protocolo do DeepStoneAI, reproduzido para MEDIR o vazamento entre chapas
    vizinhas (pendências, 04/10/2026). O organize2.ipynb junta train/valid/test numa pasta por
    rocha, e o Xception.ipynb sorteia por imagem: 70% treino, e o resto cortado ao meio em val
    e test. Sem estratificar, como o Keras. Aqui o sorteio é feito uma vez só, com a seed fixa,
    sem o reembaralhamento que no notebook misturava val e test a cada passada. O dataset em
    disco não é tocado.
    """
    if protocolo == "original":
        return {s: listar_amostras(s, classes, dataset_dir) for s in SPLITS}
    if protocolo != "aleatorio":
        raise ValueError(f"protocolo desconhecido: {protocolo}")
    todas = [a for s in SPLITS for a in listar_amostras(s, classes, dataset_dir)]
    random.Random(SEED).shuffle(todas)
    n_treino = round(len(todas) * FRACAO_TREINO_ALEATORIO)
    n_val = (len(todas) - n_treino) // 2
    return {"train": todas[:n_treino],
            "val": todas[n_treino:n_treino + n_val],
            "test": todas[n_treino + n_val:]}


def abrir_imagem(caminho: Path, tamanho: int = TAMANHO) -> torch.Tensor:
    """Abre e redimensiona para tamanho × tamanho, sem preservar proporção.

    Sem preservar proporção é de propósito: é o que o `image_dataset_from_directory` do
    Keras fazia (crop_to_aspect_ratio=False). PIL abre caminho com acento no Windows — não
    usar cv2.imread aqui (ver CLAUDE.md).

    `draft` deixa o decodificador JPEG reduzir por DCT direto para algo ≥ tamanho (as
    chapas têm ~1300 × 820), o que corta o custo de decodificação sem tocar no resultado
    final: o redimensionamento para 480 acontece depois, com antialias.
    """
    with Image.open(caminho) as img:
        img.draft("RGB", (tamanho, tamanho))
        img = img.convert("RGB")
        t = TF.pil_to_tensor(img)                                   # uint8, C×H×W
    t = TF.resize(t, [tamanho, tamanho], antialias=True)
    return t.float().div_(255.0)                                    # [0, 1]


def normalizar(x: torch.Tensor) -> torch.Tensor:
    return TF.normalize(x, MEDIA, DESVIO)


class Augmentation:
    """Flip horizontal → rotação + zoom com borda refletida → contraste. Em [0, 1]."""

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() < 0.5:
            x = TF.horizontal_flip(x)

        angulo = random.uniform(-ROTACAO_MAX_GRAUS, ROTACAO_MAX_GRAUS)
        escala = 1.0 / (1.0 + random.uniform(-ZOOM_FATOR, ZOOM_FATOR))
        x = _afim_com_reflexao(x, angulo, escala)

        fator = random.uniform(1.0 - CONTRASTE_FATOR, 1.0 + CONTRASTE_FATOR)
        media = x.mean(dim=(1, 2), keepdim=True)                    # por canal
        return ((x - media) * fator + media).clamp_(0.0, 1.0)


def _afim_com_reflexao(x: torch.Tensor, angulo: float, escala: float) -> torch.Tensor:
    """Rotação + escala com borda refletida (fill_mode='reflect' do Keras).

    O torchvision só preenche com cor sólida. Truque: espelhar a imagem para fora antes,
    aplicar a transformação e recortar o centro. Pior caso (±72°, escala 1/1,2): o canto da
    saída lê a ~0,85 lado do centro, e a margem de meio lado (0,5 + 0,5 = 1,0) cobre com
    folga.
    """
    _, h, w = x.shape
    ph, pw = h // 2, w // 2
    grande = F.pad(x.unsqueeze(0), (pw, pw, ph, ph), mode="reflect").squeeze(0)
    grande = TF.affine(grande, angle=angulo, translate=[0, 0], scale=escala, shear=[0.0, 0.0],
                       interpolation=TF.InterpolationMode.BILINEAR)
    return grande[:, ph:ph + h, pw:pw + w]


class Rochas(Dataset):
    """Um split do dataset. `aumentar=True` só no treino."""

    def __init__(self, amostras: list[tuple[Path, int]], aumentar: bool):
        self.amostras = amostras
        self.aug = Augmentation() if aumentar else None

    def __len__(self) -> int:
        return len(self.amostras)

    def __getitem__(self, i: int) -> tuple[torch.Tensor, int]:
        caminho, rotulo = self.amostras[i]
        x = abrir_imagem(caminho)
        if self.aug is not None:
            x = self.aug(x)
        return normalizar(x), rotulo


def semear_worker(worker_id: int) -> None:
    """Cada worker do DataLoader com semente própria e reprodutível para `random`/numpy."""
    semente = torch.initial_seed() % 2**32
    random.seed(semente)
    np.random.seed(semente)


# ─────────────────────────────────────────────────────────────────────────────
# Modelo e congelamento
# ─────────────────────────────────────────────────────────────────────────────

class ClassificadorXception(nn.Module):
    """Xception + GlobalAveragePooling + Dropout(0,5) + Dense — a cabeça do notebook.

    A cabeça é montada aqui, e não com o `drop_rate` do timm, porque o `legacy_xception`
    do timm (1.0.27) calcula `F.dropout(x, ...)` e DESCARTA o resultado: o dropout nunca
    acontece. Verificado lendo `Xception.forward_head`.

    A softmax fica fora do modelo: a CrossEntropyLoss já a aplica (é o mesmo que
    `sparse_categorical_crossentropy` sobre a saída softmax do Keras).
    """

    def __init__(self, n_classes: int, pretreinado: bool = True):
        super().__init__()
        self.base = timm.create_model(MODELO_TIMM, pretrained=pretreinado, num_classes=0)
        self.cabeca = nn.Sequential(nn.Dropout(0.5),
                                    nn.Linear(self.base.num_features, n_classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.cabeca(self.base(x))            # base(x) já sai do global average pool


def criar_modelo(n_classes: int, pretreinado: bool = True) -> ClassificadorXception:
    return ClassificadorXception(n_classes, pretreinado)


def _modulos_finetune(modelo: ClassificadorXception) -> list[nn.Module]:
    """O equivalente, no timm, às 50 últimas camadas da base no Keras (ver docstring)."""
    b = modelo.base
    return [
        b.block8.rep[7], b.block8.rep[8],               # Keras block9: sepconv3 + bn
        b.block9, b.block10, b.block11,                 # Keras blocks 10, 11, 12
        b.block12,                                      # Keras block13 + resíduo 1×1
        b.conv3, b.bn3, b.conv4, b.bn4,                 # Keras block14
    ]


def definir_fase(modelo: ClassificadorXception, fase: str) -> None:
    """'congelada': só a cabeça treina. 'finetune': cabeça + as 50 últimas camadas."""
    if fase not in ("congelada", "finetune"):
        raise ValueError(f"fase desconhecida: {fase}")
    for p in modelo.base.parameters():
        p.requires_grad = False
    for p in modelo.cabeca.parameters():
        p.requires_grad = True
    if fase == "finetune":
        for m in _modulos_finetune(modelo):
            for p in m.parameters():
                p.requires_grad = True
        # A conta à mão sobre o Keras (ver docstring, item 1) é conferida AQUI, e não
        # só escrita num comentário: um módulo a mais ou a menos em `_modulos_finetune`
        # treina outro conjunto de camadas e não dá erro nenhum — só deixa de ser a
        # reprodução do notebook original (D19). Pega num teste de fumaça, sem treinar.
        treinaveis = sum(p.numel() for p in modelo.base.parameters() if p.requires_grad)
        if treinaveis != TREINAVEIS_BASE_FINETUNE:
            raise RuntimeError(
                f"as 50 últimas camadas do Keras somam {TREINAVEIS_BASE_FINETUNE:,} "
                f"parâmetros, mas `_modulos_finetune` liberou {treinaveis:,}. O "
                f"mapeamento Keras→timm mudou e isto deixou de reproduzir o original."
            )


def contar_treinaveis(modelo: ClassificadorXception) -> tuple[int, int]:
    """(treináveis da base, treináveis da cabeça)."""
    base = sum(p.numel() for p in modelo.base.parameters() if p.requires_grad)
    topo = sum(p.numel() for p in modelo.cabeca.parameters() if p.requires_grad)
    return base, topo


def modo_treino(modelo: nn.Module) -> None:
    """train() para o Dropout da cabeça, mas BN sempre em inferência (training=False do Keras)."""
    modelo.train()
    for m in modelo.modules():
        if isinstance(m, nn.modules.batchnorm._BatchNorm):
            m.eval()


# ─────────────────────────────────────────────────────────────────────────────
# Checkpoint
# ─────────────────────────────────────────────────────────────────────────────

def carregar_checkpoint(caminho: Path, dispositivo: str | torch.device = "cpu"
                        ) -> tuple[ClassificadorXception, dict]:
    """Recria o modelo a partir do .pt salvo pelo train.py. Devolve (modelo em eval, meta)."""
    ck = torch.load(caminho, map_location=dispositivo, weights_only=False)
    if ck.get("tamanho") != TAMANHO or ck.get("modelo_timm") != MODELO_TIMM:
        raise ValueError(
            f"checkpoint incompatível com este código: {ck.get('modelo_timm')} @ "
            f"{ck.get('tamanho')} (esperado {MODELO_TIMM} @ {TAMANHO})")
    modelo = criar_modelo(len(ck["classes"]), pretreinado=False)
    modelo.load_state_dict(ck["state_dict"])
    modelo.to(dispositivo).eval()
    return modelo, ck


def dispositivo_padrao() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def duracao_para_texto(segundos: float) -> str:
    m, s = divmod(int(math.ceil(segundos)), 60)
    return f"{m}min{s:02d}s"
