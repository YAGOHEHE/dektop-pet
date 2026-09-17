"""
Mascota de escritorio (desktop pet) para Windows. Version 4.

Novedades respecto a la v3:
    - Actividades de canto: camina hasta el borde de la ventana sobre la que
      esta, se sienta con las piernas colgando y desde ahi pesca, con sedal,
      flotador y algun pez que pica. El lienzo es mas alto por debajo de los
      pies para que quepa el sedal.

Novedades de la v3 respecto a la v2:
    - Trajes tradicionales (Espania, Mexico, Japon, China, Corea, India,
      Escocia, Rusia, Peru, Marruecos, Baviera y Egipto). Se eligen desde el
      menu de clic derecho y la mascota se los pone mientras hace cualquier
      actividad; si quieres, se cambia de traje ella sola.

Novedades de la v2 respecto a la v1:
    - Actividades: come palomitas, bebe refresco, toca el ukelele, lee un libro
      y programa en un portatil. Cada actividad es un "prop" pixelado animado.
    - Multimonitor: camina y cae por todas las pantallas, y de vez en cuando
      decide viajar a otro monitor. Menu de clic derecho para enviarla a uno.
    - Mascara de raton: solo los pixeles dibujados capturan clics, el resto de
      la ventana deja pasar el raton a lo que haya detras.

Requisitos:
    pip install PySide6 pywin32
Ejecutar:
    pythonw desktop_pet.py
"""

import ctypes
import os
import random
import sys
from ctypes import wintypes

# Debe estar ANTES de crear QApplication. Con el escalado de Qt desactivado,
# las coordenadas de Qt son pixeles fisicos y coinciden con las de Win32, que
# es lo que permite que el multimonitor no se desalinee.
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "0")

from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QCursor, QPainter, QRegion
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QWidget

import win32api
import win32con
import win32gui

# --------------------------------------------------------------------------- #
# Paleta y arte pixel. Todo se define como filas de texto: un caracter = un
# pixel gordo. Cambia estas matrices para rediseniar la mascota o los objetos.
# --------------------------------------------------------------------------- #

PALETTE = {
    "B": QColor("#C2603E"),   # cuerpo
    "S": QColor("#9C4A2F"),   # sombra del cuerpo
    "E": QColor("#191919"),   # ojos y tinta
    "R": QColor("#D2342B"),   # rojo (cubo, lata)
    "W": QColor("#F5EFE6"),   # blanco (papel, franja)
    "P": QColor("#F3D57A"),   # palomita
    "T": QColor("#B87C4C"),   # madera clara
    "N": QColor("#6E4522"),   # madera oscura
    "C": QColor("#2D4A7D"),   # tapa del libro
    "D": QColor("#17222B"),   # pantalla
    "L": QColor("#7ED07A"),   # codigo en pantalla
    "K": QColor("#9AA3AB"),   # teclado / metal
    "M": QColor("#FFFFFF"),   # nota musical, burbujas
    # colores extra usados por los trajes tradicionales
    "G": QColor("#2E7D4F"),   # verde
    "A": QColor("#2F5FA8"),   # azul indigo
    "Y": QColor("#E8B93A"),   # dorado / amarillo
    "O": QColor("#E07B39"),   # naranja azafran
    "I": QColor("#E2739B"),   # rosa
    "Q": QColor("#7E1B1B"),   # granate
    "J": QColor("#20242B"),   # negro tela
    "Z": QColor("#414A63"),   # azul pizarra (telas oscuras visibles)
}

# Lienzo: la ventana es mas ancha que la mascota para que quepan los objetos, y
# mas alta por debajo de los pies para que quepa el sedal de la caña de pescar.
CANVAS_W, CANVAS_H = 21, 18
PET_COL, PET_ROW = 5, 3          # esquina de la mascota dentro del lienzo
SPRITE_W, SPRITE_H = 11, 9
PET_BOTTOM = PET_ROW + SPRITE_H  # fila del lienzo donde estan los pies

BODY = [
    "..B.....B..",
    "..B.....B..",
    ".BBBBBBBBB.",
    ".BEEBBBEEB.",
    ".BEEBBBEEB.",
    "BBBBBBBBBBB",
    "BBBBBBBBBBB",
    "SSSSSSSSSSS",
]

BODY_BLINK = [
    "..B.....B..",
    "..B.....B..",
    ".BBBBBBBBB.",
    ".BBBBBBBBB.",
    ".BEEBBBEEB.",
    "BBBBBBBBBBB",
    "BBBBBBBBBBB",
    "SSSSSSSSSSS",
]

BODY_HOLD = [           # brazos levantados para sujetar algo
    "..B.....B..",
    "..B.....B..",
    ".BBBBBBBBB.",
    ".BEEBBBEEB.",
    "BBEEBBBEEBB",
    "BBBBBBBBBBB",
    "BBBBBBBBBBB",
    "SSSSSSSSSSS",
]

LEGS = {
    "idle": ".BB.BBB.BB.",
    "walk_a": "BB..BBB.BB.",
    "walk_b": ".BB.BBB..BB",
    "air": "B.B.....B.B",
    "drag": "B.B..B..B.B",
    "sit": "BBB.....BBB",
    "dangle_a": ".....BB.BB.",   # sentada en el canto, piernas hacia fuera
    "dangle_b": "....BB.BB..",
    "none": "...........",
}

# --------------------------------------------------------------------------- #
# Props: (filas, columna, fila) en coordenadas del lienzo.
# --------------------------------------------------------------------------- #

