"""Humor: tres necesidades que deciden a que le apetece jugar.

En vez de sortear la actividad a pelo, cada actividad cubre una necesidad y se
elige con mas probabilidad la que cubre la que esta mas baja. La hora del
sistema tambien pesa: de madrugada casi siempre le toca dormir.
"""

from __future__ import annotations

import random

# Que necesidad cubre cada actividad
COVERS = {
    "siesta": "energia",
    "cafe": "energia",
    "colgar": "energia",
    "pescar": "calma",
    "book": "calma",
    "laptop": "calma",
    "popcorn": "hambre",
    "pizza": "hambre",
    "cola": "hambre",
    "ukulele": "juego",
    "bailar": "juego",
    "futbol": "juego",
    "patinar": "juego",
    "cybertruck": "juego",
    "pesas": "juego",
}

NEEDS = ("energia", "hambre", "juego", "calma")

# Cuanto baja cada necesidad por tick (a 60 fps, ~1 punto por minuto)
DECAY = {"energia": 0.00028, "hambre": 0.00035, "juego": 0.00045, "calma": 0.00022}
RECOVER = 34.0            # cuanto sube la necesidad cubierta al terminar


class Mood:
    def __init__(self, seed_random=random):
        self.random = seed_random
        self.levels = {need: self.random.uniform(55.0, 85.0) for need in NEEDS}

    def tick(self, n: int = 1) -> None:
        for need, rate in DECAY.items():
            self.levels[need] = max(0.0, self.levels[need] - rate * n)

    def satisfy(self, activity: str) -> None:
        need = COVERS.get(activity)
        if need:
            self.levels[need] = min(100.0, self.levels[need] + RECOVER)

    def lowest(self) -> str:
        return min(self.levels, key=self.levels.get)

    def is_night(self, hour: int) -> bool:
        return hour >= 23 or hour < 6

    def pick(self, activities, hour: int | None = None) -> str:
        """Elige actividad con peso segun necesidad, sin volverse repetitiva."""
        opciones = list(activities)
        if not opciones:
            return ""
        if hour is None:
            hour = 12

        if self.is_night(hour) and "siesta" in opciones and self.random.random() < 0.6:
            return "siesta"

        floja = self.lowest()
        pesos = []
        for nombre in opciones:
            need = COVERS.get(nombre)
            peso = 1.0
            if need == floja:
                peso = 6.0
            elif need:
                # cuanto mas baja la necesidad que cubre, mas apetecible
                peso = 1.0 + (100.0 - self.levels[need]) / 45.0
            if nombre == "siesta" and not self.is_night(hour):
                peso *= 0.35
            pesos.append(peso)
        return self.random.choices(opciones, weights=pesos, k=1)[0]

    def report(self) -> str:
        return " ".join(f"{need}={self.levels[need]:.0f}" for need in NEEDS)
