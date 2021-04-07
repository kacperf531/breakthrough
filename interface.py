import pygame

from constants import TERRAIN

TRANSPARENT = (0, 0, 0, 0)

def outline_render(text, font, color, width, outline=pygame.Color("black")):
    text_rend = font.render(text, 1, color)
    outline_rend = font.render(text, 1, outline)
    text_rect = text_rend.get_rect()
    final_rect = text_rect.inflate((width*2,width*2))
    text_rect.center = final_rect.center
    image = pygame.Surface(final_rect.size).convert_alpha()
    image.fill(TRANSPARENT)
    for i in range(-width, width+1):
        for j in range(-width, width+1):
            pos_rect = text_rect.move(i,j)
            image.blit(outline_rend, pos_rect)
    image.blit(text_rend, text_rect)
    return image

class CursorHighlight(pygame.sprite.Sprite):
    FOOTPRINT_SIZE = (65, 32)
    COLOR = (50, 50, 200, 150)
    
    def __init__(self, *groups, font=None):
        self.font = font
        super(CursorHighlight, self).__init__(*groups) 
        points = (8,4), (45,0), (64,10), (57,27), (20,31), (0,22)
        self.image = pygame.Surface(self.FOOTPRINT_SIZE).convert_alpha()
        self.image.fill(TRANSPARENT)
        pygame.draw.polygon(self.image, self.COLOR, points)
        self.rect = pygame.Rect((0,0,1,1))
        self.mask = pygame.Mask((1,1))
        self.mask.fill()
        self.target = None
        self.biome = None
        self.label_image = None
        self.label_rect = None
            
    def update(self, pos, tiles, screen_rect):
        self.rect.topleft = pos
        hits = pygame.sprite.spritecollide(self, tiles, 0, pygame.sprite.collide_mask)
        if hits:
            for sprite in tiles.sprites():
                sprite.dehighlight()
            true_hit = max(hits, key=lambda x: x.rect.bottom)
            true_hit.highlight()
            tiles.update()
            self.target = true_hit.rect.topleft
            self.biome = true_hit.biome
            self.label_image = outline_render(f'{self.biome}', self.font, pygame.Color("white"), 2)
            self.label_rect = self.label_image.get_rect(midbottom=pos)
            self.label_rect.clamp_ip(screen_rect)
        else:
            self.biome = None

    def draw(self, surface):
        if self.biome:
            surface.blit(self.label_image, self.label_rect)
      
