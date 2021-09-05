import pygame as pg
from math import cos, sin, radians
from random import choice, randrange, choices
import re
import L_system_config_legacy

RED = (255, 0, 0)
BLACK = (0, 0, 0)
CUSTOM_COLOR = (20, 20, 40)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SCREENSHOTS_DIR = r"Sreenshots"


fonts = pg.font.get_fonts()
CONFIG = 'Trees_random.yaml'


class App:
    def __init__(self, WIDTH=1600, HEIGHT=900, CELL_SIZE=8):
        pg.init()
        self.screen = pg.display.set_mode([WIDTH, HEIGHT])
        self.clock = pg.time.Clock()

        self.font_name = choice(fonts)
        self.font = pg.font.SysFont(self.font_name, 48)

        self.showFPS = False
        self.makeSreenshots = True
        self._sreencounter = 0

    def __draw_fps(self):
        img = self.font.render("%.2f" % self.clock.get_fps(), True, RED, BLACK)
        self.screen.blit(img, (20, 15))

    def run(self):
        turtles = []
        eps = 0
        for stats in L_system_config_legacy.get_turtles(CONFIG):
            turtle = Turtle(self.screen, stats[0], stats[1], radians(stats[2]), stats[3] * (1 + eps))
            turtle.set_gens(stats[4])
            if len(stats) >= 6:
                turtle.step = stats[5]*stats[3]
            turtles.append(turtle)

        # turtles[1].set_angel(pi - pi / 3)
        # turtles[2].set_angel(pi + pi / 3)

        # turtles[3].set_angel(pi)
        # turtles[3].step = 500
        # turtles[0].set_angel(pi/2)
        # turtles[1].set_angel(pi/2)

        col_frames = 1000

        while True:
            if self.showFPS:
                self.__draw_fps()

            for i in turtles:
                col_frames = i.next_step(col_frames)

            self.clock.tick(col_frames)
            pg.display.flip()

            if col_frames == 1:
                if self.makeSreenshots:
                    pg.image.save(self.screen, f"{SCREENSHOTS_DIR}\\screenshot_{self._sreencounter}.png")
                    self._sreencounter += 1
                self.screen.fill(BLACK)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_f:
                        self.showFPS = not self.showFPS
                        rect = (20, 15, 250, 60)
                        pg.draw.rect(self.screen, BLACK, rect)
                    elif event.key == pg.K_ESCAPE:
                        exit()
                    elif event.key == pg.K_r:
                        self.font_name = choice(fonts)
                        self.font = pg.font.SysFont(self.font_name, 48)
                        rect = (20, 15, 250, 60)
                        pg.draw.rect(self.screen, BLACK, rect)
                    elif event.key == pg.K_PRINTSCREEN:
                        pg.image.save(self.screen, "screenshot.jpg")


class Turtle:
    def __init__(self, screen, x, y, rotate_ang, scale=6):
        self._screen = screen
        self._x = x
        self._y = y
        self._start_pos = x, y
        self._cur_ang = 0

        self.rotate_ang = rotate_ang
        self.step = 20 * scale
        self._scale = scale
        self._color = (46, 139, 87)
        self._cur_color = self._color
        self._width = 1

        self._step_number = 0
        self._genome = []
        self._stack = [(int, int, float, tuple)]
        self._generation = 0

    def set_gens(self, gens_str):
        self._genome = self._parse_gens(gens_str)
        self._step_number = 0
        self._x = self._start_pos[0]
        self._y = self._start_pos[1]
        self._rnd_color()
        self.step /= self._scale

    @staticmethod
    def _parse_gens(gens_str: str) -> list[str]:
        gens_list = re.findall(r'[^()0-9,. ](?:[(][0-9-,. ]+[)])?', gens_str)
        return gens_list

    def set_cords(self, x, y):
        self._x = x
        self._y = y

    def set_angel(self, angle):
        self._cur_ang = angle

    def rotate(self, angle):
        self._cur_ang += angle

    def _rnd_color(self):
        self._cur_color = tuple(randrange(0, 255) for _ in range(3))

    def draw(self, length):
        end_x = self._x + cos(self._cur_ang) * length
        end_y = self._y - sin(self._cur_ang) * length

        pg.draw.line(self._screen, self._cur_color, (self._x, self._y), (end_x, end_y), self._width)
        self._x = end_x
        self._y = end_y

    def move(self, length):
        self._x += cos(self._cur_ang) * length
        self._y -= sin(self._cur_ang) * length

    def next_generation(self):
        genome_str = ''.join(self._genome)
        for key, value in L_system_config_legacy.rules.items():
            if value[1]:
                all_sub = re.finditer(value[1], genome_str)
                if isinstance(value[0], dict):
                    for i in all_sub:
                        rule = choices(list(value[0].keys()), weights=value[0].values())[0]
                        params = re.findall(r'-?\d+[.]?\d*', i.group())
                        params = tuple(map(float, params))
                        genome_str = genome_str.replace(i.group(), L_system_config_legacy.format_strings(*params, rule=rule), 1)
                else:
                    rule = value[0]
                    for i in all_sub:
                        params = re.findall(r'-?\d+[.]?\d*', i.group())  # Мб стоит вернуть [-+]?
                        params = tuple(map(float, params))
                        genome_str = genome_str.replace(i.group(), L_system_config_legacy.format_strings(*params, rule=rule), 1)
            else:
                if isinstance(value[0], dict):
                    all_sub = re.finditer(key, genome_str)
                    for i in all_sub:
                        rule = choices(list(value[0].keys()), weights=value[0].values())[0]
                        genome_str = genome_str.replace(key, rule.lower(), 1)
                else:
                    rule = value[0]
                    genome_str = genome_str.replace(key, rule.lower())

        genome_str = genome_str.replace(chr(L_system_config_legacy.CHAR_SEPARATOR), '(')
        genome_str = genome_str.replace(chr(L_system_config_legacy.CHAR_SEPARATOR+1), ')')
        genome_str = genome_str.upper()
        self.set_gens(genome_str)
        self._generation += 1

    def next_step(self, fps) -> int:
        if self._step_number == len(self._genome):
            self.next_generation()
            return 1

        params = re.findall(r"[( ,](-?\d+[.]?\d*)[),]", self._genome[self._step_number])

        if self._genome[self._step_number][0] in ('F', 'W', 'U'):
            if params:
                params = tuple(map(float, params))
                self._width = int(params[1])
                self.draw(self.step*params[0])
            else:
                self.draw(self.step)
        elif self._genome[self._step_number].lower() == 's':
            self.move(self.step)
        elif self._genome[self._step_number][0] == '+':
            if params:
                params = tuple(map(float, params))
                self.rotate(radians(params[0]))
            else:
                self.rotate(self.rotate_ang)
        elif self._genome[self._step_number][0] == '-':
            if params:
                params = tuple(map(float, params))
                self.rotate(-radians(params[0]))
            else:
                self.rotate(-self.rotate_ang)
        elif self._genome[self._step_number].lower() == '[':
            self._stack.append((self._x, self._y, self._cur_ang, self._cur_color))
        elif self._genome[self._step_number].lower() == ']':
            self._x, self._y, self._cur_ang, self._cur_color = self._stack.pop()
        self._step_number += 1
        return fps


if __name__ == '__main__':
    app = App()
    app.run()
