"""Arranque: conciencia de DPI, mascota, icono de bandeja y guardado al salir."""

from __future__ import annotations

import os
import sys

from .desktop import get_backend

# Debe estar ANTES de crear QApplication. Con el escalado de Qt desactivado,
# las coordenadas de Qt son pixeles fisicos y coinciden con las nativas, que es
# lo que permite que el multimonitor no se desalinee.
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "0")

from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap  # noqa: E402
from PySide6.QtWidgets import QApplication, QSystemTrayIcon  # noqa: E402

from .art import BODY, LEGS, PALETTE, SPRITE_H, SPRITE_W  # noqa: E402
from .menu import build_menu  # noqa: E402
from .pet import Pet  # noqa: E402
from .settings import Settings  # noqa: E402


def pet_icon(px: int = 64) -> QIcon:
    """Dibuja el sprite en un pixmap para usarlo de icono de bandeja."""
    escala = max(1, px // max(SPRITE_W, SPRITE_H))
    pixmap = QPixmap(SPRITE_W * escala, (SPRITE_H + 1) * escala)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    for fila, linea in enumerate(list(BODY) + [LEGS["idle"]]):
        for col, ch in enumerate(linea):
            if ch != ".":
                painter.fillRect(col * escala, fila * escala, escala, escala,
                                 QColor(PALETTE[ch]))
    painter.end()
    return QIcon(pixmap)


def build_tray(pet, app) -> QSystemTrayIcon | None:
    """Icono de bandeja con el mismo menu. None si el sistema no tiene bandeja."""
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return None
    tray = QSystemTrayIcon(pet_icon(), app)
    tray.setToolTip("Mascota de escritorio")
    # el menu se reconstruye en cada apertura para que los checks esten al dia
    menu_holder = {}

    def refresh():
        pet.refresh_world()
        menu_holder["menu"] = build_menu(pet, None)
        tray.setContextMenu(menu_holder["menu"])

    def on_activated(reason):
        refresh()                                   # checks siempre al dia
        if reason == QSystemTrayIcon.Trigger:       # clic: traerla a la vista
            pet.reset_position()
            pet.show()
            pet.raise_()

    refresh()
    tray.activated.connect(on_activated)
    tray.show()
    return tray


def main() -> int:
    backend = get_backend()
    backend.prepare()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)    # vive en la bandeja, no en la ventana

    settings = Settings()
    pet = Pet(backend, settings)
    pet.show()

    tray = build_tray(pet, app)
    if tray is None:
        app.setQuitOnLastWindowClosed(True)

    app.aboutToQuit.connect(pet.save_settings)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
