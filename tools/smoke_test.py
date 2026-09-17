"""Prueba de humo: ejecuta la mascota de verdad, pero sin Windows ni pantalla.

Usa StubBackend con ventanas inventadas y Qt en modo offscreen, asi que corre
en cualquier sistema y en integracion continua:

    python tools/smoke_test.py

Comprueba que el bucle no revienta en ningun estado, que todas las actividades
y trajes se dibujan, que salta entre ventanas, que no se escapa del escritorio
y que los ajustes sobreviven a un reinicio.
"""

from __future__ import annotations

import os
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "0")

from PySide6.QtWidgets import QApplication  # noqa: E402

from desktop_pet.art import ACTIVITIES, COSTUMES  # noqa: E402
from desktop_pet.context import activity_for  # noqa: E402
from desktop_pet.desktop import StubBackend  # noqa: E402
from desktop_pet.mood import Mood  # noqa: E402
from desktop_pet.pet import Pet  # noqa: E402
from desktop_pet.settings import Settings  # noqa: E402

fallos = []


def check(condicion, mensaje):
    if condicion:
        print(f"  ok   {mensaje}")
    else:
        fallos.append(mensaje)
        print(f"  FALLO {mensaje}")


def nueva_mascota(app, platforms=(), title="", carpeta=None):
    ajustes = Settings(Path(carpeta or tempfile.mkdtemp()) / "settings.json")
    mascota = Pet(StubBackend(platforms, title), ajustes)
    mascota.loop.stop()          # el bucle lo movemos a mano
    mascota.scanner.stop()
    return mascota


def main() -> int:
    random.seed(7)
    app = QApplication(sys.argv)

    pantalla = app.primaryScreen().availableGeometry()
    print(f"pantalla de prueba: {pantalla.width()}x{pantalla.height()}")
    ventanas = [
        (pantalla.left() + 100, pantalla.left() + 500, pantalla.top() + 300),
        (pantalla.left() + 620, pantalla.left() + 980, pantalla.top() + 380),
    ]

    print("\n1. bucle largo en todos los estados")
    mascota = nueva_mascota(app, ventanas, "visual studio code - main.py")
    estados, actividades = set(), set()
    for _ in range(9000):
        mascota.tick()
        estados.add(mascota.state)
        if mascota.activity:
            actividades.add(mascota.activity)
    izq, arriba, der, abajo = mascota.virtual_bounds
    check(len(estados) >= 4, f"visita varios estados: {sorted(estados)}")
    check(len(actividades) >= 3, f"hace varias actividades: {len(actividades)}")
    check(izq - 50 <= mascota.x <= der + 50, "no se escapa por los lados")
    check(mascota.y <= abajo + 50, "no se hunde por debajo del escritorio")

    print("\n2. todas las actividades se dibujan")
    for nombre in ACTIVITIES:
        mascota.start_activity(nombre)
        for _ in range(140):
            mascota.tick()
        celdas = mascota.current_cells()
        check(bool(celdas), f"actividad {nombre} pinta {len(celdas)} pixeles")

    print("\n3. todos los trajes se dibujan y caben en el lienzo")
    problemas = []
    for clave in COSTUMES:
        mascota.set_costume(clave)
        mascota.start_activity("popcorn")
        for _ in range(30):
            mascota.tick()
        if not mascota.current_cells():
            problemas.append(clave)
    check(not problemas, f"32 trajes pintados sin huecos ({problemas})")
    mascota.set_costume(None)

    print("\n4. salto de ventana a ventana")
    # HOP_CHANCE es 0.75, asi que a veces prefiere dejarse caer: se repite el
    # escenario varias veces y se mira el conjunto, no un intento suelto
    saltos, aterrizajes = 0, 0
    for intento in range(12):
        saltarina = nueva_mascota(app, ventanas)
        saltarina.refresh_world()
        x1, x2, y = saltarina.platforms[0]
        destino = saltarina.platforms[1]
        saltarina.x = x2 - 20 - (5 + 5.5) * 7
        saltarina.y = y - 12 * 7
        saltarina.state, saltarina.facing = "walk", 1
        saltarina.state_timer = 600
        for _ in range(260):
            saltarina.tick()
        saltos += saltarina.hops
        if (destino[0] <= saltarina.center_x <= destino[1]
                and abs(saltarina.feet - destino[2]) < 6):
            aterrizajes += 1
    check(saltos >= 6, f"salta el hueco casi siempre ({saltos}/12 intentos)")
    check(aterrizajes >= 5,
          f"aterriza en la ventana de enfrente ({aterrizajes}/12)")

    print("\n5. actividades de canto")
    pescadora = nueva_mascota(app, ventanas)
    pescadora.refresh_world()
    px1, px2, py = pescadora.platforms[0]
    pescadora.x = (px1 + px2) / 2
    pescadora.y = py - 12 * 7
    pescadora.state = "idle"
    pescadora.start_activity("pescar")
    check(pescadora.state == "edge", "primero va al canto")
    for _ in range(400):
        pescadora.tick()
        if pescadora.state == "act":
            break
    check(pescadora.activity == "pescar", "acaba pescando")
    check(min(abs(pescadora.center_x - px1), abs(pescadora.center_x - px2)) < 30,
          "se sienta pegada a un canto")

    print("\n6. ajustes que sobreviven al cierre")
    carpeta = tempfile.mkdtemp()
    primera = nueva_mascota(app, ventanas, carpeta=carpeta)
    primera.set_costume("skater")
    primera.set_flag("follow_mouse", False)
    primera.x, primera.y = 321.0, 123.0
    check(primera.save_settings(), "guarda sin errores")
    segunda = nueva_mascota(app, ventanas, carpeta=carpeta)
    check(segunda.costume == "skater", "recuerda el traje")
    check(segunda.follow_mouse is False, "recuerda las preferencias")
    check((int(segunda.x), int(segunda.y)) == (321, 123), "recuerda la posicion")

    print("\n7. humor y contexto")
    humor = Mood(random.Random(3))
    humor.levels["juego"] = 2.0
    elecciones = [humor.pick(list(ACTIVITIES), hour=15) for _ in range(300)]
    de_juego = sum(1 for e in elecciones if e in
                   ("ukulele", "bailar", "futbol", "patinar", "cybertruck", "pesas"))
    check(de_juego > len(elecciones) * 0.4,
          f"con pocas ganas de juego elige jugar ({de_juego}/300)")
    de_noche = [humor.pick(list(ACTIVITIES), hour=3) for _ in range(200)]
    check(de_noche.count("siesta") > 80,
          f"de madrugada suele dormir ({de_noche.count('siesta')}/200)")
    check(activity_for("Visual Studio Code - pet.py") == "laptop",
          "delante del editor se pone a programar")
    check(activity_for("YouTube - Mozilla Firefox") in
          ("ukulele", "bailar", "popcorn"), "con video, ocio")
    check(activity_for("") is None, "sin titulo no inventa nada")

    print("\n8. repintado solo cuando cambia el fotograma")
    quieta = nueva_mascota(app, ventanas)
    quieta.state = "idle"
    quieta.state_timer = 10**6
    quieta.blink_timer = 10**6
    quieta.repaint_if_changed()
    repintados = sum(1 for _ in range(600) if quieta.repaint_if_changed())
    check(repintados == 0, f"parada no repinta ({repintados} repintados en 600)")

    print()
    if fallos:
        print(f"FALLOS ({len(fallos)}):")
        for f in fallos:
            print("  -", f)
        return 1
    print("todo correcto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
