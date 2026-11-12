"""Plantilla del juego Arkanoid para el hito M2.

Completa los métodos marcados con TODO respetando las anotaciones de tipo y la
estructura de la clase. El objetivo es construir un prototipo jugable usando
pygame que cargue bloques desde un fichero de nivel basado en caracteres.
"""
from arkanoid_core import *
# --------------------------------------------------------------------- #
# Métodos a completar por el alumnado
# --------------------------------------------------------------------- #

from pathlib import Path

@arkanoid_method
def cargar_nivel(self) -> list[str]:
    """Lee el fichero de nivel y devuelve la cuadrícula como lista de filas."""
    # - Comprueba que `self.level_path` existe y es fichero.
    # - Lee su contenido, filtra líneas vacías y valida que todas tienen el mismo ancho.
    # - Guarda el resultado en `self.layout` y devuélvelo.
    ruta = Path(self.level_path)

    if not ruta.is_file():
        raise FileNotFoundError

    lineas = ruta.read_text().splitlines()


    longitud_linea = None
    for linea in lineas:
        if linea != "":
            if longitud_linea != None and longitud_linea != len(linea):
                raise ValueError("Formato del fichero no valido")
            else:
                longitud_linea = len(linea)
            self.layout.append(linea)

    return self.layout
    


@arkanoid_method
def preparar_entidades(self) -> None:
    """Posiciona paleta y bola, y reinicia puntuación y vidas."""
    # - Ajusta el tamaño de `self.paddle` y céntrala usando `midbottom`.
    # - Reinicia `self.score`, `self.lives` y `self.end_message`.
    # - Llama a `self.reiniciar_bola()` para colocar la bola sobre la paleta.
    self.paddle.midbottom = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 50) # el tamaño ya viene en arkanoid_core.py
    self.score = 0
    self.lives = 3
    self.end_message = ""
    self.reiniciar_bola()

@arkanoid_method
def crear_bloques(self) -> None:
    """Genera los rectángulos de los bloques en base a la cuadrícula.""" 
    # - Limpia `self.blocks`, `self.block_colors` y `self.block_symbols`.
    # - Recorre `self.layout` para detectar símbolos de bloque.
    # - Usa `self.calcular_posicion_bloque` y rellena las listas paralelas.
    self.blocks.clear()
    self.block_colors.clear()
    self.block_symbols.clear()
    self.block_lives.clear()
    for y in range(len(self.layout)):
        for x in range(len(self.layout[y])):

            if self.layout[y][x] not in self.BLOCK_SYMBOLS:
                raise Exception(F"Símbolo de bloque desconocido. Simbolos: {self.BLOCK_SYMBOLS}")

            if self.layout[y][x] == ".":
                continue
            
            self.blocks.append(self.calcular_posicion_bloque(y, x))

            if y + 1 < len(self.layout) and "@" in self.layout[y + 1]:
                            """
                            Esto es lo que pone en el readme:
                            '@: bloque reforzado que otorga más puntos (cambia el color de la fila superior).'
                            
                            Si hay un bloque reforzado toda la fila superior es de color rojo
                            """
                            self.block_colors.append((255, 0, 0))
            else:
                self.block_colors.append(self.BLOCK_COLORS[self.layout[y][x]])
            
            self.block_lives.append(self.BLOCK_LIVES[self.layout[y][x]])
            self.block_symbols.append(self.layout[y][x])
                   

@arkanoid_method
def procesar_input(self) -> None:
    """Gestiona la entrada de teclado para mover la paleta."""
    # - Obtén el estado de teclas con `self.obtener_estado_teclas()`.
    # - Desplaza la paleta con `self.PADDLE_SPEED` si se pulsan las teclas izquierda/derecha.
    # - Limita la posición para que no salga de la pantalla.
    estado_teclas = self.obtener_estado_teclas()
    if estado_teclas[self.KEY_RIGHT] and self.paddle.bottomright[0] < self.SCREEN_WIDTH:
        self.paddle.x += self.PADDLE_SPEED

    if self.paddle.bottomright[0] > self.SCREEN_WIDTH:
        self.paddle.bottomright = (self.SCREEN_WIDTH, self.paddle.bottomright[1])

    if estado_teclas[self.KEY_LEFT] and self.paddle.bottomleft[0] > 0:
        self.paddle.x -= self.PADDLE_SPEED
    
    if self.paddle.bottomleft[0] < 0:
        self.paddle.bottomleft = (0, self.paddle.bottomleft[1])


