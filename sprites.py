import pygame
from constants import TERRAIN

TRANSPARENT = (0, 0, 0, 0)


class HexTile(pygame.sprite.Sprite):

    highlight_color = (50, 50, 200, 150)

    def __init__(self, pos, biome, country, elevation, *groups, **kwargs):
        super(HexTile, self).__init__(*groups)
        

        self.biome = biome
        self.country = country if biome != 'Water' else None

        self.views = ['territory', 'country']
        self.current_view = 0

        self.colors = {'territory': pygame.Color(TERRAIN[biome]['color']),
                       'country': {'France': pygame.Color('Blue'), 'Germany': pygame.Color('Red')}.get(self.country, None)}
        self.descriptions = {'territory': self.biome, 'country': self.country}
        self.color_alt = [.3*col for col in self.color[:3]]
        self.elevation = elevation
        self.footprint_size = kwargs['footprint_size']
        x, y = self.footprint_size


        self.image = pygame.Surface(
            (x, y + self.elevation)).convert_alpha()
        self.draw_image()
        self.rect = self.image.get_rect(bottomleft=pos)

        self.highlighted = False
        self.was_highlighted = False

    @property
    def tile_area(self):
        percentages = [(0.123, 0.125), (0.692, 0), (1, 0.313),
                       (0.877, 0.844), (0.308, 0.969), (0, 0.688)]
        return [(i*self.footprint_size[0], j*self.footprint_size[1]) for i, j in percentages]

    @property
    def color(self):
        return self.colors[self.views[self.current_view]]

    @property
    def description(self):
        return self.descriptions[self.views[self.current_view]]

    def get_bottom_image(self):
        bottom = [self.tile_area[-1], self.tile_area[2]] + \
            [(x, y+self.elevation-1) for x, y in self.tile_area[2:]]
        return bottom

    def toggle_view(self):
        self.current_view = self.current_view + 1
        if self.current_view >= len(self.views):
            self.current_view = 0

    def draw_image(self, highlighted=False):
        if not self.color:
            return
        bottom = self.get_bottom_image()
        color_highlight = [.9*col for col in self.color[:3]]
        color = self.color if not highlighted else color_highlight

        pygame.draw.polygon(self.image, self.color_alt, bottom)
        pygame.draw.polygon(self.image, pygame.Color('black'), bottom, width=2)
        pygame.draw.polygon(self.image, color, self.tile_area)
        pygame.draw.polygon(self.image, pygame.Color(
            'black'), self.tile_area, width=2)

    def highlight(self):
        self.highlighted = True

    def dehighlight(self):
        if self.highlighted:
            self.highlighted = False
            self.was_highlighted = True

    def update(self, **kwargs):
        if self.highlighted:
            self.draw_image(highlighted=True)
        elif self.was_highlighted:
            self.draw_image(highlighted=False)
            self.was_highlighted = False
        if kwargs.get('toggle_view'):
            self.toggle_view()
            self.draw_image()
