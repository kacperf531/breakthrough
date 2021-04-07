import sys
import random
import pygame
import opensimplex as simp

from constants import TERRAIN
from interface import CursorHighlight
from sprites import HexTile

BACKGROUND = pygame.Color("darkslategray")
SCREEN_SIZE = (1800, 780)
FPS = 60


class MapGenerator(object):
    WIDTH, HEIGHT = 16, 16

    def __init__(self):
        self.seed = random.randrange(2**32)
        freq = random.randrange(5, 10)
        noise = self.gen_noise(simp.OpenSimplex(self.seed), freq)
        self.terrain = self.gen_map(noise)

    def noise(self, gen, nx, ny, freq=10):
        # Rescale from -1.0:+1.0 to 0.0:1.0
        return gen.noise2d(freq*nx, freq*ny) / 2.0 + 0.5

    def gen_noise(self, gen, freq=10):
        vals = {}
        for y in range(self.WIDTH):
            for x in range(self.HEIGHT):
                nx = float(x)/self.WIDTH - 0.5
                ny = float(y)/self.HEIGHT - 0.5
                vals[x, y] = self.noise(gen, nx, ny, freq)
        return vals

    def gen_river(self, source: tuple, river):
        ''' Generates a river on the map. '''
        flood_chance = {}
        for x in range(source[0] - 1, source[0] + 1):
            if x < 0:
                continue
            for y in range(source[1] - 1, source[1] + 1):
                if y < 0:
                    continue
                flood_chance[x, y] = random.randint(0, 20)
        new_source = min(flood_chance)
        if new_source == source or new_source[0] in [0, self.WIDTH] or new_source[1] in [0, self.HEIGHT]:
            return river if river else [source]
        river.append(new_source)
        return(self.gen_river(new_source, river))

    def gen_map(self, noise):
        mapping = [["biome"]*self.HEIGHT for _ in range(self.WIDTH)]
        rivers = []
        for x, y in noise:
            for biome, chance in [[key, TERRAIN[key]['chance']] for key in TERRAIN]:
                if noise[x, y] < chance:
                    mapping[y][x] = biome
                    if biome == 'Water':
                        river = self.gen_river((x, y), [])
                        rivers.append(river)
                    break
        for river in rivers:
            for point in river:
                mapping[point[0]][point[1]] = 'Water'
        return mapping


def get_randomized_height(range: list) -> int:
    ''' Returns random int from range in provided list of 2 ints. '''
    assert len(range) == 2, 'Provided list must contain exactly 2 elements!'
    return random.randint(*range)


class App(object):
    def __init__(self, font_name: str = 'Arial', font_size: int = 32):
        self.screen = pygame.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.done = False
        self.tiles = self.make_map()
        self.font = pygame.font.SysFont(font_name, font_size)
        self.cursor = CursorHighlight(font=self.font)

    def make_map(self):
        tiles = pygame.sprite.LayeredUpdates()
        self.mapping = MapGenerator()
        width, height = self.mapping.WIDTH, self.mapping.HEIGHT
        start_x, start_y = self.screen_rect.midtop
        start_x -= 100
        start_y += 100
        row_offset = -45, 22
        col_offset = 57, 5
        for i in range(width):
            for j in range(height):
                biome = self.mapping.terrain[i][j]
                pos = (start_x + row_offset[0]*i + col_offset[0]*j,
                       start_y + row_offset[1]*i + col_offset[1]*j)
                HexTile(pos, biome,get_randomized_height(TERRAIN[biome]['height']) , tiles)
        return tiles

    def update(self):
        for sprite in self.tiles:
            if sprite.layer != sprite.rect.bottom:
                self.tiles.change_layer(sprite, sprite.rect.bottom)
        self.cursor.update(pygame.mouse.get_pos(),
                           self.tiles, self.screen_rect)

    def render(self):
        self.screen.fill(BACKGROUND)
        self.tiles.draw(self.screen)
        self.cursor.draw(self.screen)
        pygame.display.update()

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

    def main_loop(self):
        while not self.done:
            self.event_loop()
            self.update()
            self.render()
            self.clock.tick(FPS)


def main():
    pygame.init()
    pygame.display.set_mode(SCREEN_SIZE)
    App().main_loop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
