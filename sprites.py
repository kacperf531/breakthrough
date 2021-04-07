import pygame
from constants import TERRAIN


class HexTile(pygame.sprite.Sprite):
    FOOTPRINT_SIZE = (65, 32)

    def __init__(self, pos, biome, height, *groups):
        super(HexTile, self).__init__(*groups)
        self.color = pygame.Color(TERRAIN[biome]['color'])
        self.height = height
        self.image = self.make_tile(biome)
        self.rect = self.image.get_rect(bottomleft=pos)
        self.mask = self.make_mask()
        self.biome = biome

    def make_tile(self, biome):
        h = self.height
        points = (8, 4), (45, 0), (64, 10), (57, 27), (20, 31), (0, 22)
        bottom = [points[-1], points[2]] + [(x, y+h-1) for x, y in points[2:]]
        image = pygame.Surface((65, 32+h)).convert_alpha()
        image.fill((0, 0, 0, 0))
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
        temp_image.fill((0, 0, 0, 0))
        pygame.draw.polygon(temp_image, pygame.Color("red"), points)
        return pygame.mask.from_surface(temp_image)
