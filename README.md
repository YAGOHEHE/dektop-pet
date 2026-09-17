# Desktop Pet

Mascota de escritorio pixelada para Windows. Vive por encima de todas las
ventanas, camina por sus bordes superiores como si fueran plataformas, salta de
una a otra, se cae, se deja arrastrar, se sienta en el canto a pescar, se pone
trajes de 32 paises y personajes, y elige que hacer segun su humor y segun la
ventana que tengas delante.

Todo el arte son matrices de texto: un caracter es un pixel gordo.

## Instalacion y ejecucion

```
pip install PySide6 pywin32
pythonw run_pet.pyw
```

Con `pythonw` no queda consola detras. Para que arranque con Windows, crea un
acceso directo a ese comando en `shell:startup` (pegalo en la barra de
direcciones del Explorador).

Para repartirla sin pedir que instalen Python, hay receta de PyInstaller:

```
pip install pyinstaller
pyinstaller pet.spec          # deja dist/MascotaEscritorio.exe
```

## Estructura

```
run_pet.pyw            lanzador
pet.spec               receta de PyInstaller
desktop_pet/
    art.py             paleta, sprites, objetos, trajes y actividades
    config.py          constantes de simulacion
    desktop.py         capa de escritorio: Windows, o doble de pruebas
    settings.py        ajustes que sobreviven al cierre
    mood.py            humor y necesidades
    context.py         que le apetece segun la ventana en primer plano
    pet.py             motor: fisica, estados y dibujo
    menu.py            el menu, compartido por el clic derecho y la bandeja
    app.py             arranque, icono de bandeja
tools/
    validate_art.py    comprueba el arte
    smoke_test.py      ejecuta la mascota entera sin Windows ni pantalla
    preview.py         laminas PNG de trajes y actividades
    png_to_sprite.py   convierte una imagen en filas de sprite
```

`art.py` no importa Qt ni Windows, y `pet.py` no importa Windows: solo habla con
un `DesktopBackend`. Por eso las herramientas funcionan en cualquier sistema.

## Controles

| Accion | Resultado |
|---|---|
| Clic izquierdo y arrastrar | La coges; al soltarla sale despedida |
| Doble clic | Salta |
| Clic derecho | Menu completo |
| Icono de la bandeja | El mismo menu, y un clic la trae a la vista |

Solo los pixeles dibujados capturan el raton: el resto de la ventana deja pasar
los clics a lo que haya debajo.

## Menu

- **Que haga algo**: lanza una actividad, o "Lo que le apetezca", que usa el
  mismo criterio que ella (contexto y humor).
- **Ponerse un traje**: por grupos, con "Sin traje", uno al azar y el
  interruptor de cambiarse sola.
- **Ir a la pantalla**: con varios monitores, camina hasta el que elijas.
- **Comportamiento**: seguir el raton, hacer caso a su humor, mirar que ventana
  usas.
- **Recolocar**, **Diagnostico** y **Salir**.

Todo lo que se marca aqui queda guardado.

## Que hace sola

**Actividades.** Comer palomitas, beber un refresco, tocar el ukelele, leer,
programar, jugar al futbol, conducir el cybertruck, tomar un cafe, hacer pesas,
comer pizza, patinar, bailar, echarse una siesta, sentarse en el borde y pescar.

**Humor.** Lleva cuatro necesidades (energia, hambre, juego, calma) que bajan
solas. Cada actividad cubre una, y elige con mas probabilidad la que cubre la
que tiene mas baja. De madrugada casi siempre le toca dormir. Se apaga desde el
menu si prefieres que sea puro azar.

**Contexto.** Mira el titulo de la ventana en primer plano: delante del editor
se pone a programar, con un video saca el ukelele o las palomitas, en el
navegador se va al canto. Las reglas estan en `context.py`, en una lista de
palabras facil de ampliar.

**Actividades de canto.** Sentarse en el borde y pescar llevan `edge=True`: si
esta sobre una ventana, camina hasta el canto, se gira mirando al vacio y alli
se sienta con las piernas colgando. Pescando, el sedal cae por debajo de sus
pies y cada pocos segundos pica un pez. Se queda a `EDGE_MARGIN` pixeles del
borde para no caerse.

**Saltos entre ventanas.** Al llegar al borde ya no se deja caer siempre: si hay
otra ventana al alcance calcula el impulso y salta. Los limites son
`HOP_REACH`, `HOP_UP_MAX` y `HOP_DOWN_MAX`; con `HOP_CHANCE` a veces prefiere
tirarse, que queda mas natural.

**Mirada.** Las pupilas se mueven por el ojo siguiendo el cursor, y miran hacia
donde camina cuando el raton esta lejos.

## Trajes

Son 32, en dos grupos.

**Paises.** Espania (flamenca), Mexico (charro), Japon (kimono), China
(tangzhuang), Corea (hanbok), India (sari), Escocia (kilt), Rusia (ushanka),
Peru (poncho andino), Bolivia (cholita paceña), Marruecos (chilaba y fez),
Baviera (lederhosen) y Egipto (nemes).

