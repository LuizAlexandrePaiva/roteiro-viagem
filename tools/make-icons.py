#!/usr/bin/env python3
"""
Regenera os ícones do aplicativo a partir de um desenho SVG.

Uso:
    pip install cairosvg
    python3 tools/make-icons.py

Gera, na raiz do projeto:
    icon-192.png         ícone do Android (manifest)
    icon-512.png         ícone do Android em alta resolução e tela de abertura
    apple-touch-icon.png ícone do iOS, embutido no HTML como data URI
    favicon.svg          ícone da aba do navegador

Para trocar o desenho, edite APP_ICON e FAVICON abaixo. Mantenha o conteúdo
dentro dos 60% centrais da tela: o Android recorta o ícone em círculo
("maskable") e o que estiver perto das bordas é cortado.
"""

import base64
import pathlib
import sys

try:
    import cairosvg
except ImportError:
    sys.exit("Falta a dependência: pip install cairosvg")

RAIZ = pathlib.Path(__file__).resolve().parent.parent

FUNDO = "#16232E"
TRACO = "#EFF1EC"
NUCLEO = "#A6215E"

DRONE = f"""
  <g stroke='{TRACO}' stroke-width='2.2' stroke-linecap='round' fill='none'>
    <path d='M11.4 11.4 L20.6 20.6'/><path d='M20.6 11.4 L11.4 20.6'/>
  </g>
  <g stroke='{TRACO}' stroke-width='1.9' fill='none'>
    <circle cx='9.2' cy='9.2' r='3.6'/><circle cx='22.8' cy='9.2' r='3.6'/>
    <circle cx='9.2' cy='22.8' r='3.6'/><circle cx='22.8' cy='22.8' r='3.6'/>
  </g>
  <circle cx='16' cy='16' r='3.1' fill='{NUCLEO}'/>
"""

# Ícone do aplicativo: fundo inteiro, sem cantos arredondados.
# Os sistemas aplicam a própria máscara.
APP_ICON = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'>
<rect width='512' height='512' fill='{FUNDO}'/>
<g transform='translate(256,256) scale(12.5) translate(-16,-16)'>{DRONE}</g>
</svg>"""

# Favicon: cantos arredondados por conta própria, porque o navegador não mascara.
FAVICON = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>
<rect width='32' height='32' rx='7' fill='{FUNDO}'/>{DRONE}</svg>"""


def main() -> None:
    (RAIZ / "favicon.svg").write_text(FAVICON, encoding="utf-8")

    tamanhos = {
        "icon-192.png": 192,
        "icon-512.png": 512,
        "apple-touch-icon.png": 180,
    }
    for nome, px in tamanhos.items():
        cairosvg.svg2png(
            bytestring=APP_ICON.encode(),
            write_to=str(RAIZ / nome),
            output_width=px,
            output_height=px,
        )
        print(f"gerado  {nome}  {px}x{px}")

    b64 = base64.b64encode((RAIZ / "apple-touch-icon.png").read_bytes()).decode()
    print(
        "\nO iOS não aceita SVG no apple-touch-icon, por isso ele vai embutido\n"
        "no index.html como data URI. Substitua a linha correspondente por:\n\n"
        f'<link rel="apple-touch-icon" sizes="180x180" href="data:image/png;base64,{b64[:48]}…">\n\n'
        "A cadeia completa em base64 tem "
        f"{len(b64)} caracteres."
    )


if __name__ == "__main__":
    main()