PROPS = {
    "popcorn": [
        (["PWPWP", "RWRWR", "RWRWR", ".RRR."], 16, 8),
        ([".P...", "PWPWP", "RWRWR", "RWRWR", ".RRR."], 16, 7),
    ],
    "cola": [
        (["RRR", "WWW", "RRR", "RRR"], 17, 8),
        (["RRR", "WWW", "RRR", "RRR"], 17, 7),
    ],
    "ukulele": [
        (["....N", "...N.", "..N..", ".TTT.", "TTTTT", ".TTT."], 15, 6),
        (["....N", "...N.", "..N..", ".TMT.", "TTTTT", ".TTT."], 15, 6),
    ],
    "book": [
        (["CWWWWWC", "CWEEEWC", "CWWWWWC", "CCCCCCC"], 14, 7),
        (["CWWWWWC", "CWWWWWC", "CWEEEWC", "CCCCCCC"], 14, 7),
    ],
    "laptop": [
        ([".DDDDD.", ".DLLLD.", ".DDDDD.", "KKKKKKK"], 14, 8),
        ([".DDDDD.", ".DLDLD.", ".DDDDD.", "KKKKKKK"], 14, 8),
    ],
    # el balon rebota delante de la mascota mientras regatea
    "ball": [
        ([".W.", "WEW", ".W."], 17, 9),
        ([".W.", "WEW", ".W."], 18, 7),
        ([".W.", "WEW", ".W."], 18, 5),
        ([".W.", "WEW", ".W."], 17, 7),
    ],
    # camioneta angular: solo asoman la cabeza y los ojos por encima
    "truck": [
        (["...KKKKKKKKKK....",
          "KKKKKKKKKKKKKKKKK",
          "KDDKKKKKKKKKKDDKK",
          ".EEE.......EEE..."], 2, 8),
        (["...KKKKKKKKKK....",
          "KKKKKKKKKKKKKKKKK",
          "KDDKKKKKKKKKKDDKK",
          ".E.E.......E.E..."], 2, 8),
    ],
    "coffee": [
        (["..M.", "WWWW", "WWWW", ".WW."], 16, 8),
        ([".M..", "WWWW", "WWWW", ".WW."], 16, 8),
    ],
    # barra de pesas por encima de la cabeza, sube y baja
    "dumbbell": [
        (["K...K", "KKKKK", "K...K"], 8, 1),
        (["K...K", "KKKKK", "K...K"], 8, 0),
    ],
    # cols 14-18 del lienzo: caña en diagonal, sedal recto y flotador al final
    "fishing": [
        (["....N", "...NK", "..N.K", ".N..K", "N...K",
          "....K", "....K", "....K", "....K", "....K", "....K",
          "....R"], 14, 4),
        (["....N", "...NK", "..N.K", ".N..K", "N...K",
          "....K", "....K", "....K", "....K", "....K",
          "....R"], 14, 4),
        (["....N", "...NK", "..N.K", ".N..K", "N...K",
          "....K", "....K", "....K",
          "...OO", "..OOO"], 14, 4),
        (["....N", "...NK", "..N.K", ".N..K", "N...K",
          "....K",
          "...OO", "..OOO"], 14, 4),
    ],
    "pizza": [
        (["..R..", ".RRR.", "RRRRR", "PPPPP"], 16, 8),
        (["..R..", ".RR..", "RRR..", "PPP.."], 16, 8),
    ],
}

# Adorno opcional sobre la cabeza (nota musical, burbujas...)
OVERLAYS = {
    "note": ([".MM", ".M.", "MM."], 16, 1),
    "bubble": ([".M.", "M.M", ".M."], 16, 1),
    "zzz": (["MMM", "..M", "MMM"], 16, 1),
}

# --------------------------------------------------------------------------- #
# Trajes tradicionales. Se dibujan ENCIMA del cuerpo, asi que tapan los pixeles
# que pisan. Cada pieza es (filas, dcol, drow) en coordenadas del SPRITE, no del
# lienzo: (0, 0) es la esquina superior izquierda de la mascota, drow negativo
# queda por encima de la cabeza (minimo -2, que es lo que cabe en el lienzo).
#
# "parts"     : la ropa, siempre visible.
# "accessory" : el objeto que lleva al lado (maracas, abanico, gaita...). Se
#               oculta mientras la actividad en curso ya le ocupa las manos con
#               su propio prop, para que no se solapen.
#
# Referencia de filas del sprite:
#   0-1 orejas | 2 alto de la cabeza | 3-4 ojos | 5-6 torso | 7 bajo del torso
# El torso mide 11 pixeles de ancho: esas filas deben tener 11 caracteres.
# A los lados sobran 5 columnas por banda (dcol de -5 a 15) para los accesorios.
# --------------------------------------------------------------------------- #

