# Desktop Pet

Mascota de escritorio pixelada para Windows. Vive por encima de todas las ventanas,
camina por los bordes superiores de las ventanas abiertas como si fueran plataformas,
se cae, se deja arrastrar con el raton, se entretiene sola y se pone trajes tradicionales
de trece paises.

Un solo archivo, sin dependencias de datos: todo el arte son matrices de texto donde
cada caracter es un pixel gordo.

## Requisitos

- Windows (usa la API Win32 para detectar ventanas y monitores)
- Python 3.9 o superior
- `pip install PySide6 pywin32`

## Ejecucion

```
pythonw desktop_pet.py
```

Con `pythonw` no queda ninguna consola abierta detras. Con `python` funciona igual
pero se ve la ventana negra.

Para que arranque con Windows, crea un acceso directo al comando anterior en
`shell:startup` (pegalo en la barra de direcciones del Explorador).

## Controles

| Accion | Resultado |
|---|---|
| Clic izquierdo y arrastrar | La coges; al soltarla sale despedida en la direccion del gesto |
| Doble clic | Salta |
| Clic derecho | Menu completo |

Solo los pixeles dibujados capturan el raton: el resto de la ventana deja pasar los
clics a lo que haya debajo.

## Menu de clic derecho

- **Que haga algo**: lanza una actividad concreta, o "Lo que le apetezca" para una al azar.
- **Ponerse un traje**: elige pais, quitaselo con "Sin traje", "Uno al azar", o deja
  marcado "Que se cambie sola" para que se cambie por su cuenta de vez en cuando.
- **Ir a la pantalla**: solo aparece con varios monitores. Camina hasta el que elijas.
- **Seguir el raton**: si esta activo, se acerca al cursor cuando lo tiene cerca.
- **Recolocar**: la devuelve al monitor principal si se pierde.
- **Diagnostico**: estado, actividad, traje, posicion, suelo detectado, numero de
  ventanas-plataforma y factor de conversion Win32 a Qt. Util si algo se desalinea.
- **Salir**.

## Actividades

Comer palomitas, beber un refresco, tocar el ukelele, leer un libro, programar,
jugar al futbol, conducir el cybertruck, tomar un cafe, hacer pesas, comer pizza,
bailar, echarse una siesta, sentarse en el borde y pescar desde el borde.

Cuando esta ociosa elige una sola, con probabilidad `ACTIVITY_CHANCE`.

### Actividades de canto

Las dos ultimas llevan `edge=True`. Si en ese momento esta de pie sobre el borde
superior de una ventana, no se pone a ello donde este: pasa al estado `edge`,
camina hasta el canto mas cercano de esa ventana, se gira mirando al vacio y ya
alli se sienta con las piernas colgando y balanceandose. Pescando, el sedal cae
por debajo de sus pies, el flotador baila y cada pocos segundos pica un pez.

Se queda a `EDGE_MARGIN` pixeles del canto para que el suelo siga bajo su centro
y no se caiga. Si esta en el suelo del escritorio y no sobre una ventana, o si
tarda demasiado en llegar, empieza la actividad donde este. Cogerla con el raton
o mandarla a otra pantalla cancela el viaje al canto.

Por eso el lienzo mide 18 filas y no 12: las seis de abajo son el hueco para el
sedal. Los pies ya no coinciden con el borde inferior de la ventana, estan en
`PET_BOTTOM`, que es lo que usan la fisica y el aterrizaje.

## Trajes

Son 32, repartidos en dos grupos dentro del menu.

**Paises.** Espania (flamenca), Mexico (charro), Japon (kimono), China (tangzhuang),
Corea (hanbok), India (sari), Escocia (kilt), Rusia (ushanka), Peru (poncho andino),
Bolivia (cholita paceña), Marruecos (chilaba y fez), Baviera (lederhosen) y
Egipto (nemes).

**Personajes.** Arquetipos de anime y dibujos animados: ninja shinobi, samurai,
espadachin errante, guerrero de gi, cazador de espiritus, onmyoji, chica magica,
chica gato, idol, uniforme escolar, cocinero de ramen, piloto de mecha, piloto de
caza espacial, kaiju, superheroe, robot de hojalata, mago, pirata y skater. Son
disenios originales inspirados en los generos, no copias de personajes concretos:
los de series como One Piece o Naruto estan protegidos por derechos de autor y
marca.

Cada traje tiene ropa y un accesorio propio: abanico, maracas, sombrilla, farolillo,
tambor janggu, lampara diya, gaita, matrioska, zampoña, charango, tetera, jarra de
cerveza, cayado, shuriken, katana, espada envainada, esfera de energia, ofuda,
abanico ritual, varita, ovillo de lana, microfono, mochila, bol de ramen, dron,
nave, edificio, rayo, llave inglesa, baston con orbe, loro y monopatin. El traje se
mantiene durante cualquier actividad; el accesorio se esconde mientras la actividad
ya le ocupa las manos con su propio objeto.

