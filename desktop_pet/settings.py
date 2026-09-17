"""Ajustes que sobreviven al cierre: traje, posicion y preferencias.

Se guarda en %APPDATA%\\desktop_pet\\settings.json (o ~/.config/desktop_pet en
el resto de sistemas). Nunca revienta la aplicacion: si el archivo esta roto o
no hay permisos, se sigue con los valores por defecto.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULTS = {
    "costume": None,
    "auto_costume": True,
    "follow_mouse": True,
    "mood_enabled": True,
    "context_enabled": True,
    "x": None,
    "y": None,
}


def config_path() -> Path:
    base = os.environ.get("APPDATA")
    if base:
        carpeta = Path(base) / "desktop_pet"
    else:
        carpeta = Path(os.environ.get("XDG_CONFIG_HOME",
                                      Path.home() / ".config")) / "desktop_pet"
    return carpeta / "settings.json"


class Settings:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else config_path()
        self.data = dict(DEFAULTS)
        self.load()

    def load(self) -> None:
        try:
            crudo = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if isinstance(crudo, dict):
            # solo se aceptan claves conocidas: un archivo editado a mano no
            # puede meter atributos raros en la mascota
            for clave in DEFAULTS:
                if clave in crudo:
                    self.data[clave] = crudo[clave]

    def save(self) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporal = self.path.with_suffix(".tmp")
            temporal.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
            temporal.replace(self.path)     # escritura atomica
            return True
        except OSError:
            return False

    def get(self, clave: str):
        return self.data.get(clave, DEFAULTS.get(clave))

    def set(self, clave: str, valor) -> None:
        if clave in DEFAULTS:
            self.data[clave] = valor

    def update(self, **pares) -> None:
        for clave, valor in pares.items():
            self.set(clave, valor)