COSTUMES = {
    "espana": {
        "label": "Espania - traje de flamenca",
        "parts": [
            ([".R.",
              "RYR",
              ".R."], 7, 0),                      # flor en el pelo
            (["RRWRRRWRRWR",
              "WRRRWRRRWRR",
              "RRWRRRWRRRW"], 0, 5),              # volantes de lunares
        ],
        "accessory": [
            (["R.R",
              "RRR",
              "RRR",
              ".N."], 11, 3),                     # abanico
        ],
    },
    "mexico": {
        "label": "Mexico - charro",
        "parts": [
            ([".....YYYYYYY.....",
              "....YYYYYYYYY....",
              "...YRRRRRRRRRY...",
              "YYYYYYYYYYYYYYYYY",
              "NN.............NN"], -3, -2),      # sombrero de ala ancha
            (["GGGGGGGGGGG",
              "WWWWWWWWWWW",
              "RRRRRRRRRRR"], 0, 5),              # sarape
        ],
        "accessory": [
            ([".Y.",
              "YRY",
              "YYY",
              ".N."], 11, 3),                     # maraca derecha
            ([".Y.",
              "YRY",
              "YYY",
              ".N."], -3, 3),                     # maraca izquierda
        ],
    },
    "japon": {
        "label": "Japon - kimono",
        "parts": [
            ([".I.",
              "IYI",
              ".I."], 0, 0),                      # flor de sakura
            (["AWWAAAAAWWA",
              "AAAWAAAWAAA",
              "RRRRRRRRRRR"], 0, 5),              # kimono y obi
        ],
        "accessory": [
            (["..N..",
              ".RRR.",
              "RRRRR",
              "..N..",
              "..N.."], 11, 2),                   # sombrilla wagasa
        ],
    },
    "china": {
        "label": "China - tangzhuang",
        "parts": [
            (["....YYY....",
              "..QQQQQQQ..",
              ".QQQQQQQQQ."], 0, -1),             # gorro con remate
            (["RRRRYYYRRRR",
              "RRRRRYRRRRR",
              "QQQQQYQQQQQ"], 0, 5),              # chaqueta de botones
        ],
        "accessory": [
            ([".Y.",
              "RRR",
              "RRR",
              ".Y."], 11, 3),                     # farolillo
        ],
    },
    "corea": {
        "label": "Corea - hanbok",
        "parts": [
            (["YYYYWWWYYYY",
              "IIIIIRIIIII",
              "IIIIIIIIIII"], 0, 5),              # jeogori y chima
        ],
        "accessory": [
            (["WWWW",
              ".TT.",
              ".TT.",
              "WWWW"], 11, 3),                    # tambor janggu
        ],
    },
    "india": {
        "label": "India - sari",
        "parts": [
            (["R"], 5, 2),                        # bindi
            (["OOOOOOYOOOO",
              "OOOOOOYOOOO",
              "YYYYYYYYYYY"], 0, 5),              # sari con cenefa dorada
        ],
        "accessory": [
            ([".O.",
              ".Y.",
              "NNN",
              ".N."], 11, 4),                     # lampara diya
        ],
    },
    "escocia": {
        "label": "Escocia - kilt",
        "parts": [
            ([".....R.....",
              "..AAAAAAA..",
              ".AAAAAAAAA."], 0, -1),             # boina con pompon
            (["WWWWWWWWWWW",
              "RGRGRGRGRGR",
              "GRGRGRGRGRG"], 0, 5),              # camisa y tartan
        ],
        "accessory": [
            (["N.N.",
              "N.N.",
              "GRGR",
              "RGRG",
              ".GG."], 11, 2),                    # gaita
        ],
    },
    "rusia": {
        "label": "Rusia - ushanka",
        "parts": [
            (["...NNNNN...",
              "..TTTTTTT..",
              ".TTTTTTTTT.",
              "T.........T"], 0, -1),             # gorro con orejeras
            (["RRWRRRRRWRR",
              "RRRRRRRRRRR",
              "NNNNNNNNNNN"], 0, 5),              # rubashka y cinturon
        ],
        "accessory": [
            ([".R.",
              "RWR",
              "RYR",
              "RRR"], 11, 3),                     # matrioska
        ],
    },
    "peru": {
        "label": "Peru - poncho andino",
        "parts": [
            (["...RRRRR...",
              "..RYRYRYR..",
              ".RRRRRRRRR.",
              "Y.........Y"], 0, -1),             # chullo
            (["QQQQQQQQQQQ",
              "QYQYQYQYQYQ",
              "YYYYYYYYYYY"], 0, 5),              # poncho
        ],
        "accessory": [
            (["T..",
              "TT.",
              "TTT",
              "NNN"], 11, 4),                     # zampoña
        ],
    },
    "bolivia": {
        "label": "Bolivia - cholita paceña",
        "parts": [
            (["...NNNNN...",
              "..NRRRRRN..",
              ".NNNNNNNNN."], 0, -2),             # bombin de cholita
            (["GGGGGGGGGGG",
              "RYRYRYRYRYR",
              "IIIIIIIIIII"], 0, 5),              # manta, aguayo y pollera
        ],
        "accessory": [
            (["..N.",
              "..N.",
              ".TTT",
              "TTTT",
              ".TT."], 11, 2),                    # charango
        ],
    },
    "marruecos": {
        "label": "Marruecos - chilaba y fez",
        "parts": [
            ([".....J.....",
              "...RRRRR...",
              "..RRRRRRR..",
              "..RRRRRRR.."], 0, -2),             # fez con borla
            (["WWWWGGGWWWW",
              "WWWWWGWWWWW",
              "WWWWWWWWWWW"], 0, 5),              # chilaba
        ],
        "accessory": [
            ([".K..",
              "KKK.",
              "KKKK",
              ".KK."], 11, 4),                    # tetera
        ],
    },
    "baviera": {
        "label": "Baviera - lederhosen",
        "parts": [
            (["........W..",
              "...GGGGG...",
              "..GGGGGGG..",
              ".GGGGGGGGG."], 0, -2),             # sombrero tirol con pluma
            (["WWNWWWWWNWW",
              "WWNWWWWWNWW",
              "NNNNNNNNNNN"], 0, 5),              # camisa y tirantes
        ],
        "accessory": [
            (["WWW.",
              "YYYK",
              "YYYK",
              "YYY."], 11, 4),                    # jarra de cerveza
        ],
    },
    "egipto": {
        "label": "Egipto - nemes",
        "parts": [
            (["..YYYYYYY..",
              ".AYAYAYAYA.",
              "AYAYAYAYAYA",
              "A.........A"], 0, -1),             # tocado a rayas
            (["WYYYYYYYYYW",
              "WWWWWWWWWWW",
              "WWWWWWWWWWW"], 0, 5),              # tunica y collar
        ],
        "accessory": [
            ([".YY",
              ".Y.",
              ".Y.",
              ".Y.",
              ".Y."], 11, 3),                     # cayado
        ],
    },
    # ---- personajes de anime y dibujos (arquetipos originales) ------------- #
    "ninja": {
        "label": "Ninja shinobi",
        "parts": [
            ([".ZZZKKKZZZ."], 0, 2),              # banda con placa metalica
            (["ZZZZZZZZZZZ",
              "ZZZZZZZZZZZ",
              "RRRRRRRRRRR"], 0, 5),              # traje y faja roja
        ],
        "accessory": [
            (["..K..",
              ".KKK.",
              "KK.KK",
              ".KKK.",
              "..K.."], 11, 3),                   # shuriken
        ],
    },
    "samurai": {
        "label": "Samurai",
        "parts": [
            ([".Y.......Y.",
              ".YZZZZZZZY.",
              ".ZZZYYYZZZ.",
              "ZZZZZZZZZZZ"], 0, -2),             # kabuto con cuernos
            (["QQQQQQQQQQQ",
              "QQYQQQQQYQQ",
              "ZZZZZZZZZZZ"], 0, 5),              # armadura
        ],
        "accessory": [
            ([".K.",
              ".K.",
              ".K.",
              "YKY",
              ".N.",
              ".N."], 11, 2),                     # katana
        ],
    },
    "magica": {
        "label": "Chica magica",
        "parts": [
            (["..Y..",
              ".YYY.",
              "..Y.."], 3, -2),                   # estrella flotante
            ([".YYYYYYYYY."], 0, 2),              # tiara
            (["IIIIIRIIIII",
              "IIIIRRRIIII",
              "WWWWWWWWWWW"], 0, 5),              # vestido con lazo
        ],
        "accessory": [
            ([".Y.",
              "YYY",
              ".Y.",
              ".I.",
              ".I."], 11, 3),                     # varita
        ],
    },
    "mecha": {
        "label": "Piloto de mecha",
        "parts": [
            ([".....R.....",
              "..KKKKKKK..",
              ".KKKKKKKKK.",
              "KKKKKKKKKKK",
              ".KAAAAAAAK."], 0, -2),             # casco con visor
            (["WWWWWWWWWWW",
              "AAAAALAAAAA",
              "AAAAAAAAAAA"], 0, 5),              # traje de vuelo
        ],
        "accessory": [
            ([".R.",
              "KLK",
              "KKK",
              "K.K"], 11, 4),                     # dron de apoyo
        ],
    },
    "colegiala": {
        "label": "Uniforme escolar",
        "parts": [
            (["Y"], 3, 2),                        # pasador de pelo
            (["AAWWWWWWWAA",
              "AAAAARAAAAA",
              "AAAAAAAAAAA"], 0, 5),              # cuello marinero y falda
        ],
        "accessory": [
            (["RRRR",
              "RYYR",
              "RRRR",
              ".RR."], 11, 4),                    # mochila
        ],
    },
    "kaiju": {
        "label": "Kaiju",
        "parts": [
            (["..G.G.G.G..",
              ".GGGGGGGGG.",
              "GGGGGGGGGGG"], 0, -1),             # cresta de puas
            (["GGGGGGGGGGG",
              "GLGLGLGLGLG",
              "GGGGGGGGGGG"], 0, 5),              # escamas
        ],
        "accessory": [
            (["KKK",
              "KYK",
              "KKK",
              "KYK"], 11, 4),                     # edificio
        ],
    },
    "heroe": {
        "label": "Superheroe",
        "parts": [
            ([".AAAAAAAAA.",
              ".A.......A."], 0, 2),              # antifaz
            (["RAAAAYAAAAR",
              "RAAAYYYAAAR",
              "RAAAAAAAAAR"], 0, 5),              # traje y capa
        ],
        "accessory": [
            (["..Y",
              ".YY",
              ".Y.",
              "YY.",
              ".Y."], 11, 3),                     # rayo
        ],
    },
    "robot": {
        "label": "Robot de hojalata",
        "parts": [
            ([".....R.....",
              ".....K.....",
              "..KKKKKKK..",
              "KKKKKKKKKKK",
              ".KKKKKKKKK."], 0, -2),             # antena y casco
            (["KKKKKKKKKKK",
              "KKKKLRLKKKK",
              "KKKKKKKKKKK"], 0, 5),              # chasis con botones
        ],
        "accessory": [
            (["K.K",
              "KKK",
              ".K.",
              ".K."], 11, 4),                     # llave inglesa
        ],
    },
    "mago": {
        "label": "Mago",
        "parts": [
            ([".....A.....",
              "....AAA....",
              "...AAYAA...",
              "AAAAAAAAAAA"], 0, -2),             # sombrero de punta
            (["AAAAAAAAAAA",
              "AAYAAAAAYAA",
              "AAAAAYAAAAA"], 0, 5),              # tunica de estrellas
        ],
        "accessory": [
            ([".L.",
              "LLL",
              ".L.",
              ".N.",
              ".N.",
              ".N."], 11, 2),                     # baston con orbe
        ],
    },
    "pirata": {
        "label": "Pirata",
        "parts": [
            (["RRRRWRWRRRR",
              ".RRRRRRRRR."], 0, 1),              # paniuelo con calavera
            (["WWWWWWWWWWW",
              "AAAAAAAAAAA",
              "QQQQQQQQQQQ"], 0, 5),              # camisa a rayas y faja
        ],
        "accessory": [
            ([".GG",
              "GGY",
              ".RR",
              ".R."], 11, 4),                     # loro
        ],
    },
    "gi": {
        "label": "Guerrero de gi",
        "parts": [
            ([".RRRRRRRRR."], 0, 2),              # cinta de la frente
            (["WWZWWWWWZWW",
              "WWWZWWWZWWW",
              "ZZZZZZZZZZZ"], 0, 5),              # gi y cinturon negro
        ],
        "accessory": [
            ([".LL.",
              "LWWL",
              "LWWL",
              ".LL."], 11, 4),                    # esfera de energia
        ],
    },
    "espadachin": {
        "label": "Espadachin errante",
        "parts": [
            ([".....TTT.....",
              "...TTTTTTT...",
              ".TTTTTTTTTTT.",
              "TTTTTTTTTTTTT"], -1, -1),          # kasa de paja
            (["ZZZWZZZWZZZ",
              "ZZZZWZWZZZZ",
              "NNNNNNNNNNN"], 0, 5),              # kimono de viaje
        ],
        "accessory": [
            ([".Y.",
              ".N.",
              ".Z.",
              ".Z.",
              ".Z.",
              ".Z."], 11, 2),                     # espada envainada
        ],
    },
    "cazador": {
        "label": "Cazador de espiritus",
        "parts": [
            ([".WRWRWRWRW."], 0, 2),              # cinta de talismanes
            (["WWZZZZZZZWW",
              "ZZZZZZZZZZZ",
              "WWWWWWWWWWW"], 0, 5),              # haori y hakama
        ],
        "accessory": [
            (["WWW",
              "WRW",
              "WRW",
              "WRW",
              "WWW"], 11, 3),                     # ofuda
        ],
    },
    "espacial": {
        "label": "Piloto de caza espacial",
        "parts": [
            ([".....R.....",
              "..WWWWWWW..",
              ".WWWWWWWWW.",
              "WWWWWWWWWWW",
              ".WYYYYYYYW."], 0, -2),             # casco con visor dorado
            (["OOOOOWOOOOO",
              "OOWWWWWWWOO",
              "OOOOOOOOOOO"], 0, 5),              # mono de vuelo con arnes
        ],
        "accessory": [
            ([".W.",
              ".W.",
              "WWW",
              "WRW",
              "R.R"], 11, 3),                     # nave de apoyo
        ],
    },
    "idol": {
        "label": "Idol",
        "parts": [
            (["K.........K",
              ".KKKKKKKKK."], 0, 1),              # auriculares
            (["WWAAAAAAAWW",
              "AAAAAYAAAAA",
              "WWWWWWWWWWW"], 0, 5),              # vestido de escenario
        ],
        "accessory": [
            ([".K.",
              "KKK",
              ".N.",
              ".N.",
              ".N."], 11, 3),                     # microfono
        ],
    },
    "ramen": {
        "label": "Cocinero de ramen",
        "parts": [
            (["WWWWWWWWWWW",
              ".WWWWWWWWW."], 0, 1),              # paniuelo tenugui
            (["AAAAAAAAAAA",
              "WWWWWAWWWWW",
              "WWWWWWWWWWW"], 0, 5),              # happi y delantal
        ],
        "accessory": [
            (["..M..",
              "ORORO",
              "WWWWW",
              ".WWW."], 11, 4),                   # bol de ramen
        ],
    },
    "neko": {
        "label": "Chica gato",
        "parts": [
            (["..W.....W..",
              ".WIW...WIW.",
              "WWWWW.WWWWW",
              ".WWW...WWW."], 0, -2),             # orejas de gato
            (["RRRRRYRRRRR",
              "ZZZZZZZZZZZ",
              "WWWWWWWWWWW"], 0, 5),              # collar con cascabel
        ],
        "accessory": [
            ([".II.",
              "IWII",
              "IIWI",
              ".II."], 11, 4),                    # ovillo de lana
        ],
    },
    "onmyoji": {
        "label": "Onmyoji",
        "parts": [
            (["....ZZZ....",
              "...ZZZZZ...",
              "..ZZZZZZZ..",
              ".ZZZZZZZZZ."], 0, -2),             # gorro eboshi
            (["WWWWWWWWWWW",
              "WWRWWWWWRWW",
              "AAAAAAAAAAA"], 0, 5),              # kariginu y hakama
        ],
        "accessory": [
            (["W.W",
              "WRW",
              "WWW",
              ".N."], 11, 3),                     # abanico ritual
        ],
    },
    "skater": {
        "label": "Skater",
        "parts": [
            (["...ZZZZZ...",
              "..ZZZZZZZ..",
              "..ZZZZZZZ.."], 0, -1),             # gorra
            (["ZZZ"], -1, 1),                     # visera hacia atras
            (["OOOOOOOOOOO",
              "OOOOWOWOOOO",
              "ZZZZZZZZZZZ"], 0, 5),              # sudadera y vaqueros
        ],
        "accessory": [
            ([".TT.",
              ".TT.",
              "WTTW",
              ".TT.",
              "WTTW"], 11, 3),                    # monopatin
        ],
    },
}

