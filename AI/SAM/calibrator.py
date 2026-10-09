"""calibrator — escolha do conjunto de sondas e do limiar de cada litologia.

Implementa o protocolo da **D17** sobre o motor da **D18** (`docs/decisoes.md`).

Duas perguntas, duas fases, porque a imagem ideal para cada uma é oposta:

    Fase 1 · DESCOBERTA   -> QUAIS sondas entram nesta litologia?
                             Uma imagem: a mais rica em feições (descoberta.JPG).

    Fase 2 · LIMIAR       -> ONDE corto o score de cada sonda?
                             Quatro imagens simultâneas. UM limiar julgado contra
                             TRÊS casos (sutil / típica / forte) -- as três não
                             produzem três limiares para tirar média: elas são
                             júri, não medição (D17).

Por que isto é rápido: o SAM roda UMA vez por (imagem, sonda) com `conf` no piso
e o limiar é varrido offline sobre os scores em cache (**D18** — equivalência
provada na fonte do ultralytics e verificada por `verificar_d18.py`). Arrastar o
slider não toca a GPU.

O que este programa grava:
  - `rock_prompts.json`                    -> { litologia: { sonda: limiar } }
  - `selectRocks/<rocha>/calibracao.json`  -> o limiar, a contagem em cada vaga e
                                              o CRITÉRIO escrito pelo autor.
    O critério é obrigatório por decisão: escolher limiar "no olho" é exatamente
    o que a **D3** acusa o inspetor humano de fazer. Se não está escrito, não é
    critério.

Ele NÃO gera as máscaras finais em `results/` — isso é papel do `inference.py`.

Uso:
    ..\\.venv\\Scripts\\python.exe -m streamlit run calibrator.py
"""

# ── Monkey-patch CLIP antes de qualquer import do SAM — ver inference.py ──────
# Sem ele o SAM3 falha em silêncio, sem exceção e sem saída.
try:
    import clip as _clip
    import clip.simple_tokenizer as _clip_st
    if "__call__" not in _clip_st.SimpleTokenizer.__dict__:
        _clip_st.SimpleTokenizer.__call__ = (
            lambda self, texts, context_length=77, truncate=False:
            _clip.tokenize(texts, context_length=context_length, truncate=truncate)
        )
except ImportError:
    pass

import json
from datetime import datetime
from pathlib import Path

import altair as alt
import cv2
import numpy as np
import pandas as pd
import streamlit as st

import sam_cache