**Personajes.** Arquetipos de anime y dibujos: ninja shinobi, samurai,
espadachin errante, guerrero de gi, cazador de espiritus, onmyoji, chica magica,
chica gato, idol, uniforme escolar, cocinero de ramen, piloto de mecha, piloto
de caza espacial, kaiju, superheroe, robot de hojalata, mago, pirata y skater.
Son disenios originales inspirados en los generos, no copias de personajes
concretos: los de series como One Piece o Naruto estan protegidos por derechos
de autor y marca.

Cada traje lleva ropa y un accesorio, que se esconde cuando la actividad ya le
ocupa las manos. El reparto en submenus lo decide `COSTUME_GROUPS`: si anades un
traje, metelo tambien en un grupo o no saldra en el menu.

## Ajustes guardados

En `%APPDATA%\desktop_pet\settings.json` (o `~/.config/desktop_pet` fuera de
Windows). Guarda traje, posicion y las preferencias del menu. Si el archivo se
corrompe o no hay permisos, arranca con los valores por defecto sin quejarse, y
solo acepta claves conocidas: editarlo a mano no puede inyectar nada raro.

## Herramientas

```
python tools/validate_art.py              # antes de cada commit
python tools/smoke_test.py                # ejecuta la mascota sin Windows
python tools/preview.py trajes t.png      # lamina de los 32 trajes
python tools/preview.py actividades a.png
python tools/png_to_sprite.py dibujo.png --ancho 11
```

`smoke_test.py` arranca la aplicacion de verdad con Qt en modo offscreen y un
escritorio simulado: mueve la mascota 9000 fotogramas, dibuja las 15
actividades y los 32 trajes, comprueba los saltos entre ventanas, las
actividades de canto, la persistencia y que parada no repinta. Es la red de
seguridad para tocar el motor sin tener Windows delante.

`png_to_sprite.py` necesita Pillow (`pip install pillow`), que no hace falta
para ejecutar la mascota.

## Ajustes rapidos

En `config.py`:

- `SCALE`: tamanio del pixel. Subelo a 10-12 en pantallas 4K.
- `GRAVITY`, `MAX_FALL`, `WALK_SPEED`, `THROW_FACTOR`: fisica.
- `TICK_MS`: milisegundos por fotograma (16 son unos 60 fps).
- `SCAN_MS`: cada cuanto vuelve a mirar que ventanas hay.
- `ACTIVITY_CHANCE`, `TRAVEL_CHANCE`, `COSTUME_CHANCE`, `CONTEXT_CHANCE`.
- `EDGE_MARGIN`, `HOP_*`, `GAZE_RANGE`.

## Anadir un traje

Copia una entrada de `COSTUMES` en `art.py`. Cada pieza es
`(filas, dcol, drow)` en coordenadas del sprite: `(0, 0)` es su esquina
superior izquierda.

```
0-1  orejas        5-6  torso
2    alto cabeza   7    bajo del torso
3-4  ojos          8    piernas
```

- Las filas del torso (`drow` 5, 6 y 7) miden 11 caracteres con `dcol = 0`.
- `drow` negativo queda por encima de la cabeza, con un minimo de -2: por debajo
  se sale del lienzo cuando la mascota da el respingo al andar o se sube al
  monopatin.
- Los accesorios van a los lados, con `dcol` entre -5 y 15.
- Un punto es pixel transparente; cualquier otro caracter tiene que estar en
  `PALETTE`.
- El negro puro (`J`) desaparece sobre fondos oscuros: para telas oscuras usa
  `Z`, el azul pizarra.

Anade la clave a un grupo de `COSTUME_GROUPS` y pasa `validate_art.py`.

## Anadir una actividad

1. Dibuja el objeto en `PROPS` como lista de fotogramas `(filas, columna, fila)`,
   esta vez en coordenadas del lienzo (21x18).
2. Anade la entrada en `ACTIVITIES` con `label`, `prop`, `body`, `legs`, `speed`,
   `overlay`, `move` y, si quieres, `ticks`, `edge` o `lift`.
3. Si cubre alguna necesidad, apuntala en `COVERS` de `mood.py`.

Aparece sola en el menu.

## Detalles del lienzo

Mide 21x18 pixeles gordos. La mascota ocupa las filas 3 a 11; las de arriba son
para sombreros y las seis de abajo, para el sedal de la caña. Los pies no
coinciden con el borde inferior de la ventana: estan en `PET_BOTTOM`, que es lo
que usan la fisica y el aterrizaje.

`lift` sube el sprite (el monopatin lo usa) y anula el respingo del paso en vez
de sumarse: si se sumaran, los sombreros altos se saldrian por arriba.

## Problemas conocidos

- Solo Windows. En otros sistemas arranca con el backend de mentira: se ve y se
  arrastra, pero no detecta ventanas ni monitores como plataformas. Portarlo es
  escribir otra subclase de `DesktopBackend`.
- Si se descoloca con monitores de escalados distintos, mira "Diagnostico" y el
  `factor_nativo_a_qt`. El escalado alto de Qt se desactiva a proposito al
  arrancar para que las coordenadas de Qt y las nativas coincidan.
- Algunas ventanas a pantalla completa y algunos juegos capturan el "siempre
  encima" y la tapan. Es una limitacion de Windows.
- Si se cae mas de cuatro segundos seguidos, se rescata sola en el suelo del
  monitor mas cercano.
