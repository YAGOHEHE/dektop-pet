"""Arte pixelado: paleta, sprites, objetos, trajes y actividades.

Todo es texto: un caracter = un pixel. Este modulo no importa Qt ni Windows a
proposito, asi que se puede validar y previsualizar sin arrancar la aplicacion.
Las herramientas de tools/ trabajan sobre el.
"""

# --------------------------------------------------------------------------- #
# Paleta (hex, sin Qt) y arte pixel. Todo se define como filas de texto: un caracter = un
# pixel gordo. Cambia estas matrices para rediseniar la mascota o los objetos.
# --------------------------------------------------------------------------- #

PALETTE = {
    "B": "#C2603E",   # cuerpo
    "S": "#9C4A2F",   # sombra del cuerpo
    "E": "#191919",   # ojos y tinta
    "R": "#D2342B",   # rojo (cubo, lata)
    "W": "#F5EFE6",   # blanco (papel, franja)
    "P": "#F3D57A",   # palomita
    "T": "#B87C4C",   # madera clara
    "N": "#6E4522",   # madera oscura
    "C": "#2D4A7D",   # tapa del libro
    "D": "#17222B",   # pantalla
    "L": "#7ED07A",   # codigo en pantalla
    "K": "#9AA3AB",   # teclado / metal
    "M": "#FFFFFF",   # nota musical, burbujas
    # colores extra usados por los trajes tradicionales
    "G": "#2E7D4F",   # verde
    "A": "#2F5FA8",   # azul indigo
    "Y": "#E8B93A",   # dorado / amarillo
    "O": "#E07B39",   # naranja azafran
    "I": "#E2739B",   # rosa
    "Q": "#7E1B1B",   # granate
    "J": "#20242B",   # negro tela
    "Z": "#414A63",   # azul pizarra (telas oscuras visibles)
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

# Bloques de ojo (columna, fila) dentro del sprite: cada uno mide 2x2 y la
# pupila se mueve por sus cuatro esquinas segun donde mire.
EYES = [(2, 3), (7, 3)]
EYE_PUPIL = "M"          # blanco: hace de brillo dentro del ojo oscuro

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
    # monopatin: una sola fila a la altura de los pies, con las ruedas en las
    # puntas. La mascota va levantada una fila (lift=1) para ir encima.
    "skateboard": [
        (["KTTTTTTTTTTTK"], 4, 11),
        (["WTTTTTTTTTTTW"], 4, 11),
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
    "patinar": dict(label="Patinar", prop="skateboard", body="normal",
                    legs="idle", speed=6, overlay=None, move=2.2,
                    ticks=(420, 900), lift=1),
    "bailar": dict(label="Bailar", prop=None, body="normal",
                   legs="walk", speed=10, overlay="note", move=0.0),
    "siesta": dict(label="Echarse una siesta", prop=None, body="blink",
                   legs="sit", speed=40, overlay="zzz", move=0.0,
                   ticks=(600, 1400)),
}

