import sys
import random
import pygame
import opensimplex as simp

from constants import TERRAIN
from interface import CursorHighlight

BACKGROUND = pygame.Color("darkslategray")
TRANSPARENT = (0, 0, 0, 0)
SCREEN_SIZE = (1800, 780)
FPS = 60


class MapGen(object):
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

    def gen_map(self, noise):
        mapping = [["biome"]*self.HEIGHT for _ in range(self.WIDTH)]
        for x, y in noise:
            for biome, chance in [[key, TERRAIN[key]['chance']] for key in TERRAIN]:
                if noise[x, y] < chance:
                    mapping[y][x] = biome
                    break
        return mapping


def get_value_from_range(range: list) -> int:
    ''' Returns random int from range in provided list of 2 ints. '''
    assert len(range) == 2, 'Provided list must contain exactly 2 elements!'
    return random.randint(*range)


class HexTile(pygame.sprite.Sprite):
    FOOTPRINT_SIZE = (65, 32)

    def __init__(self, pos, biome, *groups):
        super(HexTile, self).__init__(*groups)
        self.color = pygame.Color(TERRAIN[biome]['color'])
        self.height = get_value_from_range(TERRAIN[biome]['height'])
        self.image = self.make_tile(biome)
        self.rect = self.image.get_rect(bottomleft=pos)
        self.mask = self.make_mask()
        self.biome = biome

    def make_tile(self, biome):
        h = self.height
        points = (8, 4), (45, 0), (64, 10), (57, 27), (20, 31), (0, 22)
        bottom = [points[-1], points[2]] + [(x, y+h-1) for x, y in points[2:]]
        image = pygame.Surface((65, 32+h)).convert_alpha()
        image.fill(TRANSPARENT)
        bottom_col = [.5*col for col in self.color[:3]]
        pygame.draw.polygon(image, bottom_col, bottom)
        pygame.draw.polygon(image, self.color, points)
        pygame.draw.lines(image, pygame.Color("black"), 1, points, 2)
        for start, end in zip(points[2:], bottom[2:]):
            pygame.draw.line(image, pygame.Color("black"), start, end, 1)
        pygame.draw.lines(image, pygame.Color("black"), 0, bottom[2:], 2)
        return image

    def make_mask(self):
        points = (8, 4), (45, 0), (64, 10), (57, 27), (20, 31), (0, 22)
        temp_image = pygame.Surface(self.image.get_size()).convert_alpha()
        temp_image.fill(TRANSPARENT)
        pygame.draw.polygon(temp_image, pygame.Color("red"), points)
        return pygame.mask.from_surface(temp_image)


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
        self.mapping = MapGen()
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
                HexTile(pos, biome, tiles)
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
    app = App()
    app.main_loop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
