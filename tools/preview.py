"""Genera una lamina PNG con todos los trajes o todas las actividades.

    python tools/preview.py trajes trajes.png
    python tools/preview.py actividades actividades.png

Dibuja con el motor de verdad (las mismas celdas que pinta la aplicacion), asi
que si algo se ve mal aqui, se ve mal en pantalla. No necesita Windows.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "0")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from desktop_pet.art import ACTIVITIES, CANVAS_H, CANVAS_W, COSTUMES  # noqa: E402
from desktop_pet.desktop import StubBackend  # noqa: E402
from desktop_pet.pet import COLORS, Pet  # noqa: E402
from desktop_pet.settings import Settings  # noqa: E402

ESCALA = 8
COLUMNAS = 6
PIE = 18
FONDO = QColor("#20242B")


def dibujar(painter, mascota, ox, oy, etiqueta):
    for col, fila, ch in mascota.mirrored(mascota.current_cells()):
        painter.fillRect(ox + col * ESCALA, oy + fila * ESCALA,
                         ESCALA, ESCALA, COLORS[ch])
    painter.setPen(QColor("#D8D8D8"))
    painter.drawText(ox + 4, oy + CANVAS_H * ESCALA + 13, etiqueta)


def lamina(mascota, items, salida: Path):
    filas = (len(items) + COLUMNAS - 1) // COLUMNAS
    ancho = COLUMNAS * CANVAS_W * ESCALA
    alto = filas * (CANVAS_H * ESCALA + PIE)
    pixmap = QPixmap(ancho, alto)
    pixmap.fill(FONDO)
    painter = QPainter(pixmap)
    painter.setFont(QFont("DejaVu Sans", 8))
    painter.setRenderHint(QPainter.Antialiasing, False)
    for indice, (preparar, etiqueta) in enumerate(items):
        preparar()
        mascota.ticks = 24            # un fotograma intermedio de la animacion
        ox = (indice % COLUMNAS) * CANVAS_W * ESCALA
        oy = (indice // COLUMNAS) * (CANVAS_H * ESCALA + PIE)
        dibujar(painter, mascota, ox, oy, etiqueta)
    painter.end()
    pixmap.save(str(salida))
    return ancho, alto


def main() -> int:
    que = sys.argv[1] if len(sys.argv) > 1 else "trajes"
    salida = Path(sys.argv[2] if len(sys.argv) > 2 else f"{que}.png")

    app = QApplication(sys.argv[:1])
    mascota = Pet(StubBackend(), Settings(Path(tempfile.mkdtemp()) / "s.json"))
    mascota.loop.stop()
    mascota.scanner.stop()
    mascota.blink_timer = 10 ** 6         # sin parpadeos en la lamina
    mascota.facing = 1

    if que.startswith("act"):
        items = []
        for clave, config in ACTIVITIES.items():
            def preparar(k=clave):
                mascota.set_costume(None)
                mascota.state = "act"
                mascota.activity = k
            items.append((preparar, config["label"]))
    else:
        items = [((lambda: (setattr(mascota, "state", "idle"),
                            mascota.set_costume(None))), "Sin traje")]
        for clave, traje in COSTUMES.items():
            def preparar(k=clave):
                mascota.state = "idle"
                mascota.activity = None
                mascota.set_costume(k)
            items.append((preparar, traje["label"]))

    ancho, alto = lamina(mascota, items, salida)
    print(f"{salida} ({ancho}x{alto}) con {len(items)} casillas")
    _ = app
    return 0


if __name__ == "__main__":
    sys.exit(main())
