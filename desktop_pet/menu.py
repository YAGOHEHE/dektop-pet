"""El menu, en un solo sitio: lo usan el clic derecho y el icono de la bandeja."""

from __future__ import annotations

import random

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu

from .art import ACTIVITIES, COSTUME_GROUPS, COSTUMES


def _toggle(menu, parent, etiqueta, pet, clave):
    accion = QAction(etiqueta, parent, checkable=True)
    accion.setChecked(bool(getattr(pet, clave)))
    accion.triggered.connect(lambda v, k=clave: pet.set_flag(k, v))
    menu.addAction(accion)
    return accion


def build_menu(pet, parent=None) -> QMenu:
    parent = parent or pet
    menu = QMenu(parent)

    actions = menu.addMenu("Que haga algo")
    for key, config in ACTIVITIES.items():
        accion = QAction(config["label"], parent)
        accion.triggered.connect(lambda _c=False, k=key: pet.start_activity(k))
        actions.addAction(accion)
    actions.addSeparator()
    sorpresa = QAction("Lo que le apetezca", parent)
    sorpresa.triggered.connect(lambda: pet.start_activity(pet.choose_activity()))
    actions.addAction(sorpresa)

    trajes = menu.addMenu("Ponerse un traje")
    quitar = QAction("Sin traje", parent, checkable=True)
    quitar.setChecked(pet.costume is None)
    quitar.triggered.connect(lambda: pet.set_costume(None))
    trajes.addAction(quitar)
    trajes.addSeparator()
    for nombre_grupo, claves in COSTUME_GROUPS:
        grupo = trajes.addMenu(nombre_grupo)
        for key in claves:
            accion = QAction(COSTUMES[key]["label"], parent, checkable=True)
            accion.setChecked(pet.costume == key)
            accion.triggered.connect(lambda _c=False, k=key: pet.set_costume(k))
            grupo.addAction(accion)
    trajes.addSeparator()
    azar = QAction("Uno al azar", parent)
    azar.triggered.connect(lambda: pet.set_costume(random.choice(list(COSTUMES))))
    trajes.addAction(azar)
    _toggle(trajes, parent, "Que se cambie sola", pet, "auto_costume")

    if len(pet.monitors) > 1:
        pantallas = menu.addMenu("Ir a la pantalla")
        for indice, area in enumerate(pet.monitors, start=1):
            accion = QAction(f"Pantalla {indice} ({area[2] - area[0]} px)", parent)
            accion.triggered.connect(lambda _c=False, a=area: pet.go_to_monitor(a))
            pantallas.addAction(accion)

    comportamiento = menu.addMenu("Comportamiento")
    _toggle(comportamiento, parent, "Seguir el raton", pet, "follow_mouse")
    _toggle(comportamiento, parent, "Hacer caso a su humor", pet, "mood_enabled")
    _toggle(comportamiento, parent, "Mirar que ventana usas", pet,
            "context_enabled")

    recolocar = QAction("Recolocar", parent)
    recolocar.triggered.connect(pet.reset_position)
    menu.addAction(recolocar)

    diagnostico = QAction("Diagnostico", parent)
    diagnostico.triggered.connect(pet.show_report)
    menu.addAction(diagnostico)

    menu.addSeparator()
    salir = QAction("Salir", parent)
    salir.triggered.connect(QApplication.quit)
    menu.addAction(salir)
    return menu
