"""Valida art.py: colores, anchos, limites del lienzo y coherencia.

    python tools/validate_art.py

No necesita Qt ni Windows. Pasalo despues de tocar cualquier sprite: pilla los
fallos que en la aplicacion solo se ven como un pixel raro o un cuelgue.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from desktop_pet import art  # noqa: E402

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
BOB_MAX = 1          # el respingo al andar sube un pixel
LIFT_MAX = 1         # patinar la sube uno (y anula el respingo, no se suman)
ALZADO_MAX = max(BOB_MAX, LIFT_MAX)


def revisar():
    fallos = []
    paleta = set(art.PALETTE)

    def pixeles(rows):
        for fila, linea in enumerate(rows):
            for col, ch in enumerate(linea):
                if ch != ".":
                    yield col, fila, ch

    # --- paleta ---------------------------------------------------------- #
    for clave, valor in art.PALETTE.items():
        if len(clave) != 1:
            fallos.append(f"paleta: la clave '{clave}' no es un solo caracter")
        if clave == ".":
            fallos.append("paleta: '.' esta reservado para el pixel vacio")
        if not HEX.match(valor):
            fallos.append(f"paleta: '{clave}' no es un color hex valido: {valor}")

    # --- sprite ---------------------------------------------------------- #
    for nombre, cuerpo in (("BODY", art.BODY), ("BODY_BLINK", art.BODY_BLINK),
                           ("BODY_HOLD", art.BODY_HOLD)):
        if len(cuerpo) != art.SPRITE_H - 1:
            fallos.append(f"{nombre}: {len(cuerpo)} filas, se esperaban "
                          f"{art.SPRITE_H - 1}")
        for fila, linea in enumerate(cuerpo):
            if len(linea) != art.SPRITE_W:
                fallos.append(f"{nombre} fila {fila}: ancho {len(linea)}, "
                              f"se esperaba {art.SPRITE_W}")
    for clave, linea in art.LEGS.items():
        if len(linea) != art.SPRITE_W:
            fallos.append(f"LEGS[{clave}]: ancho {len(linea)}")

    for col, fila in art.EYES:
        if not (0 <= col < art.SPRITE_W - 1 and 0 <= fila < art.SPRITE_H - 2):
            fallos.append(f"EYES: el ojo en ({col},{fila}) se sale del sprite")
    if art.EYE_PUPIL not in paleta:
        fallos.append(f"EYE_PUPIL '{art.EYE_PUPIL}' no esta en la paleta")

    # --- objetos y adornos (coordenadas del lienzo) ----------------------- #
    for coleccion, nombre in ((art.PROPS, "PROPS"), (art.OVERLAYS, "OVERLAYS")):
        for clave, valor in coleccion.items():
            frames = valor if nombre == "PROPS" else [valor]
            if not frames:
                fallos.append(f"{nombre}[{clave}]: sin fotogramas")
            for indice, (rows, col0, row0) in enumerate(frames):
                if len({len(r) for r in rows}) != 1:
                    fallos.append(f"{nombre}[{clave}] fotograma {indice}: "
                                  f"filas de distinto ancho")
                for col, fila, ch in pixeles(rows):
                    if ch not in paleta:
                        fallos.append(f"{nombre}[{clave}]: color '{ch}' desconocido")
                    x, y = col0 + col, row0 + fila
                    if not (0 <= x < art.CANVAS_W and 0 <= y < art.CANVAS_H):
                        fallos.append(f"{nombre}[{clave}] fotograma {indice}: "
                                      f"pixel fuera del lienzo ({x},{y})")

    # --- trajes ----------------------------------------------------------- #
    for clave, traje in art.COSTUMES.items():
        if "label" not in traje:
            fallos.append(f"traje {clave}: sin etiqueta")
        if not traje.get("accessory"):
            fallos.append(f"traje {clave}: sin accesorio")
        for grupo in ("parts", "accessory"):
            for indice, (rows, dcol, drow) in enumerate(traje.get(grupo, [])):
                if len({len(r) for r in rows}) != 1:
                    fallos.append(f"{clave}/{grupo}[{indice}]: filas desiguales")
                if grupo == "parts" and drow == 5 and (len(rows[0]) != art.SPRITE_W
                                                       or dcol != 0):
                    fallos.append(f"{clave}: el torso debe medir {art.SPRITE_W} "
                                  f"con dcol=0")
                for col, fila, ch in pixeles(rows):
                    if ch not in paleta:
                        fallos.append(f"{clave}/{grupo}: color '{ch}' desconocido")
                    x = art.PET_COL + dcol + col
                    for alzado in range(ALZADO_MAX + 1):
                        y = art.PET_ROW + drow + fila - alzado
                        if not (0 <= x < art.CANVAS_W and 0 <= y < art.CANVAS_H):
                            fallos.append(
                                f"{clave}/{grupo}[{indice}]: ({x},{y}) fuera del "
                                f"lienzo con alzado {alzado}")
                            break

    agrupados = [clave for _grupo, claves in art.COSTUME_GROUPS for clave in claves]
    if len(agrupados) != len(set(agrupados)):
        fallos.append("COSTUME_GROUPS: hay trajes repetidos")
    if sorted(agrupados) != sorted(art.COSTUMES):
        sobran = set(agrupados) - set(art.COSTUMES)
        faltan = set(art.COSTUMES) - set(agrupados)
        if sobran:
            fallos.append(f"COSTUME_GROUPS nombra trajes que no existen: {sobran}")
        if faltan:
            fallos.append(f"trajes sin grupo (no saldran en el menu): {faltan}")

    # --- actividades ------------------------------------------------------ #
    for clave, config in art.ACTIVITIES.items():
        for campo in ("label", "prop", "body", "legs", "speed", "overlay", "move"):
            if campo not in config:
                fallos.append(f"actividad {clave}: le falta '{campo}'")
        if config.get("prop") and config["prop"] not in art.PROPS:
            fallos.append(f"actividad {clave}: prop '{config['prop']}' no existe")
        if config.get("overlay") and config["overlay"] not in art.OVERLAYS:
            fallos.append(f"actividad {clave}: overlay '{config['overlay']}' no existe")
        if config.get("body") not in ("normal", "hold", "blink"):
            fallos.append(f"actividad {clave}: body '{config.get('body')}' raro")
        if config.get("legs") not in tuple(art.LEGS) + ("walk", "dangle"):
            fallos.append(f"actividad {clave}: legs '{config.get('legs')}' no existe")
        if not isinstance(config.get("speed"), int) or config["speed"] <= 0:
            fallos.append(f"actividad {clave}: speed debe ser un entero positivo")
        if config.get("lift", 0) > LIFT_MAX:
            fallos.append(f"actividad {clave}: lift {config['lift']} pasa de "
                          f"{LIFT_MAX}, sube el limite del validador si es a proposito")
    return fallos


def main() -> int:
    fallos = revisar()
    print(f"paleta {len(art.PALETTE)} colores | {len(art.COSTUMES)} trajes | "
          f"{len(art.PROPS)} objetos | {len(art.ACTIVITIES)} actividades")
    if fallos:
        print(f"\n{len(fallos)} problemas:")
        for f in fallos:
            print("  -", f)
        return 1
    print("arte correcto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