# Los dos grupos en que se parte el menu de trajes. Toda clave de COSTUMES tiene
# que aparecer aqui una sola vez.
COSTUME_GROUPS = [
    ("Paises", ["espana", "mexico", "japon", "china", "corea", "india",
                "escocia", "rusia", "peru", "bolivia", "marruecos",
                "baviera", "egipto"]),
    ("Personajes", ["ninja", "samurai", "espadachin", "gi", "cazador",
                    "onmyoji", "magica", "neko", "idol", "colegiala",
                    "ramen", "mecha", "espacial", "kaiju", "heroe",
                    "robot", "mago", "pirata", "skater"]),
]

# label  : nombre en el menu
# prop   : objeto de PROPS, o None
# body   : "normal" o "hold" (brazos levantados)
# legs   : clave de LEGS, o "walk" para que alterne el paso
# speed  : ticks por fotograma del prop
# overlay: adorno sobre la cabeza, o None
# move   : pixeles por tick que avanza mientras la hace (0 = quieta)
# ticks  : duracion minima y maxima

ACTIVITIES = {
    "popcorn": dict(label="Comer palomitas", prop="popcorn", body="normal",
                    legs="idle", speed=14, overlay=None, move=0.0),
    "cola": dict(label="Beber un refresco", prop="cola", body="hold",
                 legs="idle", speed=22, overlay="bubble", move=0.0),
    "ukulele": dict(label="Tocar el ukelele", prop="ukulele", body="hold",
                    legs="idle", speed=10, overlay="note", move=0.0),
    "book": dict(label="Leer un libro", prop="book", body="hold",
                 legs="sit", speed=40, overlay=None, move=0.0),
    "laptop": dict(label="Programar", prop="laptop", body="normal",
                   legs="sit", speed=12, overlay=None, move=0.0),
    "futbol": dict(label="Jugar al futbol", prop="ball", body="normal",
                   legs="walk", speed=6, overlay=None, move=1.1,
                   ticks=(400, 900)),
    "cybertruck": dict(label="Conducir el cybertruck", prop="truck",
                       body="normal", legs="none", speed=6, overlay=None,
                       move=3.2, ticks=(500, 1200)),
    "cafe": dict(label="Tomar un cafe", prop="coffee", body="hold",
                 legs="idle", speed=22, overlay=None, move=0.0),
    "pesas": dict(label="Hacer pesas", prop="dumbbell", body="hold",
                  legs="idle", speed=18, overlay=None, move=0.0),
    "pizza": dict(label="Comer pizza", prop="pizza", body="hold",
                  legs="idle", speed=30, overlay=None, move=0.0),
    "pescar": dict(label="Pescar desde el borde", prop="fishing", body="hold",
                   legs="dangle", speed=30, overlay=None, move=0.0,
                   ticks=(900, 1800), edge=True),
    "colgar": dict(label="Sentarse en el borde", prop=None, body="normal",
                   legs="dangle", speed=20, overlay=None, move=0.0,
                   ticks=(500, 1200), edge=True),
    "bailar": dict(label="Bailar", prop=None, body="normal",
                   legs="walk", speed=10, overlay="note", move=0.0),
    "siesta": dict(label="Echarse una siesta", prop=None, body="blink",
                   legs="sit", speed=40, overlay="zzz", move=0.0,
                   ticks=(600, 1400)),
}

