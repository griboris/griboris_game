import pygame


class HP(pygame.sprite.Sprite):
    def __init__(self, character):
        self.character = character
        super().__init__()
        x = self.character.hit_points*30 + (self.character.hit_points-1)*10
        self.image = pygame.surface.Surface((x, 30))
        self.rect = self.image.get_rect(bottomleft=(self.character.rect.x, self.character.rect.y))

    def hearts_output(self):
        x = self.character.hit_points * 30 + (self.character.hit_points - 1) * 10
        x *= int(self.character.hit_points > 0)
        self.image = pygame.surface.Surface((x+int(self.character.hit_points <= 0), 30))
        self.rect = self.image.get_rect(center=(self.character.rect.centerx, self.character.rect.y))

        surface = pygame.surface.Surface((30, 30))
        surface.fill('red')
        for i in range(self.character.hit_points):
            self.image.blit(surface, (i*40, 0))

    def update(self):
        self.rect.centerx = self.character.rect.centerx
        self.rect.bottom = self.character.rect.y
        self.hearts_output()
