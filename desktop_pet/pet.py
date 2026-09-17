"""El widget de la mascota: fisica, maquina de estados y dibujo.

No sabe nada de Windows: todo lo que necesita del escritorio se lo da un
DesktopBackend. Eso permite ejecutarlo sin Windows para probarlo.
"""

from __future__ import annotations

import datetime
import random

from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QPainter, QRegion
from PySide6.QtWidgets import QMessageBox, QWidget

from . import context
from .art import (ACTIVITIES, BODY, BODY_BLINK, BODY_HOLD, CANVAS_H, CANVAS_W,
                  COSTUMES, EYES, EYE_PUPIL, LEGS, OVERLAYS, PALETTE, PET_BOTTOM,
                  PET_COL, PET_ROW, PROPS, SPRITE_W)
from .config import (ACTIVITY_CHANCE, CONTEXT_CHANCE, COSTUME_CHANCE,
                     EDGE_MARGIN, GAZE_RANGE, GRAVITY, HOP_CHANCE, HOP_DOWN_MAX,
                     HOP_REACH, HOP_UP_MAX, HOP_VX, HOP_VY, MAX_FALL, SCALE,
                     SCAN_MS, THROW_FACTOR, TICK_MS, TRAVEL_CHANCE, WALK_SPEED)
from .desktop import monitor_work_areas
from .mood import Mood
from .settings import Settings

COLORS = {clave: QColor(valor) for clave, valor in PALETTE.items()}