# --------------------------------------------------------------------------- #
# Parametros de simulacion
# --------------------------------------------------------------------------- #

SCALE = 7            # tamanio del pixel. Subelo en pantallas 4K.
GRAVITY = 0.9
MAX_FALL = 24.0
WALK_SPEED = 1.5
THROW_FACTOR = 0.45
TICK_MS = 16
SCAN_MS = 600
ACTIVITY_CHANCE = 0.45
TRAVEL_CHANCE = 0.12
EDGE_MARGIN = 6.0         # px que deja entre el centro y el canto
COSTUME_CHANCE = 0.07     # probabilidad de cambiarse de traje al quedarse quieta

# --------------------------------------------------------------------------- #
# Win32: ventanas como plataformas, monitores como suelo
# --------------------------------------------------------------------------- #

DWMWA_CLOAKED = 14
DWMWA_EXTENDED_FRAME_BOUNDS = 9
_dwmapi = ctypes.WinDLL("dwmapi")


def set_dpi_awareness():
    """Sin esto Windows falsea las coordenadas en monitores con escalado."""
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return
    except Exception:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()


def _is_cloaked(hwnd: int) -> bool:
    value = ctypes.c_int(0)
    try:
        _dwmapi.DwmGetWindowAttribute(
            wintypes.HWND(hwnd), ctypes.c_uint(DWMWA_CLOAKED),
            ctypes.byref(value), ctypes.sizeof(value))
    except OSError:
        return False
    return value.value != 0


