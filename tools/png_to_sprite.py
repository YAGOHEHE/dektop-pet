"""Convierte una imagen pequenia en filas de texto listas para pegar en art.py.

    python tools/png_to_sprite.py traje.png
    python tools/png_to_sprite.py traje.png --ancho 11 --nombre "mi traje"
    python tools/png_to_sprite.py traje.png --ampliar        # sugiere colores nuevos

Cada pixel se asigna al color mas parecido de la paleta; los transparentes o
muy claros pasan a '.'. Con --ampliar, en vez de forzar la paleta, propone las
entradas nuevas que harian falta para respetar los colores del original.

Usa Pillow, que NO hace falta para ejecutar la mascota:
    pip install pillow
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from desktop_pet.art import PALETTE  # noqa: E402

LIBRES = "abcdefghijklmnopqrstuvwxyz0123456789"


def a_rgb(hexa: str):
    hexa = hexa.lstrip("#")
    return tuple(int(hexa[i:i + 2], 16) for i in (0, 2, 4))


def distancia(uno, otro) -> int:
    """Distancia de color ponderada: el ojo no pesa igual los tres canales."""
    dr, dg, db = (uno[0] - otro[0], uno[1] - otro[1], uno[2] - otro[2])
    return 2 * dr * dr + 4 * dg * dg + 3 * db * db


def mas_cercano(rgb, paleta):
    return min(paleta, key=lambda clave: distancia(rgb, paleta[clave]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("imagen", type=Path)
    parser.add_argument("--ancho", type=int, default=0,
                        help="reescala a este ancho antes de convertir")
    parser.add_argument("--nombre", default="pieza")
    parser.add_argument("--alfa", type=int, default=128,
                        help="por debajo de esta opacidad, pixel vacio")
    parser.add_argument("--ampliar", action="store_true",
                        help="propone colores nuevos en vez de forzar la paleta")
    args = parser.parse_args()

    try:
        from PIL import Image
    except ImportError:
        print("Falta Pillow: pip install pillow", file=sys.stderr)
        return 2

    imagen = Image.open(args.imagen).convert("RGBA")
    if args.ancho and imagen.width != args.ancho:
        alto = max(1, round(imagen.height * args.ancho / imagen.width))
        imagen = imagen.resize((args.ancho, alto), Image.NEAREST)

    paleta = {clave: a_rgb(valor) for clave, valor in PALETTE.items()}
    pixeles = imagen.load()

    if args.ampliar:
        cuenta = Counter()
        for y in range(imagen.height):
            for x in range(imagen.width):
                r, g, b, a = pixeles[x, y]
                if a >= args.alfa:
                    cuenta[(r, g, b)] += 1
        nuevos, libres = {}, [c for c in LIBRES.upper() if c not in paleta]
        for rgb, _veces in cuenta.most_common():
            if min(distancia(rgb, otro) for otro in paleta.values()) > 2600:
                if libres:
                    nuevos[libres.pop(0)] = rgb
        for clave, rgb in nuevos.items():
            paleta[clave] = rgb
        if nuevos:
            print("# colores nuevos para PALETTE:")
            for clave, rgb in nuevos.items():
                print(f'    "{clave}": "#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}",')
            print()

    filas = []
    for y in range(imagen.height):
        fila = ""
        for x in range(imagen.width):
            r, g, b, a = pixeles[x, y]
            fila += "." if a < args.alfa else mas_cercano((r, g, b), paleta)
        filas.append(fila)

    while filas and set(filas[0]) == {"."}:
        filas.pop(0)
    while filas and set(filas[-1]) == {"."}:
        filas.pop()

    print(f"# {args.nombre}: {imagen.width}x{len(filas)}")
    print("([" + ",\n  ".join(f'"{fila}"' for fila in filas) + "], 0, 5),")
    usados = {ch for fila in filas for ch in fila if ch != "."}
    print(f"# colores usados: {''.join(sorted(usados))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
