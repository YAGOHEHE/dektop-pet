# Receta de PyInstaller. Genera un .exe que no necesita Python instalado.
#
#     pip install pyinstaller
#     pyinstaller pet.spec
#
# El resultado queda en dist/MascotaEscritorio.exe. Con onefile tarda un par de
# segundos en arrancar porque se descomprime en una carpeta temporal; si te
# molesta, pon onefile=False mas abajo y reparte la carpeta entera.

onefile = True

a = Analysis(
    ["run_pet.pyw"],
    pathex=["."],
    binaries=[],
    datas=[],
    # pywin32 se importa dentro de una funcion, asi que hay que declararlo
    hiddenimports=["win32gui", "win32api", "win32con"],
    hookspath=[],
    runtime_hooks=[],
    # fuera media pesada de Qt que la mascota no usa
    excludes=[
        "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
        "PySide6.QtQuick", "PySide6.QtQml", "PySide6.Qt3DCore",
        "PySide6.QtMultimedia", "PySide6.QtCharts", "PySide6.QtSql",
        "PySide6.QtNetwork", "PySide6.QtPdf", "PySide6.QtDesigner",
        "tkinter", "unittest", "pydoc", "PIL",
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

if onefile:
    exe = EXE(
        pyz, a.scripts, a.binaries, a.datas, [],
        name="MascotaEscritorio",
        debug=False,
        strip=False,
        upx=True,
        runtime_tmpdir=None,
        console=False,          # sin ventana negra detras
        icon=None,              # pon aqui la ruta de un .ico si quieres
    )
else:
    exe = EXE(
        pyz, a.scripts, [],
        exclude_binaries=True,
        name="MascotaEscritorio",
        debug=False,
        strip=False,
        upx=True,
        console=False,
        icon=None,
    )
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True,
                   name="MascotaEscritorio")