def _visible_rect(hwnd: int):
    rect = wintypes.RECT()
    ok = _dwmapi.DwmGetWindowAttribute(
        wintypes.HWND(hwnd), ctypes.c_uint(DWMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(rect), ctypes.sizeof(rect))
    if ok == 0:
        return rect.left, rect.top, rect.right, rect.bottom
    return win32gui.GetWindowRect(hwnd)


def window_platforms(skip_hwnd: int):
    """Borde superior de cada ventana visible: [(x1, x2, y)]."""
    found = []

    def callback(hwnd, _):
        if hwnd == skip_hwnd:
            return True
        if not win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd):
            return True
        if not win32gui.GetWindowText(hwnd):
            return True
        if win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOOLWINDOW:
            return True
        if _is_cloaked(hwnd):
            return True
        left, top, right, bottom = _visible_rect(hwnd)
        if right - left < 120 or bottom - top < 60:
            return True
        found.append((left, right, top))
        return True

    try:
        win32gui.EnumWindows(callback, None)
    except Exception:
        pass
    return found


SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN = 76, 77
SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN = 78, 79


def monitor_work_areas():
    """Area util de cada pantalla, EN COORDENADAS DE QT.

    Se usan las de Qt y no las de Win32 a proposito: son las mismas que acepta
    move(), asi que el suelo esta siempre donde Qt puede dibujar, tenga el
    sistema el escalado que tenga.
    """
    areas = []
    for screen in QApplication.screens():
        geo = screen.availableGeometry()
        areas.append((geo.left(), geo.top(), geo.right() + 1, geo.bottom() + 1))
    return areas