st.set_page_config(
    page_title="ARIA Calibrator",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Caminhos ──────────────────────────────────────────────────────────────────
SAM_DIR        = Path(__file__).parent.resolve()
SELECT_ROCKS   = SAM_DIR / "selectRocks"
PROMPTS_CONFIG = SAM_DIR / "rock_prompts.json"
DATASET_DIR    = (SAM_DIR / ".." / "dataset").resolve()

# O vocabulário do protocolo (as 4 vagas, as faixas de volume, a ordem de
# trabalho) mora no rock_viewer: é ele que cria as vagas. Importar em vez de
# repetir — se PAPEIS mudar lá, o calibrador acompanha (DRY, CLAUDE.md).
import rock_viewer as protocolo  # noqa: E402

# O rock_viewer resolve caminho relativo ao CWD porque é sempre chamado de
# AI/SAM/. O streamlit pode ser lançado de outro lugar, então fixamos em
# absoluto ANTES da primeira chamada (as funções com lru_cache leem estes
# globais do módulo).
protocolo.DATASET_DIR = DATASET_DIR
protocolo.SELECT_ROCKS_DIR = SELECT_ROCKS

PAPEIS = protocolo.PAPEL_CHAVES                 # descoberta -> sutil -> típica -> forte
PAPEIS_LIMIAR = tuple(p for p in PAPEIS if p.startswith("limiar_"))

# ── Sondas ────────────────────────────────────────────────────────────────────
# O cadastro de sondas (id de classe e cor) mora no `sondas.py`, um lugar só,
# compartilhado com o `inference.py`: as duas cópias que existiam antes tinham
# cores diferentes para a mesma sonda. Sonda fora do cadastro pode ser explorada
# aqui, mas não é salva — class_id inválido corrompe o .txt em silêncio (D8).
from sondas import CLASS_ID_MAP, cor  # noqa: E402

# Sugestões para a fase de descoberta. Não é escopo fechado — o escopo é o
# CLASS_ID_MAP (D8); estas são só ideias de sonda para experimentar.
BIBLIOTECA: dict[str, list[str]] = {
    "Físicas":     ["crack", "fracture", "fissure", "scratch", "chip", "pit"],
    "Minerais":    ["vein", "mineral vein", "quartz vein", "crystal"],
    "Coloração":   ["Stain", "Dark patches", "light spot", "rust stain", "oxidation"],
    "Contextuais": ["crack on stone surface", "dark stain on marble",
                    "surface defect on rock"],
}

LIMIAR_INICIAL = 0.10   # ponto de partida neutro quando não há valor anterior

# Casas decimais do limiar. O número é único no programa de propósito: o
# `select_slider` manda para o navegador as opções JÁ FORMATADAS e devolve a
# escolha pelo texto. Se duas posições da grade formatassem igual ("0.0846"), o
# slider saltaria para a outra. Arredondar a grade nas MESMAS casas em que ela é
# exibida torna a correspondência bijetora — e mantém em disco exatamente o
# valor que o autor viu na tela.
CASAS = 4
FORMATO = f"%.{CASAS}f"


def arredondar(v: float) -> float:
    return round(float(v), CASAS)


OVERRIDES = dict(
    task="segment", mode="predict",
    model=str(SAM_DIR / ".." / "models" / "sam3.pt"),
    imgsz=644, half=False, save=False,
)


# ══════════════════════════════════════════════════════════════════════════════
# Leitura e escrita de configuração
# ══════════════════════════════════════════════════════════════════════════════

def ler_prompts() -> dict:
    if not PROMPTS_CONFIG.exists():
        return {}
    with PROMPTS_CONFIG.open(encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def gravar_prompts(rocha: str, config: dict[str, float]) -> None:
    raw: dict = {}
    if PROMPTS_CONFIG.exists():
        with PROMPTS_CONFIG.open(encoding="utf-8") as f:
            raw = json.load(f)
    raw[rocha] = config
    with PROMPTS_CONFIG.open("w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
        f.write("\n")


# O `calibracao.json` tem um leitor só, no protocolo. Este módulo é o único que
# **escreve** o arquivo (`gravar_calib`), e o lê pelo mesmo caminho que o
# `inference.py` usa — antes havia um leitor em cada arquivo, discordando sobre
# o que fazer com JSON corrompido.
caminho_calib = protocolo.caminho_calibracao
ler_calib = protocolo.ler_calibracao


def gravar_calib(rocha: str, sondas: dict[str, float], regra: dict[str, float | None],
                 marcacoes_por_sonda: dict, criterio: str) -> None:
    """Registra os DOIS limiares, o efeito de cada um e o critério do autor.

    `limiar_regra` é o joelho puro (**D17**) — é ele que vai para os dois braços
    do Experimento 1 (**D5**), porque comparar regra contra regra mantém uma
    variável só. `limiar_trabalho` é o que o autor de fato escolheu, e é o que
    vai para produção. Gravar os dois torna a divergência **medível**: a taxa de
    concordância com a regra é resultado reportável, não anedota.
    """
    import ultralytics
    detalhe = {}
    for sonda, trabalho in sondas.items():
        r = regra.get(sonda)
        detalhe[sonda] = {
            "limiar_trabalho": arredondar(trabalho),
            "limiar_regra": None if r is None else arredondar(r),
            "divergencia": None if r is None else round(arredondar(trabalho) - arredondar(r), 5),
            "marcacoes_por_vaga": marcacoes_por_sonda.get(sonda, {}),
        }
    divergentes = [k for k, v in detalhe.items()
                   if v["divergencia"] not in (None, 0.0)]
    dados = {
        "rock": rocha,
        "faixa": protocolo.faixa_of(rocha),
        "protocolo": "D17 (4 vagas, regra = joelho) + D18 (varredura offline)",
        "calibrado_em": datetime.now().isoformat(timespec="seconds"),
        "criterio": criterio.strip(),
        "conf_piso_cache": float(sam_cache.CONF_PISO),
        "ultralytics": ultralytics.__version__,
        "sondas_na_regra": len(detalhe) - len(divergentes),
        "sondas_divergentes": divergentes,
        "sondas": detalhe,
    }
    f = caminho_calib(rocha)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")


# Mora no protocolo junto com o leitor: o `inference.py` faz a mesma pergunta e
# não pode importar uma interface Streamlit para isso.
calibracao_desatualizada = protocolo.calibracao_desatualizada


def estado_rocha(rocha: str) -> str:
    """'sem_vagas' | 'vagas_parciais' | 'pronta' | 'calibrada' | 'desatualizada'

    "Calibrada" é ter `calibracao.json` — ou seja, limiar E critério escritos.
    Não basta o SAM ter rodado: `rock_prompts.json` é provisório (D15).

    "Desatualizada" é ter `calibracao.json` cujas imagens mudaram depois: o
    limiar continua escrito, mas não foi escolhido nas 4 vagas atuais, então
    não conta como calibrada.
    """
    n = len(protocolo.slots_preenchidos(rocha))
    if n == 0:
        return "sem_vagas"
    if (calib := ler_calib(rocha)) is not None:
        return "desatualizada" if calibracao_desatualizada(rocha, calib) else "calibrada"
    return "pronta" if n == len(PAPEIS) else "vagas_parciais"


# ══════════════════════════════════════════════════════════════════════════════
# Cache de scores (D18)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="Carregando SAM3 (3,4 GB) — só na primeira vez…")
def _predictor():
    from ultralytics.models.sam import SAM3SemanticPredictor
    return SAM3SemanticPredictor(overrides=OVERRIDES)


def arquivo_cache(rocha: str, papel: str, sonda: str) -> Path:
    return sam_cache.caminho_cache(SELECT_ROCKS / rocha, papel, sonda)


@st.cache_data(show_spinner=False)
def _ler(rocha: str, papel: str, sonda: str, _assinatura: float):
    """(scores, polígonos) de um par (vaga, sonda), já sem detecção degenerada.

    Descarta os pares cujo polígono tem menos de 3 pontos: o SAM devolve
    detecção com máscara vazia, e ela nunca vira rótulo (ver
    `sam_cache.indices_validos`). Filtrar aqui, na entrada, mantém contagem,
    curva e desenho contando exatamente a mesma coisa.
    """
    scores, polys = sam_cache.carregar(arquivo_cache(rocha, papel, sonda))
    manter = sam_cache.indices_validos(polys)
    return scores[manter], [polys[i] for i in manter]


def ler(rocha: str, papel: str, sonda: str):
    f = arquivo_cache(rocha, papel, sonda)
    if not f.exists():
        return None
    return _ler(rocha, papel, sonda, f.stat().st_mtime)


def pares_faltantes(rocha: str, sondas: list[str]) -> list[tuple[str, Path, str]]:
    vagas = protocolo.slots_preenchidos(rocha)
    return [
        (papel, img, sonda)
        for papel, img in vagas.items()
        for sonda in sondas
        if not arquivo_cache(rocha, papel, sonda).exists()
    ]


def capturar(rocha: str, pendentes: list[tuple[str, Path, str]]) -> int:
    """Roda o SAM no piso para os pares que faltam e grava o cache.

    Agrupa por imagem de propósito: `set_image` custa ~1 s e cada sonda depois
    dele custa ~55 ms. Chamar uma vez por imagem, e não por par, é a diferença
    entre ~6 s e ~25 s para uma litologia inteira.
    """
    if not pendentes:
        return 0
    predictor = _predictor()
    por_imagem: dict[tuple[str, Path], list[str]] = {}
    for papel, img, sonda in pendentes:
        por_imagem.setdefault((papel, img), []).append(sonda)

    barra = st.progress(0.0, text="Capturando…")
    feitos = 0
    for (papel, img), sondas in por_imagem.items():
        predictor.set_image(str(img))
        for sonda in sondas:
            barra.progress(feitos / len(pendentes), text=f"`{papel}` · `{sonda}`")
            scores, polys = sam_cache.capturar(predictor, img, sonda)
            sam_cache.salvar(arquivo_cache(rocha, papel, sonda), scores, polys)
            feitos += 1
    barra.empty()
    _ler.clear()
    semear_da_regra(rocha)
    return feitos


# ══════════════════════════════════════════════════════════════════════════════
# Desenho
# ══════════════════════════════════════════════════════════════════════════════

def abrir_imagem(caminho: Path):
    """Lê a imagem sem passar o caminho para o OpenCV.

    ⚠️ `cv2.imread` NÃO abre caminho com caractere não-ASCII no Windows — e o
    caminho deste projeto tem acento ("…ARIA - Análise e Reconhecimento…").
    O erro é traiçoeiro porque o ultralytics, ao ser importado, monkey-patcha
    `cv2.imread` para uma versão que aceita Unicode: quem importa ultralytics
    antes não vê o bug. Este módulo só importa ultralytics quando vai capturar
    cache, então na abertura normal do app o `imread` cru voltaria None e todas
    as previews quebrariam. `np.fromfile` + `imdecode` não depende disso.
    """
    dados = np.fromfile(caminho, dtype=np.uint8)
    if dados.size == 0:
        return None
    return cv2.imdecode(dados, cv2.IMREAD_COLOR)


@st.cache_data(show_spinner=False)
def _imagem_base(caminho: str, _assinatura: float, lado: int = 780):
    """Imagem reduzida (BGR). Reduzir é o que deixa o slider instantâneo:
    preencher 150 polígonos num 1300x830 a cada rerun não é grátis."""
    im = abrir_imagem(Path(caminho))
    if im is None:
        return None
    h, w = im.shape[:2]
    if max(h, w) > lado:
        e = lado / max(h, w)
        im = cv2.resize(im, (int(w * e), int(h * e)), interpolation=cv2.INTER_AREA)
    return im


def imagem_base(caminho: Path):
    return _imagem_base(str(caminho), caminho.stat().st_mtime)


def desenhar(base, camadas: list[tuple[list[np.ndarray], tuple[int, int, int]]],
             alpha: float = 0.50):
    """Sobrepõe polígonos normalizados (xyn) na imagem. Devolve RGB para o st.image.

    Preenche e **não** contorna, de propósito. `Masks.xyn` usa
    `masks2segments(strategy="all")`, que funde os contornos disjuntos de uma
    mesma detecção numa só poligonal, ligando-os por pontes de ida e volta.
    Medido em `siena_white/descoberta` (crack @ 0,08): 45 das 76 detecções têm
    mais de um contorno. A ponte tem área ~zero — no agregado o polígono infla
    só 2,4% sobre a máscara (IoU 0,93) —, então o preenchimento é fiel; mas
    traçada, ela vira uma reta atravessando a chapa e polui a imagem justamente
    onde o autor precisa enxergar a feição. Preencher mostra o que de fato vira
    rótulo.

    ⚠️ O caso individual não é tão benigno quanto o agregado: numa detecção com
    18 contornos o polígono chegou a 2,5x a área da máscara. Isso é ruído de
    rótulo a tratar no pós-processamento do Professor (roadmap, Fase 3.0).
    """
    out = base.copy()
    h, w = out.shape[:2]
    for polys, cor_bgr in camadas:
        contornos = [
            np.round(np.asarray(p, dtype=np.float32) * (w, h)).astype(np.int32)
            for p in polys if len(p) > 2
        ]
        if not contornos:
            continue
        sobre = out.copy()
        cv2.fillPoly(sobre, contornos, cor_bgr)
        out = cv2.addWeighted(sobre, alpha, out, 1.0 - alpha, 0)
    return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)


def _hex(bgr: tuple[int, int, int]) -> str:
    b, g, r = bgr
    return f"#{r:02x}{g:02x}{b:02x}"


def preview(caminho: Path, camadas) -> None:
    """Desenha as camadas sobre a vaga e mostra. Avisa em vez de estourar se a
    imagem não abrir (ver `abrir_imagem`)."""
    base = imagem_base(caminho)
    if base is None:
        st.error(f"não consegui abrir `{caminho.name}`")
        return
    st.image(desenhar(base, camadas), width="stretch")


# ══════════════════════════════════════════════════════════════════════════════
# Estado de sessão
# ══════════════════════════════════════════════════════════════════════════════

def _iniciar_estado() -> None:
    padroes = {
        "rocha": None,
        "candidatas": {},   # {rocha: [sonda, ...]}   sondas em exame
        "entram":    {},    # {rocha: {sonda: bool}}  decisão da fase 1
        "limiares":  {},    # {rocha: {sonda: float}}
        "criterio":  {},    # {rocha: str}
    }
    for k, v in padroes.items():
        st.session_state.setdefault(k, v)


def trocar_rocha(rocha: str) -> None:
    """Semeia o estado da litologia a partir do que já existe em disco."""
    st.session_state.rocha = rocha
    calib = ler_calib(rocha)
    if calib:
        anterior = {s: d.get("limiar_trabalho", d.get("limiar"))
                    for s, d in calib.get("sondas", {}).items()}
        st.session_state.criterio[rocha] = calib.get("criterio", "")
    else:
        # rock_prompts.json é PROVISÓRIO (D15) — serve de ponto de partida, não
        # de calibração feita.
        anterior = dict(ler_prompts().get(rocha, {}))

    candidatas = list(CLASS_ID_MAP) + [s for s in anterior if s not in CLASS_ID_MAP]
    st.session_state.candidatas[rocha] = candidatas
    st.session_state.entram[rocha] = {s: (s in anterior) for s in candidatas}
    st.session_state.limiares[rocha] = {
        s: float(anterior.get(s, LIMIAR_INICIAL)) for s in candidatas
    }
    st.session_state.criterio.setdefault(rocha, "")
    if calib is None:
        # Sem calibração em disco, o ponto de partida é a REGRA — não o número
        # provisório do rock_prompts.json, que a D15 declara sem valor.
        semear_da_regra(rocha)


def sondas_candidatas(rocha: str) -> list[str]:
    return st.session_state.candidatas.get(rocha, list(CLASS_ID_MAP))


def sondas_do_conjunto(rocha: str) -> list[str]:
    entram = st.session_state.entram.get(rocha, {})
    return [s for s in sondas_candidatas(rocha) if entram.get(s)]


def limiar(rocha: str, sonda: str) -> float:
    return float(st.session_state.limiares.get(rocha, {}).get(sonda, LIMIAR_INICIAL))


def definir_limiar(rocha: str, sonda: str, valor: float) -> None:
    st.session_state.limiares.setdefault(rocha, {})[sonda] = arredondar(valor)


# ══════════════════════════════════════════════════════════════════════════════
# Contagem e curva
# ══════════════════════════════════════════════════════════════════════════════

def marcacoes(rocha: str, papel: str, sonda: str, conf: float) -> int:
    dados = ler(rocha, papel, sonda)
    if dados is None:
        return 0
    scores, _ = dados
    return int((scores > conf).sum())


def scores_reunidos(rocha: str, sonda: str, papeis) -> np.ndarray:
    partes = [d[0] for p in papeis if (d := ler(rocha, p, sonda)) is not None]
    if not partes:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(partes)


def grade_de_limiares(scores: np.ndarray, atual: float) -> list[float]:
    """Posições do slider. Log-espaçadas (D18) e sempre contendo o valor atual —
    senão o select_slider recusa o valor que veio digitado no campo."""
    g = sam_cache.limiares_sugeridos(scores, n=80)
    vals = {arredondar(v) for v in g}
    vals.add(arredondar(atual))
    return sorted(vals)


def curva_das_vagas_de_limiar(rocha: str, sonda: str,
                              grade: list[float]) -> list[tuple[float, int]]:
    """Curva somada das TRÊS vagas de limiar — a entrada da regra (D17).

    A vaga `descoberta` fica de fora de propósito: ela foi escolhida por ser a
    mais rica em feições, e entrar na conta puxaria o limiar para cima — que é
    justamente o viés de seleção por visibilidade que o protocolo existe para
    evitar.
    """
    dados = [d for pap in PAPEIS_LIMIAR if (d := ler(rocha, pap, sonda)) is not None]
    return [(float(t), sum(int((d[0] > t).sum()) for d in dados)) for t in grade]


def limiar_da_regra(rocha: str, sonda: str) -> float | None:
    """O valor que a REGRA produz — o joelho da curva (**D17**, fechada em 26/09).

    Constrói a própria grade em vez de reaproveitar a do slider: o valor da regra
    não pode depender do que o autor escolheu, senão deixa de ser reproduzível.
    É este número que vai para os dois braços do Experimento 1 (**D5**).
    """
    scores = scores_reunidos(rocha, sonda, PAPEIS_LIMIAR)
    if len(scores) == 0:
        return None
    grade = [float(v) for v in sam_cache.limiares_sugeridos(scores, n=80)]
    j = sam_cache.joelho(curva_das_vagas_de_limiar(rocha, sonda, grade))
    return None if j is None else arredondar(j)


def semear_da_regra(rocha: str) -> None:
    """Põe o limiar de cada sonda no valor da regra. O autor parte dela e diverge
    se quiser — nunca o contrário (D17)."""
    for sonda in sondas_candidatas(rocha):
        j = limiar_da_regra(rocha, sonda)
        if j is not None:
            definir_limiar(rocha, sonda, j)
            for k in (f"sl_{rocha}_{sonda}", f"ni_{rocha}_{sonda}"):
                st.session_state.pop(k, None)   # o widget recarrega do novo valor


def curva(rocha: str, sonda: str, grade: list[float]) -> pd.DataFrame:
    linhas = []
    for papel in PAPEIS:
        dados = ler(rocha, papel, sonda)
        if dados is None:
            continue
        for t, n in sam_cache.curva_de_limiar(dados[0], grade):
            linhas.append({"limiar": t, "marcacoes": n,
                           "vaga": protocolo.PAPEL_INFO[papel][0]})
    return pd.DataFrame(linhas)


# ══════════════════════════════════════════════════════════════════════════════
# Barra lateral
# ══════════════════════════════════════════════════════════════════════════════

ICONE = {"sem_vagas": "·", "vagas_parciais": "◐", "pronta": "○", "calibrada": "●",
         "desatualizada": "⊘"}


def barra_lateral() -> None:
    with st.sidebar:
        st.markdown("### 🪨 ARIA Calibrator")

        rochas = protocolo.find_all_rocks()          # ordenadas por volume (D6/D15)
        feitas, total = protocolo.contar_progresso()
        estados = {r: estado_rocha(r) for r in rochas}
        n_calib = sum(1 for e in estados.values() if e == "calibrada")
        n_prontas = sum(1 for e in estados.values() if e == "pronta")

        st.caption(
            f"**{feitas}/{total}** vagas selecionadas · "
            f"**{n_prontas}** prontas para calibrar · "
            f"**{n_calib}/{len(rochas)}** calibradas"
        )
        st.progress(feitas / total if total else 0.0)

        st.divider()
        st.caption("● calibrada · ⊘ desatualizada · ○ 4/4 pronta · ◐ incompleta · `·` sem vagas")
        with st.container(height=260, border=False):
            for r in rochas:
                e = estados[r]
                n = len(protocolo.slots_preenchidos(r))
                rotulo = f"{ICONE[e]} {r}  ·  {protocolo.faixa_of(r)} {n}/{len(PAPEIS)}"
                atual = st.session_state.rocha == r
                if st.button(rotulo, key=f"rb_{r}", width="stretch",
                             type="primary" if atual else "secondary",
                             disabled=(e == "sem_vagas")):
                    if not atual:
                        trocar_rocha(r)
                        st.rerun()

        rocha = st.session_state.rocha
        if rocha is None:
            return

        st.divider()
        st.markdown(f"**Sondas em exame** — `{rocha}`")
        st.caption(
            "Tudo que estiver aqui é capturado no piso de confiança. Quem *entra* "
            "no conjunto se decide na aba Descoberta."
        )

        candidatas = sondas_candidatas(rocha)
        faltam = pares_faltantes(rocha, candidatas)
        n_pares = len(protocolo.slots_preenchidos(rocha)) * len(candidatas)
        if faltam:
            st.warning(f"{len(faltam)} de {n_pares} pares sem cache.")
        else:
            st.success(f"{n_pares} pares em cache.")

        if st.button("⟳ Capturar o que falta", type="primary", width="stretch",
                     disabled=not faltam):
            n = capturar(rocha, faltam)
            st.toast(f"{n} pares capturados.")
            st.rerun()

        with st.expander("+ sonda exploratória"):
            st.caption(
                "Serve para testar se uma palavra faz o modelo responder. Sonda "
                "fora do CLASS_ID_MAP **não é salva** (D8) — para promovê-la, "
                "registre-a no `inference.py` e aqui."
            )
            sugestoes = [s for ss in BIBLIOTECA.values() for s in ss
                         if s not in candidatas]
            escolha = st.selectbox("da biblioteca", ["—"] + sugestoes,
                                   key="sel_biblioteca")
            livre = st.text_input("ou digite", key="txt_sonda",
                                  placeholder="ex: crack on granite surface")
            nova = livre.strip() or (escolha if escolha != "—" else "")
            if st.button("Adicionar", width="stretch", disabled=not nova):
                if nova not in candidatas:
                    st.session_state.candidatas[rocha] = candidatas + [nova]
                    st.session_state.entram[rocha][nova] = False
                    st.session_state.limiares[rocha][nova] = LIMIAR_INICIAL
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# Aba 1 — Descoberta: quais sondas entram
# ══════════════════════════════════════════════════════════════════════════════

def aba_descoberta(rocha: str) -> None:
    vagas = protocolo.slots_preenchidos(rocha)
    img = vagas.get("descoberta")

    st.markdown(
        "**A pergunta desta aba:** esta sonda faz o modelo responder a algo que "
        "existe de verdade nesta litologia? Se não responde a nada aqui — na chapa "
        "escolhida justamente por ser a mais rica — ela não entra (D17)."
    )
    if img is None:
        st.warning(f"Falta a vaga `descoberta`. Rode `python rock_viewer.py {rocha}`.")
        return

    candidatas = sondas_candidatas(rocha)
    entram = st.session_state.entram.setdefault(rocha, {})
    if pares_faltantes(rocha, candidatas):
        st.info("Capture o cache na barra lateral para ver as máscaras.")

    origem = (protocolo.ler_meta(rocha).get("slots", {})
              .get("descoberta", {}).get("origem", "?"))
    col_a, col_b = st.columns([3, 2])
    with col_a:
        explora = st.slider(
            "Limiar de exploração (só para olhar — não é o limiar salvo)",
            min_value=0.005, max_value=0.60, value=0.08, step=0.005,
            format="%.3f", key="sl_explora",
        )
    with col_b:
        st.caption(f"vaga `descoberta` · arquivo `{img.name}` · origem `{origem}`")

    st.divider()

    cols = st.columns(3)
    for i, sonda in enumerate(candidatas):
        dados = ler(rocha, "descoberta", sonda)
        with cols[i % 3]:
            registrada = sonda in CLASS_ID_MAP
            etiqueta = f"`{sonda}`" + ("" if registrada else " ⚠️ não registrada")
            st.markdown(etiqueta)
            if dados is None:
                st.caption("sem cache")
                continue
            scores, polys = dados
            _, vis = sam_cache.filtrar(scores, polys, explora)
            entra = st.checkbox(
                f"entra no conjunto · {len(vis)} marcações",
                value=entram.get(sonda, False),
                key=f"cb_{rocha}_{sonda}",
                disabled=not registrada,
                help=None if registrada else
                "Sonda fora do CLASS_ID_MAP não pode virar rótulo (D8).",
            )
            entram[sonda] = entra and registrada
            if len(scores):
                preview(img, [(vis, cor(sonda))])
                st.caption(f"scores no piso: {scores.min():.3f} – {scores.max():.3f} "
                           f"({len(scores)} detecções)")
            else:
                st.caption("o modelo não respondeu a esta sonda nesta imagem")


# ══════════════════════════════════════════════════════════════════════════════
# Aba 2 — Limiar: um slider, quatro previews
# ══════════════════════════════════════════════════════════════════════════════

def _sync(origem: str, destino: str, rocha: str, sonda: str):
    def _cb():
        v = arredondar(st.session_state[origem])
        st.session_state[origem] = v      # o campo exato pode vir com mais casas
        st.session_state[destino] = v
        definir_limiar(rocha, sonda, v)
    return _cb


def _painel_conjunto(rocha: str, conjunto: list[str], vagas: dict, ncols: int) -> None:
    st.caption("Todas as sondas nos limiares atuais — é assim que o conjunto chega "
               "no `.txt` de treino.")
    st.markdown(
        "&nbsp;&nbsp;".join(
            f'<span style="display:inline-block;width:.7em;height:.7em;'
            f'background:{_hex(cor(s))};border-radius:2px"></span> '
            f"<code>{s}</code> {FORMATO % limiar(rocha, s)}"
            for s in conjunto
        ),
        unsafe_allow_html=True,
    )
    cols = st.columns(ncols)
    for i, papel in enumerate(PAPEIS):
        if papel not in vagas:
            continue
        camadas, total = [], 0
        for s in conjunto:
            dados = ler(rocha, papel, s)
            if dados is None:
                continue
            _, vis = sam_cache.filtrar(dados[0], dados[1], limiar(rocha, s))
            camadas.append((vis, cor(s)))
            total += len(vis)
        with cols[i % ncols]:
            st.markdown(f"**{protocolo.PAPEL_INFO[papel][0]}** · {total} marcações")
            preview(vagas[papel], camadas)


def _painel_comparar(rocha: str, sonda: str, conf: float, vagas: dict) -> None:
    """As 3 vagas de limiar lado a lado, marcada em cima e crua embaixo em
    cada coluna -- o limiar é o MESMO nas três (D17), então julgar a sonda
    é comparar as três de uma vez, não vaga por vaga."""
    cols = st.columns(len(PAPEIS_LIMIAR))
    for col, papel in zip(cols, PAPEIS_LIMIAR):
        with col:
            if papel not in vagas:
                st.info(f"Falta `{papel}` — rode `python rock_viewer.py {rocha}`.")
                continue

            rotulo, dica, _ = protocolo.PAPEL_INFO[papel]
            dados = ler(rocha, papel, sonda)
            if dados is None:
                st.markdown(f"**{rotulo}**", help=dica)
                st.caption("sem cache")
                continue

            n = int((dados[0] > conf).sum())
            st.markdown(f"**{rotulo}** · {n} marcações", help=dica)
            _, vis = sam_cache.filtrar(dados[0], dados[1], conf)
            preview(vagas[papel], [(vis, cor(sonda))])

            st.caption("sem marcação")
            preview(vagas[papel], [])


def aba_limiar(rocha: str) -> None:
    conjunto = sondas_do_conjunto(rocha)
    if not conjunto:
        st.info("Nenhuma sonda no conjunto ainda. Decida na aba **Descoberta**.")
        return

    vagas = protocolo.slots_preenchidos(rocha)
    ausentes = [p for p in PAPEIS_LIMIAR if p not in vagas]
    if ausentes:
        st.warning(
            "Faltam as vagas " + ", ".join(f"`{p}`" for p in ausentes) +
            ". O limiar é julgado contra os três casos (D17) — rode "
            f"`python rock_viewer.py {rocha}`."
        )

    modo = st.radio("modo", ["uma sonda", "conjunto completo"], horizontal=True,
                    key="rd_modo", label_visibility="collapsed")
    layout = st.radio("layout", ["4 colunas", "2 colunas", "comparar"], horizontal=True,
                      key="rd_layout", label_visibility="collapsed")
    ncols = 2 if layout == "2 colunas" else 4

    if modo == "conjunto completo":
        _painel_conjunto(rocha, conjunto, vagas, ncols)
        return

    sonda = st.radio("sonda", conjunto, horizontal=True, key="rd_sonda")
    scores_lim = scores_reunidos(rocha, sonda, PAPEIS_LIMIAR)
    if len(scores_lim) == 0:
        st.warning(f"`{sonda}` não produziu marcação nenhuma nas vagas de limiar. "
                   "Ou falta cache, ou a sonda não responde nesta litologia.")
        return

    atual = limiar(rocha, sonda)
    grade = grade_de_limiares(scores_lim, atual)
    sl, ni = f"sl_{rocha}_{sonda}", f"ni_{rocha}_{sonda}"
    st.session_state.setdefault(sl, arredondar(atual))
    st.session_state.setdefault(ni, arredondar(atual))

    c1, c2 = st.columns([5, 1])
    with c1:
        st.select_slider(
            f"limiar de `{sonda}`", options=grade, key=sl,
            format_func=lambda v: FORMATO % v,
            on_change=_sync(sl, ni, rocha, sonda),
        )
    with c2:
        st.number_input("valor exato", min_value=0.0001, max_value=1.0, step=0.001,
                        format=FORMATO, key=ni,
                        on_change=_sync(ni, sl, rocha, sonda))
    conf = limiar(rocha, sonda)

    if layout == "comparar":
        _painel_comparar(rocha, sonda, conf, vagas)
        return

    # ── Os quatro previews simultâneos (D18) ──────────────────────────────────
    cols = st.columns(ncols)
    for i, papel in enumerate(PAPEIS):
        if papel not in vagas:
            continue
        dados = ler(rocha, papel, sonda)
        with cols[i % ncols]:
            rotulo, dica, _ = protocolo.PAPEL_INFO[papel]
            eh_limiar = papel in PAPEIS_LIMIAR
            n = 0 if dados is None else int((dados[0] > conf).sum())
            st.markdown(
                f"**{rotulo}** · {n} marcações" +
                ("" if eh_limiar else "  \n:gray[referência — não julga o limiar]"),
                help=dica,
            )
            if dados is None:
                st.caption("sem cache")
                continue
            _, vis = sam_cache.filtrar(dados[0], dados[1], conf)
            preview(vagas[papel], [(vis, cor(sonda))])

    # ── Curva limiar × marcações ──────────────────────────────────────────────
    st.divider()
    df = curva(rocha, sonda, grade)
    if df.empty:
        return
    j = limiar_da_regra(rocha, sonda)

    linhas = alt.Chart(df).mark_line(interpolate="step-after").encode(
        x=alt.X("limiar:Q", scale=alt.Scale(type="log"), title="limiar (escala log)"),
        y=alt.Y("marcacoes:Q", title="marcações"),
        color=alt.Color("vaga:N", title=None, scale=alt.Scale(scheme="tableau10")),
        tooltip=["vaga", alt.Tooltip("limiar:Q", format=".4f"), "marcacoes"],
    )
    camadas = [linhas, alt.Chart(pd.DataFrame({"v": [conf]}))
               .mark_rule(color="#e6e9ef", strokeWidth=2).encode(x="v:Q")]
    if j:
        camadas.append(alt.Chart(pd.DataFrame({"v": [j]}))
                       .mark_rule(color="#fbbf24", strokeDash=[5, 4]).encode(x="v:Q"))
    st.altair_chart(alt.layer(*camadas).properties(height=240), width="stretch")

    legenda = f"Linha clara: o **limiar de trabalho** (**{FORMATO % conf}**)."
    if j:
        delta = conf - j
        legenda += (f" Tracejado âmbar: o **limiar da regra** — o joelho das três vagas "
                    f"(**{FORMATO % j}**). É o valor da regra que vai para os dois braços "
                    "do Experimento 1 (D5); o de trabalho é o que vai para produção.")
        if abs(delta) < 1e-9:
            legenda += " Você está **na regra**."
        else:
            legenda += (f" Você **divergiu da regra** em {delta:+.4f} — isso é permitido e "
                        "fica gravado no `calibracao.json` junto do seu critério (D17).")
    st.caption(legenda)
    st.caption("Para que lado errar, na dúvida: **mais apertado**. A literatura de "
               "pseudo-rotulagem privilegia precisão porque a rede memoriza rótulo "
               "errado (D17).")


# ══════════════════════════════════════════════════════════════════════════════
# Aba 3 — Fechar: escrever o critério e salvar
# ══════════════════════════════════════════════════════════════════════════════

def aba_fechar(rocha: str) -> None:
    conjunto = sondas_do_conjunto(rocha)
    if not conjunto:
        st.info("Nada a salvar: nenhuma sonda no conjunto.")
        return

    vagas = protocolo.slots_preenchidos(rocha)
    contagens: dict[str, dict[str, int]] = {}
    regra: dict[str, float | None] = {}
    linhas = []
    for s in conjunto:
        conf = limiar(rocha, s)
        r = limiar_da_regra(rocha, s)
        regra[s] = r
        por_vaga = {p: marcacoes(rocha, p, s, conf) for p in vagas}
        contagens[s] = por_vaga
        linhas.append({
            "sonda": s, "id": CLASS_ID_MAP.get(s, -1),
            "regra": r, "trabalho": arredondar(conf),
            "divergência": None if r is None else round(arredondar(conf) - r, 4),
            **{protocolo.PAPEL_INFO[p][0]: n for p, n in por_vaga.items()},
        })
    st.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch")

    n_div = sum(1 for s in conjunto
                if regra[s] is not None and arredondar(limiar(rocha, s)) != regra[s])
    if n_div:
        st.caption(f"Você divergiu da regra em **{n_div}** de {len(conjunto)} sondas. "
                   "Os dois valores vão para o `calibracao.json` — a divergência é "
                   "resultado reportável (D17), não problema.")
    else:
        st.caption("Todas as sondas estão **no valor da regra**. "
                   "Concordância é evidência a favor dela (D17).")

    total_limiar = sum(n for s in conjunto for p, n in contagens[s].items()
                       if p in PAPEIS_LIMIAR)
    st.caption(f"{total_limiar} marcações somadas nas três vagas de limiar — é o "
               "volume que o Aluno veria se treinasse nestas três chapas.")

    st.divider()
    st.markdown("**Critério** — por que estes limiares, e não outros?")
    st.caption(
        "Obrigatório. Escolher limiar no olho é o que a **D3** acusa o inspetor "
        "humano de fazer; o critério escrito é o que torna a marcação auditável. "
        "Ele também é a matéria-prima para fechar o TODO da D17 — a regra que "
        "produz o valor é a mesma para as 45 litologias, só o valor muda."
    )
    criterio = st.text_area(
        "critério", key=f"ta_{rocha}", label_visibility="collapsed", height=120,
        value=st.session_state.criterio.get(rocha, ""),
        placeholder="ex: subi até o ponto em que a vaga típica para de marcar "
                    "matriz limpa, aceitando perder as feições mais fracas da "
                    "vaga sutil; a vaga forte continua com todas as óbvias.",
    )
    st.session_state.criterio[rocha] = criterio

    nao_registradas = [s for s in conjunto if s not in CLASS_ID_MAP]
    if nao_registradas:
        st.error("Fora do CLASS_ID_MAP (D8), não serão salvas: " +
                 ", ".join(f"`{s}`" for s in nao_registradas))

    if st.button("💾 Salvar calibração", type="primary",
                 disabled=not criterio.strip()):
        salvar = {s: arredondar(limiar(rocha, s)) for s in conjunto
                  if s in CLASS_ID_MAP}
        gravar_prompts(rocha, salvar)
        gravar_calib(rocha, salvar, regra, contagens, criterio)
        st.success(f"`rock_prompts.json` e `{protocolo.CALIB_NAME}` gravados.")
        st.rerun()
    if not criterio.strip():
        st.caption(":gray[Escreva o critério para habilitar o salvamento.]")

    calib = ler_calib(rocha)
    if calib:
        with st.expander(f"calibracao.json em disco — {calib.get('calibrado_em', '?')}"):
            st.json(calib)


# ══════════════════════════════════════════════════════════════════════════════
# Principal
# ══════════════════════════════════════════════════════════════════════════════

ABERTURA = """
Escolhe **quais sondas** e **qual limiar** cada litologia usa, seguindo o
protocolo das 4 vagas (**D17**) sobre a varredura offline (**D18**).

| | |
|---|---|
| **1 · Descoberta** | Na chapa mais rica: que sondas respondem a algo real? |
| **2 · Limiar** | Um slider, quatro previews. Um limiar julgado em três casos. |
| **3 · Fechar** | A contagem, o critério escrito e o salvamento. |

O SAM roda **uma vez** por (imagem, sonda) no piso de confiança; o limiar é
varrido sobre o cache, sem GPU. Arrastar o slider é instantâneo.

Selecione uma litologia na barra lateral. As apagadas ainda não têm vaga nenhuma —
rode `python rock_viewer.py` para selecionar as imagens.
"""


def principal() -> None:
    rocha = st.session_state.rocha
    if rocha is None:
        st.markdown("## 🪨 ARIA Calibrator")
        st.markdown(ABERTURA)
        return

    meta = protocolo.ler_meta(rocha)
    n = len(protocolo.slots_preenchidos(rocha))
    e = estado_rocha(rocha)
    selo = {"calibrada": "● calibrada", "desatualizada": "⊘ desatualizada",
            "pronta": "○ pronta",
            "vagas_parciais": "◐ incompleta", "sem_vagas": "sem vagas"}[e]

    st.markdown(f"## `{rocha}`")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("faixa", meta.get("faixa", protocolo.faixa_of(rocha)))
    c2.metric("imagens da litologia",
              meta.get("total_imagens_litologia", protocolo.count_images(rocha)))
    c3.metric("vagas", f"{n}/{len(PAPEIS)}")
    c4.metric("estado", selo)

    if e == "calibrada":
        st.info("Esta litologia já tem `calibracao.json`. Salvar de novo sobrescreve.")
    elif e == "desatualizada":
        quais = ", ".join(protocolo.vagas_trocadas_depois(rocha, ler_calib(rocha) or {}))
        st.warning(
            f"**Calibração desatualizada.** O `calibracao.json` foi salvo antes de "
            f"a(s) vaga(s) **{quais}** serem substituídas, então o limiar gravado "
            f"não foi escolhido nas 4 imagens atuais. Recalibrar e salvar resolve."
        )

    t1, t2, t3 = st.tabs(["1 · Descoberta", "2 · Limiar", "3 · Fechar"])
    with t1:
        aba_descoberta(rocha)
    with t2:
        aba_limiar(rocha)
    with t3:
        aba_fechar(rocha)


# O streamlit executa este arquivo com __name__ == "__main__". O guard nao muda
# nada no app e deixa o modulo importavel por script de teste sem subir a UI.
if __name__ == "__main__":
    _iniciar_estado()
    barra_lateral()
    principal()