class Pet(QWidget):
    def __init__(self, backend, settings: Settings | None = None):
        super().__init__()
        self.backend = backend
        self.settings = settings or Settings()

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
            | Qt.Tool | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(CANVAS_W * SCALE, CANVAS_H * SCALE)
        self.setCursor(Qt.OpenHandCursor)

        self.handle = int(self.winId())
        self.state = "fall"    # idle | walk | act | edge | travel | fall | drag
        self.activity = None
        self.pending_activity = None      # actividad que hara al llegar al canto
        self.edge_target = None
        self.travel_target = None
        self.facing = 1
        self.vx = self.vy = 0.0
        self.ticks = 0
        self.fall_ticks = 0
        self.hops = 0
        self.state_timer = 60
        self.blink_timer = random.randint(120, 300)
        self.mood = Mood()

        self.costume = self.settings.get("costume")
        self.auto_costume = bool(self.settings.get("auto_costume"))
        self.follow_mouse = bool(self.settings.get("follow_mouse"))
        self.mood_enabled = bool(self.settings.get("mood_enabled"))
        self.context_enabled = bool(self.settings.get("context_enabled"))
        if self.costume not in COSTUMES:
            self.costume = None

        self._frame_key = None
        self._drag_offset = None
        self._last_pos = None

        self.platforms = []
        self.monitors = []
        self.transform = (0, 0, 1.0, 1.0, 0, 0)
        self.refresh_world()
        self.restore_position()

        self.loop = QTimer(self, interval=TICK_MS, timeout=self.tick)
        self.loop.start()
        self.scanner = QTimer(self, interval=SCAN_MS, timeout=self.refresh_world)
        self.scanner.start()

    # ---- mundo -------------------------------------------------------------- #

    def refresh_world(self):
        self.monitors = monitor_work_areas()
        self.transform = self.backend.transform()
        qx, qy, fx, fy, wx, wy = self.transform
        self.platforms = [
            (qx + (x1 - wx) * fx, qx + (x2 - wx) * fx, qy + (y - wy) * fy)
            for x1, x2, y in self.backend.window_platforms(self.handle)
        ]

    def restore_position(self):
        """Vuelve donde estaba la ultima vez, si ese sitio sigue existiendo."""
        x, y = self.settings.get("x"), self.settings.get("y")
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            cx = x + (PET_COL + SPRITE_W / 2) * SCALE
            if any(left <= cx < right for left, _t, right, _b in self.monitors):
                self.x, self.y = float(x), float(y)
                self.move(int(self.x), int(self.y))
                return
        area = self.monitors[0]
        self.x = float(area[2] - self.width() - 80)
        self.y = float(area[1] + 40)
        self.move(int(self.x), int(self.y))

    @property
    def feet(self) -> float:
        return self.y + PET_BOTTOM * SCALE

    @property
    def center_x(self) -> float:
        return self.x + (PET_COL + SPRITE_W / 2) * SCALE

    @property
    def virtual_bounds(self):
        left = min(m[0] for m in self.monitors)
        top = min(m[1] for m in self.monitors)
        right = max(m[2] for m in self.monitors)
        bottom = max(m[3] for m in self.monitors)
        return left, top, right, bottom

    def monitor_floors(self, cx: float):
        return sorted(bottom for left, _t, right, bottom in self.monitors
                      if left <= cx < right)

    def floor_for(self, cx: float, feet: float):
        for bottom in self.monitor_floors(cx):
            if bottom >= feet - 6:
                return bottom
        return None

    def support_at(self, cx: float, feet: float, tolerance: float = 5.0):
        floor = self.floor_for(cx, feet)
        if floor is not None and abs(feet - floor) <= tolerance:
            return floor
        for x1, x2, y in self.platforms:
            if x1 <= cx <= x2 and abs(feet - y) <= tolerance:
                return y
        return None

    def platform_under(self, tolerance: float = 5.0):
        """Ventana sobre la que esta de pie: (x1, x2, y). None si es el suelo."""
        cx, feet = self.center_x, self.feet
        for x1, x2, y in self.platforms:
            if x1 <= cx <= x2 and abs(feet - y) <= tolerance:
                return (x1, x2, y)
        return None

    def platforms_under(self, cx: float) -> bool:
        return any(x1 <= cx <= x2 and y >= self.feet - 5
                   for x1, x2, y in self.platforms)

    def clamp_horizontal(self):
        left, _t, right, _b = self.virtual_bounds
        min_x = left - PET_COL * SCALE
        max_x = right - (PET_COL + SPRITE_W) * SCALE
        if self.x < min_x:
            self.x = min_x
            return -1
        if self.x > max_x:
            self.x = max_x
            return 1
        return 0

    # ---- bucle -------------------------------------------------------------- #

    def tick(self):
        self.ticks += 1
        self.blink_timer -= 1
        if self.blink_timer < -8:
            self.blink_timer = random.randint(120, 320)
        if self.mood_enabled:
            self.mood.tick()

        if self.state == "drag":
            self.repaint_if_changed()
            return

        if self.state != "fall":
            self.fall_ticks = 0

        if self.state == "fall":
            self.do_fall()
        elif self.state == "walk":
            self.do_walk()
        elif self.state == "travel":
            self.do_travel()
        elif self.state == "edge":
            self.do_edge()
        elif self.state == "act":
            self.do_act()
        else:
            self.do_idle()

        self.move(int(self.x), int(self.y))
        self.repaint_if_changed()

    def do_fall(self):
        prev_feet = self.feet
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        self.vx *= 0.99
        self.x += self.vx
        self.y += self.vy
        if self.clamp_horizontal():
            self.vx = -self.vx * 0.5
        new_feet = self.feet

        self.fall_ticks += 1
        if self.vy > 0:
            cx = self.center_x
            target = None
            floor = self.floor_for(cx, prev_feet)
            if floor is not None and new_feet >= floor:
                target = floor          # ha cruzado el suelo en este fotograma
            for x1, x2, y in self.platforms:
                if x1 <= cx <= x2 and prev_feet <= y <= new_feet:
                    if target is None or y < target:
                        target = y
            if target is not None:
                self.land(target)
                return

        _l, _t, _r, bottom = self.virtual_bounds
        if self.fall_ticks > 240 or self.y > bottom + 300:
            self.rescue()

    def land(self, feet_y: float):
        self.y = feet_y - PET_BOTTOM * SCALE
        self.vx = self.vy = 0.0
        self.fall_ticks = 0
        self.state = "idle"
        self.activity = None
        self.state_timer = random.randint(30, 90)

    def rescue(self):
        self.refresh_world()
        cx = self.center_x
        area = min(self.monitors, key=lambda m: abs((m[0] + m[2]) / 2 - cx))
        self.x = float(max(area[0], min(cx, area[2] - 1))
                       - (PET_COL + SPRITE_W / 2) * SCALE)
        self.land(area[3])

    def do_walk(self):
        self.step(self.facing)
        self.state_timer -= 1
        if self.state == "walk" and self.state_timer <= 0:
            self.state = "idle"
            self.state_timer = random.randint(40, 140)

    def do_travel(self):
        if not self.travel_target:
            self.state = "idle"
            return
        left, _t, right, _b = self.travel_target
        if left <= self.center_x <= right:
            self.travel_target = None
            self.state = "idle"
            self.state_timer = random.randint(30, 80)
            return
        self.facing = 1 if (left + right) / 2 > self.center_x else -1
        self.step(self.facing, speed=WALK_SPEED * 1.6)

    def step(self, direction: int, speed: float = WALK_SPEED):
        """Avanza si hay suelo delante; si no, salta a otra ventana, o se cae."""
        previous_x = self.x
        self.x += direction * speed
        if self.clamp_horizontal():
            self.facing *= -1
            return

        cx = self.center_x
        if self.floor_for(cx, self.feet) is None and not self.platforms_under(cx):
            self.x = previous_x            # hueco entre monitores: media vuelta
            self.facing *= -1
            self.travel_target = None
            return

        if self.support_at(cx, self.feet) is None:
            if self.try_hop(direction):
                return
            self.state = "fall"            # se ha salido de un borde: cae
            self.vx = direction * 1.3
            self.vy = 0.0

    def hop_gap(self, direction: int):
        """Hueco hasta la ventana mas cercana alcanzable de un salto, o None."""
        cx, feet = self.center_x, self.feet
        mejor = None
        for x1, x2, y in self.platforms:
            subida = feet - y
            if subida > HOP_UP_MAX or -subida > HOP_DOWN_MAX:
                continue
            borde = x1 if direction > 0 else x2
            hueco = (borde - cx) * direction
            if 0 < hueco <= HOP_REACH and (mejor is None or hueco < mejor):
                mejor = hueco
        return mejor

    def try_hop(self, direction: int) -> bool:
        """Salta al borde de enfrente en vez de dejarse caer."""
        if random.random() > HOP_CHANCE:
            return False
        hueco = self.hop_gap(direction)
        if hueco is None:
            return False
        vuelo = 2 * abs(HOP_VY) / GRAVITY          # ticks en el aire
        self.vx = direction * min(max((hueco + 34.0) / vuelo, HOP_VX), 9.5)
        self.vy = HOP_VY
        self.state = "fall"
        self.hops += 1
        return True

    def do_edge(self):
        """Camina hasta el canto de su ventana y alli empieza la actividad."""
        config = ACTIVITIES.get(self.pending_activity)
        if config is None:
            self.state = "idle"
            self.pending_activity = self.edge_target = None
            return

        plataforma = self.platform_under()
        self.state_timer -= 1
        if plataforma is None or self.state_timer <= 0:
            self.begin_activity(self.pending_activity, config)
            return

        x1, x2, _y = plataforma
        derecha = self.edge_target >= (x1 + x2) / 2
        destino = (x2 - EDGE_MARGIN) if derecha else (x1 + EDGE_MARGIN)
        dx = destino - self.center_x
        if abs(dx) <= WALK_SPEED:
            self.facing = 1 if derecha else -1     # mira hacia el vacio
            self.begin_activity(self.pending_activity, config)
            return

        self.facing = 1 if dx > 0 else -1
        self.step(self.facing)
        if self.state != "edge":                   # se ha caido por el camino
            self.pending_activity = self.edge_target = None

    def do_act(self):
        config = ACTIVITIES.get(self.activity)
        if config and config["move"]:
            self.step(self.facing, speed=config["move"])
            if self.state != "act":        # se ha caido o saltado de un borde
                return

        if self.support_at(self.center_x, self.feet) is None:
            self.state = "fall"
            self.activity = None
            return

        self.state_timer -= 1
        if self.state_timer <= 0:
            if self.mood_enabled:
                self.mood.satisfy(self.activity)
            self.state = "idle"
            self.activity = None
            self.state_timer = random.randint(30, 90)

    def do_idle(self):
        if self.support_at(self.center_x, self.feet) is None:
            self.state = "fall"
            return

        if self.follow_mouse:
            cursor = QCursor.pos()
            dx = cursor.x() - self.center_x
            if 50 < abs(dx) < 400 and abs(cursor.y() - self.y) < 250:
                self.facing = 1 if dx > 0 else -1
                self.state = "walk"
                self.state_timer = random.randint(30, 70)
                return

        self.state_timer -= 1
        if self.state_timer > 0:
            return

        if self.auto_costume and random.random() < COSTUME_CHANCE:
            self.set_costume(random.choice([None] + list(COSTUMES)))

        roll = random.random()
        if roll < ACTIVITY_CHANCE:
            self.start_activity(self.choose_activity())
        elif roll < ACTIVITY_CHANCE + TRAVEL_CHANCE and len(self.monitors) > 1:
            others = [m for m in self.monitors if not (m[0] <= self.center_x < m[2])]
            if others:
                self.go_to_monitor(random.choice(others))
            else:
                self.state_timer = 60
        elif roll < 0.8:
            self.facing = random.choice((-1, 1))
            self.state = "walk"
            self.state_timer = random.randint(50, 160)
        elif roll < 0.9:
            self.state = "fall"            # salto
            self.vy = -11.0
            self.vx = self.facing * 1.8
        else:
            self.state_timer = random.randint(60, 180)

    def choose_activity(self) -> str:
        """Primero la ventana que tengas delante, luego el humor, luego el azar."""
        if self.context_enabled and random.random() < CONTEXT_CHANCE:
            sugerida = context.activity_for(self.backend.foreground_title())
            if sugerida in ACTIVITIES:
                return sugerida
        if self.mood_enabled:
            return self.mood.pick(list(ACTIVITIES), datetime.datetime.now().hour)
        return random.choice(list(ACTIVITIES))

    # ---- ordenes ------------------------------------------------------------ #

    def start_activity(self, name: str):
        config = ACTIVITIES.get(name)
        if not config:
            return
        if config.get("edge") and self.state in ("idle", "walk", "act"):
            plataforma = self.platform_under()
            if plataforma is not None:
                x1, x2, _y = plataforma
                cx = self.center_x
                self.edge_target = x2 if abs(x2 - cx) <= abs(cx - x1) else x1
                self.pending_activity = name
                self.activity = None
                self.state = "edge"
                self.state_timer = 300      # si no llega, lo hace donde este
                self.vx = self.vy = 0.0
                return
        self.begin_activity(name, config)

    def begin_activity(self, name: str, config: dict):
        self.pending_activity = None
        self.edge_target = None
        self.activity = name
        self.state = "act"
        self.vx = self.vy = 0.0
        low, high = config.get("ticks", (320, 700))
        self.state_timer = random.randint(low, high)

    def set_costume(self, name):
        self.costume = name if name in COSTUMES else None
        self.settings.set("costume", self.costume)
        self.settings.save()
        self._frame_key = None
        self.update()

    def set_flag(self, clave: str, valor: bool):
        """Cambia una preferencia del menu y la deja guardada."""
        setattr(self, clave, bool(valor))
        self.settings.set(clave, bool(valor))
        self.settings.save()

    def go_to_monitor(self, area):
        self.travel_target = area
        self.activity = None
        self.pending_activity = self.edge_target = None
        self.state = "travel"

    def reset_position(self):
        self.refresh_world()
        area = self.monitors[0]
        self.x = float(area[2] - self.width() - 80)
        self.y = float(area[1] + 40)
        self.vx = self.vy = 0.0
        self.activity = None
        self.travel_target = None
        self.pending_activity = self.edge_target = None
        self.state = "fall"

    def save_settings(self):
        self.settings.update(costume=self.costume,
                             auto_costume=self.auto_costume,
                             follow_mouse=self.follow_mouse,
                             mood_enabled=self.mood_enabled,
                             context_enabled=self.context_enabled,
                             x=int(self.x), y=int(self.y))
        return self.settings.save()

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    # ---- raton -------------------------------------------------------------- #

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.state = "drag"
            self.activity = None
            self.travel_target = None
            self.pending_activity = self.edge_target = None
            self.vx = self.vy = 0.0
            self._drag_offset = event.position().toPoint()
            self._last_pos = event.globalPosition().toPoint()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self.state != "drag" or self._drag_offset is None:
            return
        pos = event.globalPosition().toPoint()
        self.vx = (pos.x() - self._last_pos.x()) * THROW_FACTOR
        self.vy = (pos.y() - self._last_pos.y()) * THROW_FACTOR
        self._last_pos = pos
        self.x = float(pos.x() - self._drag_offset.x())
        self.y = float(pos.y() - self._drag_offset.y())
        self.move(int(self.x), int(self.y))

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        self.setCursor(Qt.OpenHandCursor)
        self.state = "fall"
        if self.vx:
            self.facing = 1 if self.vx > 0 else -1
        self.refresh_world()

    def mouseDoubleClickEvent(self, _event):
        if self.state in ("idle", "walk", "act"):
            self.activity = None
            self.state = "fall"
            self.vy = -12.0
            self.vx = self.facing * 2.0

    def contextMenuEvent(self, event):
        from .menu import build_menu
        self.refresh_world()
        build_menu(self, self).exec(event.globalPos())

    # ---- diagnostico -------------------------------------------------------- #

    def report(self) -> str:
        cx = self.center_x
        return (
            f"escritorio={self.backend.name}\n"
            f"estado={self.state} actividad={self.activity} traje={self.costume}\n"
            f"pos=({self.x:.0f},{self.y:.0f}) pies={self.feet:.0f} "
            f"suelo={self.floor_for(cx, self.feet)}\n"
            f"ventanas={len(self.platforms)} saltos={self.hops}\n"
            f"humor: {self.mood.report()}\n"
            f"ajustes={self.settings.path}\n"
            f"monitores(Qt)={self.monitors}\n"
            f"factor_nativo_a_qt=({self.transform[2]:.4f}, {self.transform[3]:.4f})"
        )

    def show_report(self):
        self.refresh_world()
        QMessageBox.information(self, "Diagnostico", self.report())

    # ---- dibujo ------------------------------------------------------------- #

    def current_config(self):
        return ACTIVITIES.get(self.activity) if self.state == "act" else None

    def gaze(self):
        """Direccion de la mirada (gx, gy) ya en coordenadas del sprite."""
        cursor = QCursor.pos()
        dx = cursor.x() - self.center_x
        dy = cursor.y() - (self.y + (PET_ROW + 4) * SCALE)
        if abs(dx) > GAZE_RANGE or abs(dy) > GAZE_RANGE:
            gx, gy = self.facing, 0          # lejos: mira hacia donde anda
        else:
            gx = 0 if abs(dx) < 14 else (1 if dx > 0 else -1)
            gy = 0 if abs(dy) < 14 else (1 if dy > 0 else -1)
        return gx * self.facing, gy          # compensa el volteo del sprite

    def current_cells(self):
        """Lista de (columna, fila, caracter) ya colocados en el lienzo."""
        config = self.current_config()
        stepping = self.state in ("walk", "travel", "edge") or bool(
            config and config["move"])

        body_kind = config["body"] if config else "normal"
        blinking = body_kind == "blink" or (body_kind != "hold"
                                            and self.blink_timer < 0)
        if body_kind == "hold":
            body = BODY_HOLD
        elif blinking:
            body = BODY_BLINK
        else:
            body = BODY

        legs_kind = config["legs"] if config else None
        if legs_kind == "walk" or (legs_kind is None and stepping):
            legs = LEGS["walk_a"] if (self.ticks // 8) % 2 == 0 else LEGS["walk_b"]
        elif legs_kind == "dangle":
            legs = (LEGS["dangle_a"] if (self.ticks // 24) % 2 == 0
                    else LEGS["dangle_b"])
        elif legs_kind:
            legs = LEGS[legs_kind]
        elif self.state == "drag":
            legs = LEGS["drag"]
        elif self.state == "fall":
            legs = LEGS["air"]
        else:
            legs = LEGS["idle"]

        # Alzado del sprite. Las actividades que la suben a algo (el monopatin)
        # fijan el suyo y anulan el respingo del paso: si se sumaran, los
        # sombreros mas altos se saldrian por arriba del lienzo.
        lift = config.get("lift", 0) if config else 0
        bob = lift if lift else (1 if (stepping and (self.ticks // 8) % 2) else 0)

        cells = []
        for row, line in enumerate(list(body) + [legs]):
            for col, ch in enumerate(line):
                if ch != ".":
                    cells.append((PET_COL + col, PET_ROW + row - bob, ch))

        if not blinking:
            gx, gy = self.gaze()
            for indice, (ecol, erow) in enumerate(EYES):
                if gx > 0:
                    dx = 1
                elif gx < 0:
                    dx = 0
                else:
                    dx = 1 if indice == 0 else 0      # de frente: hacia dentro
                dy = 1 if gy > 0 else 0
                cells.append((PET_COL + ecol + dx, PET_ROW + erow + dy - bob,
                              EYE_PUPIL))

        if self.costume:
            costume = COSTUMES[self.costume]
            pieces = list(costume["parts"])
            if not (config and config["prop"]):
                # si ya sujeta el objeto de una actividad, guarda el accesorio
                pieces += costume.get("accessory", [])
            for rows, dcol, drow in pieces:
                for row, line in enumerate(rows):
                    for col, ch in enumerate(line):
                        if ch == ".":
                            continue
                        cx = PET_COL + dcol + col
                        cy = PET_ROW + drow + row - bob
                        if 0 <= cx < CANVAS_W and 0 <= cy < CANVAS_H:
                            cells.append((cx, cy, ch))

        if config and config["prop"]:
            frames = PROPS[config["prop"]]
            rows, col0, row0 = frames[(self.ticks // config["speed"]) % len(frames)]
            for row, line in enumerate(rows):
                for col, ch in enumerate(line):
                    if ch != ".":
                        cells.append((col0 + col, row0 + row, ch))

        if config and config["overlay"]:
            if (self.ticks // (config["speed"] * 2)) % 2 == 0:
                rows, col0, row0 = OVERLAYS[config["overlay"]]
                for row, line in enumerate(rows):
                    for col, ch in enumerate(line):
                        if ch != ".":
                            cells.append((col0 + col, row0 + row, ch))
        return cells

    def mirrored(self, cells):
        if self.facing > 0:
            return cells
        return [(CANVAS_W - 1 - col, row, ch) for col, row, ch in cells]

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        for col, row, ch in self.mirrored(self.current_cells()):
            painter.fillRect(col * SCALE, row * SCALE, SCALE, SCALE, COLORS[ch])
        painter.end()

    def frame_signature(self):
        """Todo lo que determina que pixeles se pintan este tick."""
        config = self.current_config()
        prop_index = 0
        if config and config["prop"]:
            prop_index = (self.ticks // config["speed"]) % len(PROPS[config["prop"]])
        overlay_on = bool(config and config["overlay"]
                          and (self.ticks // (config["speed"] * 2)) % 2 == 0)
        return (self.state, self.activity, self.costume, self.facing,
                (self.ticks // 8) % 2, (self.ticks // 24) % 2,
                prop_index, overlay_on, self.blink_timer < 0, self.gaze())

    def repaint_if_changed(self):
        """Repinta y recalcula la mascara solo cuando el fotograma cambia."""
        clave = self.frame_signature()
        if clave == self._frame_key:
            return False
        self._frame_key = clave
        region = QRegion()
        for col, row, _ch in self.mirrored(self.current_cells()):
            region = region.united(
                QRegion(QRect(col * SCALE, row * SCALE, SCALE, SCALE)))
        self.setMask(region)
        self.update()
        return True