El reparto en submenus lo decide `COSTUME_GROUPS`: una lista de pares
`(nombre del grupo, claves de COSTUMES)`. Si anades un traje nuevo, metelo tambien
en un grupo o no saldra en el menu.

## Como esta organizado el archivo

| Bloque | Que contiene |
|---|---|
| `PALETTE` | Un color por caracter. Cualquier caracter usado en el arte debe existir aqui |
| `BODY`, `BODY_BLINK`, `BODY_HOLD`, `LEGS` | El sprite de la mascota, 11x9 pixeles |
| `PROPS` | Objetos animados de las actividades, en coordenadas del lienzo (21x12) |
| `OVERLAYS` | Adornos sobre la cabeza: nota musical, burbujas, zzz |
| `COSTUMES` | Trajes, en coordenadas del sprite |
| `COSTUME_GROUPS` | Como se reparten los trajes en los submenus |
| `ACTIVITIES` | Une prop, postura, piernas, velocidad, adorno y duracion |
| Clase `Pet` | Fisica, deteccion de ventanas y monitores, dibujo y menu |

## Ajustes rapidos

Constantes al principio del archivo:

- `SCALE`: tamanio del pixel. Subelo a 10 o 12 en pantallas 4K.
- `GRAVITY`, `MAX_FALL`, `WALK_SPEED`, `THROW_FACTOR`: fisica.
- `TICK_MS`: milisegundos por fotograma (16 son unos 60 fps).
- `SCAN_MS`: cada cuanto vuelve a mirar que ventanas hay abiertas.
- `ACTIVITY_CHANCE`, `TRAVEL_CHANCE`, `COSTUME_CHANCE`: como de inquieta es.
- `EDGE_MARGIN`: cuanto se separa del canto al sentarse a pescar.

## Anadir un traje nuevo

Copia una entrada de `COSTUMES`. Cada pieza es `(filas, dcol, drow)` en coordenadas
del sprite: `(0, 0)` es la esquina superior izquierda de la mascota.

Filas del sprite:

```
0-1  orejas
2    alto de la cabeza
3-4  ojos
5-6  torso
7    bajo del torso
8    piernas
```

Reglas practicas:

- Las filas del torso (`drow` 5, 6 y 7) miden 11 caracteres y van con `dcol = 0`.
- `drow` negativo queda por encima de la cabeza, con un minimo de -2: por debajo de
  eso el sombrero se sale del lienzo cuando la mascota da el respingo al andar.
- Los accesorios van a los lados, con `dcol` entre -5 y 15.
- Un punto significa pixel transparente. Cualquier otro caracter tiene que estar en
  `PALETTE`.
- Si quieres mas sitio a lo alto o a lo ancho, sube `CANVAS_W` y `CANVAS_H` y ajusta
  `PET_COL` y `PET_ROW`.

Ejemplo minimo:

```python
"pais": {
    "label": "Pais - traje",
    "parts": [
        (["WWWWWWWWWWW",
          "AAAAAAAAAAA",
          "RRRRRRRRRRR"], 0, 5),
    ],
    "accessory": [
        ([".Y.",
          "YYY",
          ".N."], 11, 4),
    ],
},
```

Y anade la clave a un grupo de `COSTUME_GROUPS`.

Un apunte de color: el negro puro (`J`) desaparece sobre fondos de escritorio
oscuros. Para telas oscuras usa mejor `Z`, el azul pizarra.

## Anadir una actividad

1. Dibuja el objeto en `PROPS` como lista de fotogramas `(filas, columna, fila)`,
   esta vez en coordenadas del lienzo de 21x12.
2. Anade la entrada en `ACTIVITIES` con `label`, `prop`, `body` (`normal`, `hold` o
   `blink`), `legs`, `speed`, `overlay`, `move` y, si quieres, `ticks`.

Aparece sola en el menu, no hay que tocar nada mas.

## Problemas conocidos

- Solo Windows. En Linux y macOS no hay `pywin32` ni las llamadas Win32 que usa.
- Si la mascota se descoloca en monitores con escalados distintos, abre "Diagnostico"
  y comprueba `factor_win32_a_qt`. El escalado alto de Qt se desactiva a proposito
  al arrancar (`QT_ENABLE_HIGHDPI_SCALING = 0`) para que las coordenadas de Qt y las
  de Win32 coincidan.
- Algunas ventanas a pantalla completa y algunos juegos capturan el "siempre encima"
  y la tapan. Es una limitacion del propio Windows.
- Si se cae mas de cuatro segundos seguidos, se rescata sola en el suelo del monitor
  mas cercano.
