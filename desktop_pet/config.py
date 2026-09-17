"""Parametros de simulacion. Todo lo que se toca a mano vive aqui."""

SCALE = 7                 # tamanio del pixel. Subelo a 10-12 en pantallas 4K.
GRAVITY = 0.9
MAX_FALL = 24.0
WALK_SPEED = 1.5
THROW_FACTOR = 0.45
TICK_MS = 16              # ~60 fps
SCAN_MS = 600             # cada cuanto vuelve a mirar que ventanas hay

ACTIVITY_CHANCE = 0.45
TRAVEL_CHANCE = 0.12
COSTUME_CHANCE = 0.07
EDGE_MARGIN = 6.0         # px que deja entre su centro y el canto de la ventana

# Salto de ventana a ventana
HOP_CHANCE = 0.75         # probabilidad de intentarlo en vez de dejarse caer
HOP_REACH = 230.0         # px de hueco que se atreve a saltar
HOP_UP_MAX = 85.0         # cuanto puede subir de un salto (v^2/2g con HOP_VY)
HOP_DOWN_MAX = 420.0      # cuanto acepta bajar
HOP_VY = -13.0            # impulso vertical del salto
HOP_VX = 3.2              # impulso horizontal del salto

# Reaccion a la ventana en primer plano
CONTEXT_CHANCE = 0.55     # con que frecuencia la actividad la decide el contexto

# Mirada
GAZE_RANGE = 700.0        # px dentro de los cuales sigue al cursor con los ojos
