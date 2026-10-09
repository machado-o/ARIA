"""ambiente — diz em que máquina você está e o que ela pode rodar.

**Por que existe.** O Henrique alterna entre dois PCs com hardware diferente, e
por isso o índice CUDA, a versão do torch e a do ultralytics *são diferentes de
propósito* — não há nada a "acertar". O problema nunca foi a diferença: foi
escrever o número de uma das máquinas num documento compartilhado, como se fosse
verdade das duas. Foi o que aconteceu com o `CLAUDE.md` e com a **D18**, que
afirmavam `ultralytics 8.4.61` sendo que o venv deste PC tem a 8.4.52.

A regra que resolve: **documento compartilhado não guarda número de máquina.**
Quando precisar saber, rode isto:

    cd AI
    .venv\\Scripts\\python.exe ambiente.py

A única versão que tem peso metodológico é a do **ultralytics**, porque a
equivalência da **D18** depende do `postprocess` dela. Essa não fica a cargo da
memória de ninguém: o `verificar_d18.py` grava cada versão verificada em
`SAM/d18_verificado.json`, que **vai para o git** — verificar numa máquina vale
para a outra. Este script lê esse registro e diz se a versão instalada aqui já
está coberta.
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path

# O console do Windows abre em cp1252 e os acentos saem trocados. Mesmo remendo
# do rock_viewer.py: força UTF-8, degradando o caractere em vez de derrubar.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

AI_DIR = Path(__file__).parent.resolve()
REGISTRO_D18 = AI_DIR / "SAM" / "d18_verificado.json"

# O que cada máquina tem de ter por conta própria: pesado, fora do git.
PESOS = {
    "SAM3 (Professor)": AI_DIR / "models" / "sam3.pt",
    "Xception (roteador)": AI_DIR / "models" / "xception_480.pt",
}


def linha(rotulo: str, valor: object) -> None:
    print(f"  {rotulo:<22} {valor}")


def driver_nvidia() -> str:
    """Nome da GPU e versão do driver, via nvidia-smi. Não falha se não houver."""
    try:
        saida = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version",
             "--format=csv,noheader"],
            capture_output=True, text=True, timeout=20, check=True,
        ).stdout.strip()
        return saida.splitlines()[0].strip() if saida else "(sem resposta)"
    except (OSError, subprocess.SubprocessError):
        return "(nvidia-smi indisponível)"


def versao(modulo: str) -> str:
    """Versão do módulo, ou o motivo de não dar para saber.

    Distingue "não está instalado" de "está instalado e quebrou ao importar":
    devolver "(não instalado)" nos dois casos manda procurar no lugar errado.
    """
    try:
        return __import__(modulo).__version__
    except ImportError:
        return "(não instalado)"
    except Exception as e:                  # noqa: BLE001 — queremos o motivo, não o silêncio
        return f"(instalado, mas falhou ao importar: {type(e).__name__}: {e})"


def estado_d18(versao_ultra: str) -> tuple[str, str]:
    """A D18 já foi verificada nesta versão do ultralytics? (marca, explicação)"""
    if not REGISTRO_D18.exists():
        return "?", (f"{REGISTRO_D18.name} não existe — nenhuma versão verificada "
                     "ainda. Rode `verificar_d18.py` de AI/SAM/.")
    try:
        registro = json.loads(REGISTRO_D18.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return "!", f"{REGISTRO_D18.name} está ilegível ({e})."
    if versao_ultra in registro:
        r = registro[versao_ultra]
        return "ok", (f"verificada em {r.get('verificado_em', '?')} "
                      f"({r.get('comparacoes', '?')} comparações, "
                      f"máquina {r.get('maquina', '?')})")
    return "!", ("esta versão NÃO foi verificada. Versões no registro: "
                 f"{', '.join(registro) or 'nenhuma'}. Rode `verificar_d18.py` "
                 "de AI/SAM/ antes de calibrar nela (D18).")


def main() -> int:
    ultra = versao("ultralytics")

    print("\nMáquina")
    linha("nome", platform.node())
    linha("sistema", f"{platform.system()} {platform.release()}")
    linha("GPU / driver", driver_nvidia())

    print("\nInterpretador e bibliotecas")
    linha("python", platform.python_version())
    linha("executável", sys.executable)
    linha("torch", versao("torch"))
    try:
        import torch
        linha("CUDA do torch", torch.version.cuda or "(build sem CUDA)")
        linha("GPU visível ao torch",
              torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NENHUMA")
    except ImportError:
        pass
    linha("ultralytics", ultra)
    linha("streamlit", versao("streamlit"))
    linha("timm", versao("timm"))
    linha("opencv (cv2)", versao("cv2"))

    print("\nPesos (fora do git — cada máquina tem os seus)")
    for nome, caminho in PESOS.items():
        if caminho.exists():
            linha(nome, f"ok  {caminho.stat().st_size / 2**30:.2f} GB")
        else:
            linha(nome, f"FALTA  ({caminho})")

    print("\nD18 — varredura offline")
    marca, texto = estado_d18(ultra)
    simbolo = {"ok": "[OK]", "!": "[ATENÇÃO]", "?": "[?]"}[marca]
    print(f"  {simbolo} ultralytics {ultra}: {texto}")

    print("\nNenhum número deste relatório deve ser copiado para documento "
          "compartilhado:\n  as duas máquinas são diferentes de propósito.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
