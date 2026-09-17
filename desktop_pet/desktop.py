"""Capa de escritorio: lo unico que sabe de Windows.

El motor habla solo con un DesktopBackend, asi que portarlo a otro sistema es
escribir otra subclase. StubBackend, ademas, permite ejecutar y probar la
aplicacion entera sin Windows, que es como se valida el motor.
"""

from __future__ import annotations


class DesktopBackend:
    """Contrato minimo que necesita la mascota para vivir en un escritorio."""

    name = "abstracto"
    available = False

    def prepare(self) -> None:
        """Ajustes previos a crear QApplication (conciencia de DPI, etc)."""

    def window_platforms(self, skip_handle: int) -> list:
        """Borde superior de cada ventana visible: [(x1, x2, y)] nativo."""
        return []

    def transform(self) -> tuple:
        """(qx, qy, fx, fy, wx, wy) para pasar de pixeles nativos a Qt."""
        return (0.0, 0.0, 1.0, 1.0, 0.0, 0.0)

    def foreground_title(self) -> str:
        """Titulo de la ventana en primer plano, en minusculas."""
        return ""


class StubBackend(DesktopBackend):
    """Escritorio de mentira: ni ventanas ni Win32. Sirve para pruebas."""

    name = "stub"
    available = True

    def __init__(self, platforms=None, title=""):
        self._platforms = list(platforms or [])
        self._title = title

    def window_platforms(self, skip_handle: int) -> list:
        return list(self._platforms)

    def foreground_title(self) -> str:
        return self._title


class WindowsBackend(DesktopBackend):
    """Ventanas como plataformas y monitores como suelo, via Win32."""

    name = "windows"
    available = True

    DWMWA_CLOAKED = 14
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN = 76, 77
    SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN = 78, 79

    def __init__(self):
        import ctypes
        from ctypes import wintypes
        import win32api
        import win32con
        import win32gui

        self._ctypes = ctypes
        self._wintypes = wintypes
        self._api = win32api
        self._con = win32con
        self._gui = win32gui
        self._dwmapi = ctypes.WinDLL("dwmapi")

    def prepare(self) -> None:
        """Sin esto Windows falsea las coordenadas con escalado por monitor."""
        ctypes = self._ctypes
        try:
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
            return
        except Exception:
            pass
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()

    def _is_cloaked(self, hwnd: int) -> bool:
        value = self._ctypes.c_int(0)
        try:
            self._dwmapi.DwmGetWindowAttribute(
                self._wintypes.HWND(hwnd), self._ctypes.c_uint(self.DWMWA_CLOAKED),
                self._ctypes.byref(value), self._ctypes.sizeof(value))
        except OSError:
            return False
        return value.value != 0

    def _visible_rect(self, hwnd: int):
        rect = self._wintypes.RECT()
        ok = self._dwmapi.DwmGetWindowAttribute(
            self._wintypes.HWND(hwnd),
            self._ctypes.c_uint(self.DWMWA_EXTENDED_FRAME_BOUNDS),
            self._ctypes.byref(rect), self._ctypes.sizeof(rect))
        if ok == 0:
            return rect.left, rect.top, rect.right, rect.bottom
        return self._gui.GetWindowRect(hwnd)

    def window_platforms(self, skip_handle: int) -> list:
        found = []
        gui, con = self._gui, self._con

        def callback(hwnd, _):
            if hwnd == skip_handle:
                return True
            if not gui.IsWindowVisible(hwnd) or gui.IsIconic(hwnd):
                return True
            if not gui.GetWindowText(hwnd):
                return True
            if gui.GetWindowLong(hwnd, con.GWL_EXSTYLE) & con.WS_EX_TOOLWINDOW:
                return True
            if self._is_cloaked(hwnd):
                return True
            left, top, right, bottom = self._visible_rect(hwnd)
            if right - left < 120 or bottom - top < 60:
                return True
            found.append((left, right, top))
            return True

        try:
            gui.EnumWindows(callback, None)
        except Exception:
            pass
        return found

    def transform(self) -> tuple:
        """Se calibra sola comparando el escritorio virtual de Windows y el de Qt."""
        from PySide6.QtWidgets import QApplication

        api = self._api
        wx = api.GetSystemMetrics(self.SM_XVIRTUALSCREEN)
        wy = api.GetSystemMetrics(self.SM_YVIRTUALSCREEN)
        ww = api.GetSystemMetrics(self.SM_CXVIRTUALSCREEN) or 1
        wh = api.GetSystemMetrics(self.SM_CYVIRTUALSCREEN) or 1
        rects = [s.geometry() for s in QApplication.screens()]
        if not rects:
            return (0.0, 0.0, 1.0, 1.0, float(wx), float(wy))
        qx = min(r.left() for r in rects)
        qy = min(r.top() for r in rects)
        qw = max(r.right() + 1 for r in rects) - qx
        qh = max(r.bottom() + 1 for r in rects) - qy
        return qx, qy, qw / ww, qh / wh, wx, wy

    def foreground_title(self) -> str:
        try:
            return self._gui.GetWindowText(self._gui.GetForegroundWindow()).lower()
        except Exception:
            return ""


def get_backend() -> DesktopBackend:
    """WindowsBackend si se puede; si no, el de mentira (la app sigue viva)."""
    try:
        return WindowsBackend()
    except Exception:
        return StubBackend()


def monitor_work_areas() -> list:
    """Area util de cada pantalla EN COORDENADAS DE QT.

    Se usan las de Qt y no las nativas a proposito: son las mismas que acepta
    move(), asi que el suelo esta siempre donde Qt puede dibujar, tenga el
    sistema el escalado que tenga.
    """
    from PySide6.QtWidgets import QApplication

    areas = []
    for screen in QApplication.screens():
        geo = screen.availableGeometry()
        areas.append((geo.left(), geo.top(), geo.right() + 1, geo.bottom() + 1))
    return areas or [(0, 0, 1280, 720)]
