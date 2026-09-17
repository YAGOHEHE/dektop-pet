"""Que le apetece hacer segun la ventana que tengas delante.

Se mira el titulo de la ventana en primer plano, en minusculas, contra una
lista de palabras. La primera regla que encaja gana; dentro de ella, la
actividad se sortea para que no sea siempre la misma.
"""

from __future__ import annotations

import random

RULES = [
    (("visual studio", "code", "pycharm", "sublime", "intellij", "vim",
      "terminal", "powershell", "cmd.exe", "github", ".py", ".js", ".ts"),
     ("laptop",)),
    (("youtube", "spotify", "music", "vlc", "netflix", "twitch", "podcast",
      "prime video", "disney"),
     ("ukulele", "bailar", "popcorn")),
    (("word", "docs", ".pdf", "notion", "obsidian", "acrobat", "kindle"),
     ("book",)),
    (("excel", "sheets", "calc", "powerpoint", "jira", "trello", "asana"),
     ("cafe", "pesas")),
    (("steam", "epic games", "minecraft", "league of", "battle.net"),
     ("futbol", "patinar", "cybertruck")),
    (("whatsapp", "telegram", "slack", "discord", "teams", "outlook", "gmail"),
     ("cola", "cafe")),
    (("chrome", "firefox", "edge", "opera", "safari", "explorador", "explorer"),
     ("colgar", "pescar")),
]


def activity_for(title: str, chooser=random) -> str | None:
    """Actividad sugerida por el titulo, o None si no encaja ninguna regla."""
    if not title:
        return None
    title = title.lower()
    for palabras, actividades in RULES:
        if any(palabra in title for palabra in palabras):
            return chooser.choice(list(actividades))
    return None