@arkanoid_method
def actualizar_bola(self) -> None:
    """Actualiza la posición de la bola y resuelve colisiones."""
    # - Suma `self.ball_velocity` a `self.ball_pos` y genera `ball_rect` con `self.obtener_rect_bola()`.
    # - Gestiona rebotes con paredes, paleta y bloques, modificando velocidad y puntuación.
    # - Controla fin de nivel cuando no queden bloques y resta vidas si la bola cae.

    rect_bola_anterior = self.obtener_rect_bola()
    self.ball_pos += self.ball_velocity
    rect_bola = self.obtener_rect_bola()

    if self.ball_pos.x >= self.SCREEN_WIDTH - self.BALL_RADIUS or self.ball_pos.x <= self.BALL_RADIUS:
        self.ball_velocity.x *= -1

    if self.ball_pos.y <= self.BALL_RADIUS:
        self.ball_velocity.y *= -1

    if self.paddle.colliderect(rect_bola):
        pygame.mixer.Sound.play(self.bounce)
        if self.paddle.top >= rect_bola_anterior.bottom and self.ball_velocity.y > 0:
            self.ball_velocity.y *= -1
        elif self.paddle.bottom <= rect_bola_anterior.top and self.ball_velocity.y < 0:
            self.ball_velocity.y *= -1
        else:
            self.ball_velocity.x *= -1


    if self.ball_pos.y > self.paddle.bottomleft[1]:
        self.lives -= 1
        self.reiniciar_bola()
        if self.lives <= 0:
            pygame.mixer.stop()
            pygame.mixer.Sound.play(self.losing)
    
    for i in range(len(self.blocks)):
        if self.block_symbols[i] != "." and self.blocks[i].colliderect(self.obtener_rect_bola()):
            pygame.mixer.Sound.play(self.bounce)
            if self.blocks[i].top >= rect_bola_anterior.bottom and self.ball_velocity.y > 0:
                self.ball_velocity.y *= -1
            elif self.blocks[i].bottom <= rect_bola_anterior.top and self.ball_velocity.y < 0:
                self.ball_velocity.y *= -1
            else:
                self.ball_velocity.x *= -1

            self.block_lives[i] -= 1

            if self.block_lives[i] <= 0:
                if self.block_symbols[i] == "@":
                    pygame.mixer.Sound.play(self.reinforce_block)

                self.score += self.BLOCK_POINTS[self.block_symbols[i]]
                self.blocks.pop(i)
                self.block_colors.pop(i)
                self.block_symbols.pop(i)
                self.block_lives.pop(i)

                if self.ball_velocity.magnitude() <= self.BALL_THRESHOLD_SPEED:
                    self.ball_velocity *= 1.025 # Por cada blqoue roto la velocidad sube un 2.5% hasta un limite

                if len(self.blocks) <= 0:
                    pygame.mixer.stop()
                    pygame.mixer.Sound.play(self.winning)
            
            break
         

@arkanoid_method
def dibujar_escena(self) -> None:
    """Renderiza fondo, bloques, paleta, bola y HUD."""
    # - Rellena el fondo y dibuja cada bloque con `self.dibujar_rectangulo`.
    # - Pinta la paleta y la bola con las utilidades proporcionadas.
    # - Muestra puntuación, vidas y mensajes usando `self.dibujar_texto`.

    self.screen.fill(self.BACKGROUND_COLOR)

    for i in range(len(self.blocks)):
        if self.block_symbols[i] != ".":
            self.dibujar_rectangulo(self.blocks[i], self.block_colors[i])

    self.dibujar_rectangulo(self.paddle, self.PADDLE_COLOR)
    self.dibujar_circulo(self.ball_pos, self.BALL_RADIUS, self.BALL_COLOR)
    self.dibujar_texto(f"Vidas: {self.lives}", (30, 30))
    self.dibujar_texto(f"Puntuacion: {self.score}", (600, 30))

    if self.lives <= 0:
        self.end_message = "HAS PERDIDO"
    elif len(self.blocks) == 0:
        self.end_message = "HAS GANADO!!"

    self.dibujar_texto(self.end_message, (200, 30), True)

@arkanoid_method
def run(self) -> None:
    """Ejecuta el bucle principal del juego."""
    # - Inicializa recursos (`self.inicializar_pygame`, `self.cargar_nivel`, etc.).
    # - Procesa eventos de `self.iterar_eventos()` y llama a los métodos de actualización/dibujo.
    # - Refresca la pantalla con `self.actualizar_pantalla()` y cierra con `self.finalizar_pygame()`.
    
    self.inicializar_pygame()
    self.cargar_nivel()
    self.preparar_entidades()
    self.crear_bloques()
    pygame.mixer.Sound.play(self.music, -1)

    while True:
        
        for evento in self.iterar_eventos():
            if evento.type == self.EVENT_QUIT:
                self.finalizar_pygame()
                return       

        if not self.lives <= 0 and not len(self.blocks) == 0:
            self.actualizar_bola()
            self.procesar_input()

        self.dibujar_escena()
        self.actualizar_pantalla()

        if self.obtener_estado_teclas()[self.KEY_ESCAPE]:
            self.finalizar_pygame()
            return
        
        self.clock.tick(self.FPS)

        

def main() -> None:
    """Permite ejecutar el juego desde la línea de comandos."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Plantilla del hito M2: Arkanoid con pygame.",
    )
    parser.add_argument(
        "level",
        type=str,
        help="Ruta al fichero de nivel (texto con # para bloques y . para huecos).",
    )
    args = parser.parse_args()

    game = ArkanoidGame(args.level)
    game.run()


if __name__ == "__main__":
    main()