def win32_to_qt_transform():
    """(qx, qy, fx, fy, wx, wy) para pasar pixeles de Win32 a coordenadas Qt.

    Se calibra solo comparando el escritorio virtual segun Windows con el de
    Qt, asi funciona tanto si el escalado de Qt esta activo como si no.
    """
    wx = win32api.GetSystemMetrics(SM_XVIRTUALSCREEN)
    wy = win32api.GetSystemMetrics(SM_YVIRTUALSCREEN)
    ww = win32api.GetSystemMetrics(SM_CXVIRTUALSCREEN) or 1
    wh = win32api.GetSystemMetrics(SM_CYVIRTUALSCREEN) or 1
    rects = [s.geometry() for s in QApplication.screens()]
    qx = min(r.left() for r in rects)
    qy = min(r.top() for r in rects)
    qw = max(r.right() + 1 for r in rects) - qx
    qh = max(r.bottom() + 1 for r in rects) - qy
    return qx, qy, qw / ww, qh / wh, wx, wy


# --------------------------------------------------------------------------- #


class Pet(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
            | Qt.Tool | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(CANVAS_W * SCALE, CANVAS_H * SCALE)
        self.setCursor(Qt.OpenHandCursor)

        self.hwnd = int(self.winId())
        self.state = "fall"    # idle | walk | act | edge | travel | fall | drag
        self.pending_activity = None     # actividad que hara al llegar al canto
        self.edge_target = None          # x del canto al que se dirige
        self.activity = None
        self.travel_target = None
        self.facing = 1
        self.vx = self.vy = 0.0
        self.ticks = 0
        self.fall_ticks = 0
        self.state_timer = 60
        self.blink_timer = random.randint(120, 300)
        self.follow_mouse = True
        self.costume = None              # clave de COSTUMES, o None
        self.auto_costume = True         # se cambia de traje por su cuenta
        self._mask_key = None
        self._drag_offset = None
        self._last_pos = None

        self.platforms = []
        self.monitors = []
        self.transform = (0, 0, 1.0, 1.0, 0, 0)
        self.refresh_world()

        area = self.monitors[0]
        self.x = float(area[2] - self.width() - 80)
        self.y = float(area[1] + 40)
        self.move(int(self.x), int(self.y))

        self.loop = QTimer(self, interval=TICK_MS, timeout=self.tick)
        self.loop.start()
        self.scanner = QTimer(self, interval=SCAN_MS, timeout=self.refresh_world)
        self.scanner.start()

    # ---- geometria ---------------------------------------------------------- #

    def refresh_world(self):
        self.monitors = monitor_work_areas()
        self.transform = win32_to_qt_transform()
        qx, qy, fx, fy, wx, wy = self.transform
        self.platforms = [
            (qx + (x1 - wx) * fx, qx + (x2 - wx) * fx, qy + (y - wy) * fy)
            for x1, x2, y in window_platforms(self.hwnd)
        ]

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
        """Suelos (borde inferior del area util) de los monitores que cubren cx."""
        return sorted(bottom for left, _t, right, bottom in self.monitors
                      if left <= cx < right)

    def floor_for(self, cx: float, feet: float):
        """Primer suelo a la altura de los pies o por debajo. None si no hay."""
        for bottom in self.monitor_floors(cx):
            if bottom >= feet - 6:
                return bottom
        return None

    def support_at(self, cx: float, feet: float, tolerance: float = 5.0):
        """Y de la superficie sobre la que se apoya, o None si esta en el aire."""
        floor = self.floor_for(cx, feet)
        if floor is not None and abs(feet - floor) <= tolerance:
            return floor
        for x1, x2, y in self.platforms:
            if x1 <= cx <= x2 and abs(feet - y) <= tolerance:
                return y
        return None

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

        if self.state == "drag":
            self.update_mask()
            self.update()
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
        self.update_mask()
        self.update()

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

        # Red de seguridad: si lleva demasiado tiempo cayendo, la deja en el
        # suelo del monitor mas cercano en lugar de perderla.
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
        """Coloca la mascota en el suelo del monitor mas cercano al centro."""
        self.refresh_world()
        cx = self.center_x
        area = min(self.monitors,
                   key=lambda m: abs((m[0] + m[2]) / 2 - cx))
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
        """Avanza si hay suelo delante; si no, se cae o da la vuelta."""
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
            self.state = "fall"            # se ha salido de un borde: cae
            self.vx = direction * 1.3
            self.vy = 0.0

    def platform_under(self, tolerance: float = 5.0):
        """Ventana sobre la que esta de pie: (x1, x2, y). None si es el suelo."""
        cx, feet = self.center_x, self.feet
        for x1, x2, y in self.platforms:
            if x1 <= cx <= x2 and abs(feet - y) <= tolerance:
                return (x1, x2, y)
        return None

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
            # sin canto a la vista, o lleva demasiado intentandolo
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

    def platforms_under(self, cx: float) -> bool:
        return any(x1 <= cx <= x2 and y >= self.feet - 5
                   for x1, x2, y in self.platforms)

    def do_act(self):
        config = ACTIVITIES.get(self.activity)
        if config and config["move"]:
            self.step(self.facing, speed=config["move"])
            if self.state != "act":        # se ha caido de un borde
                return

        if self.support_at(self.center_x, self.feet) is None:
            self.state = "fall"
            self.activity = None
            return

        self.state_timer -= 1
        if self.state_timer <= 0:
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
            self.start_activity(random.choice(list(ACTIVITIES)))
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
        """name = clave de COSTUMES, o None para quitarle el traje."""
        self.costume = name if name in COSTUMES else None
        self.update_mask()
        self.update()

    def go_to_monitor(self, area):
        self.travel_target = area
        self.activity = None
        self.pending_activity = self.edge_target = None
        self.state = "travel"

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

    def contextMenuEvent(self, event):
        self.refresh_world()
        menu = QMenu(self)

        actions = menu.addMenu("Que haga algo")
        for key, config in ACTIVITIES.items():
            act = QAction(config["label"], self)
            act.triggered.connect(lambda _c=False, k=key: self.start_activity(k))
            actions.addAction(act)
        actions.addSeparator()
        sorpresa = QAction("Lo que le apetezca", self)
        sorpresa.triggered.connect(
            lambda: self.start_activity(random.choice(list(ACTIVITIES))))
        actions.addAction(sorpresa)

        trajes = menu.addMenu("Ponerse un traje")
        quitar = QAction("Sin traje", self, checkable=True)
        quitar.setChecked(self.costume is None)
        quitar.triggered.connect(lambda: self.set_costume(None))
        trajes.addAction(quitar)
        trajes.addSeparator()
        for group_name, keys in COSTUME_GROUPS:
            grupo = trajes.addMenu(group_name)
            for key in keys:
                act = QAction(COSTUMES[key]["label"], self, checkable=True)
                act.setChecked(self.costume == key)
                act.triggered.connect(lambda _c=False, k=key: self.set_costume(k))
                grupo.addAction(act)
        trajes.addSeparator()
        azar = QAction("Uno al azar", self)
        azar.triggered.connect(
            lambda: self.set_costume(random.choice(list(COSTUMES))))
        trajes.addAction(azar)
        solo = QAction("Que se cambie sola", self, checkable=True)
        solo.setChecked(self.auto_costume)
        solo.triggered.connect(lambda v: setattr(self, "auto_costume", v))
        trajes.addAction(solo)

        if len(self.monitors) > 1:
            screens = menu.addMenu("Ir a la pantalla")
            for index, area in enumerate(self.monitors, start=1):
                act = QAction(f"Pantalla {index} ({area[2] - area[0]} px)", self)
                act.triggered.connect(lambda _c=False, a=area: self.go_to_monitor(a))
                screens.addAction(act)

        follow = QAction("Seguir el raton", self, checkable=True)
        follow.setChecked(self.follow_mouse)
        follow.triggered.connect(lambda v: setattr(self, "follow_mouse", v))
        menu.addAction(follow)

        recolocar = QAction("Recolocar", self)
        recolocar.triggered.connect(self.reset_position)
        menu.addAction(recolocar)

        diagnostico = QAction("Diagnostico", self)
        diagnostico.triggered.connect(self.show_report)
        menu.addAction(diagnostico)

        menu.addSeparator()
        salir = QAction("Salir", self)
        salir.triggered.connect(QApplication.quit)
        menu.addAction(salir)

        menu.exec(event.globalPos())

    def report(self) -> str:
        cx = self.center_x
        return (
            f"estado={self.state} actividad={self.activity} "
            f"traje={self.costume}\n"
            f"pos=({self.x:.0f},{self.y:.0f}) pies={self.feet:.0f} "
            f"suelo={self.floor_for(cx, self.feet)}\n"
            f"ventanas={len(self.platforms)}\n"
            f"monitores(Qt)={self.monitors}\n"
            f"factor_win32_a_qt=({self.transform[2]:.4f}, {self.transform[3]:.4f})"
        )

    def show_report(self):
        self.refresh_world()
        QMessageBox.information(self, "Diagnostico", self.report())

    def mouseDoubleClickEvent(self, _event):
        """Doble clic: salto."""
        if self.state in ("idle", "walk", "act"):
            self.activity = None
            self.state = "fall"
            self.vy = -12.0
            self.vx = self.facing * 2.0

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

    # ---- dibujo -------------------------------------------------------------- #

    def current_config(self):
        return ACTIVITIES.get(self.activity) if self.state == "act" else None

    def current_cells(self):
        """Lista de (columna, fila, caracter) ya colocados en el lienzo."""
        config = self.current_config()
        stepping = self.state in ("walk", "travel", "edge") or bool(
            config and config["move"])

        body_kind = config["body"] if config else "normal"
        if body_kind == "hold":
            body = BODY_HOLD
        elif body_kind == "blink" or self.blink_timer < 0:
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

        bob = 1 if (stepping and (self.ticks // 8) % 2) else 0
        cells = []
        for row, line in enumerate(list(body) + [legs]):
            for col, ch in enumerate(line):
                if ch != ".":
                    cells.append((PET_COL + col, PET_ROW + row - bob, ch))

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
            painter.fillRect(col * SCALE, row * SCALE, SCALE, SCALE, PALETTE[ch])
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
                prop_index, overlay_on)

    def update_mask(self):
        """Solo los pixeles pintados capturan el raton."""
        key = self.frame_signature()
        if key == self._mask_key:
            return
        self._mask_key = key
        region = QRegion()
        for col, row, _ch in self.mirrored(self.current_cells()):
            region = region.united(QRegion(QRect(col * SCALE, row * SCALE,
                                                 SCALE, SCALE)))
        self.setMask(region)


def main():
    set_dpi_awareness()
    app = QApplication(sys.argv)
    pet = Pet()
    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
