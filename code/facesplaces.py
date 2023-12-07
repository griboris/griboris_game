import random

import pygame
from game_data import levels
from game_data import screen_width, screen_height
from random import randint


#  Прямоугольник, обозначающий уровень
class LevelBox(pygame.sprite.Sprite):
    def __init__(self, pos, status, icon_speed, num):
        super().__init__()
        self.image = pygame.Surface((100, 80))
        if status == 'available':
            self.image.fill('red')
        else:
            self.image.fill('grey')
        self.rect = self.image.get_rect(center=pos)

        font = pygame.font.SysFont('arial', 80)
        self.image.blit(font.render(str(num), 1, 'white'), (30, -5))

        self.zone = pygame.Rect(self.rect.centerx - (icon_speed / 2), self.rect.centery - (icon_speed / 2),
                                          icon_speed, icon_speed)


#  иконка для выбора уровня
class Cursor(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pygame.Surface((20, 20))
        self.image.fill('blue')
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.center = self.pos


#  карта уровней
class LevelMap:
    def __init__(self, start_level, max_level, surface, create_download):

        self.display_surface = surface
        self.current_level = start_level
        self.max_level = max_level
        self.create_download = create_download

        self.moving = False
        self.move_direction = pygame.math.Vector2(0, 0)
        self.speed = 8

        self.setup_nodes()
        self.setup_icons()

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()

        for index, node_data in enumerate(levels.values()):
            if index <= self.max_level:
                node_sprite = LevelBox(node_data['node_pos'], 'available', self.speed, index)
            else:
                node_sprite = LevelBox(node_data['node_pos'], 'locked', self.speed, index)
            self.nodes.add(node_sprite)

    # нарисовать пути между доступными уровнями
    def draw_paths(self):
        points = [node['node_pos'] for index, node in enumerate(levels.values()) if index <= self.max_level]
        pygame.draw.lines(self.display_surface, 'red', False, points, 6)

    def setup_icons(self):
        self.icon = pygame.sprite.GroupSingle()
        icon_sprite = Cursor(self.nodes.sprites()[self.current_level].rect.center)
        self.icon.add(icon_sprite)

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.moving:
            if keys[pygame.K_RIGHT] and self.current_level < self.max_level:
                self.move_direction = self.get_movement_data('next')
                self.current_level += 1
                self.moving = True
            elif keys[pygame.K_LEFT] and self.current_level >= 1:
                self.move_direction = self.get_movement_data('previous')
                self.current_level -= 1
                self.moving = True
            elif keys[pygame.K_SPACE]:
                self.create_download(self.current_level)

    def get_movement_data(self, target):
        start = pygame.math.Vector2(self.nodes.sprites()[self.current_level].rect.center)

        if target == 'next':
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level + 1].rect.center)
        else:
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level - 1].rect.center)

        return (end - start).normalize()

    def update_icon_pos(self):
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0, 0)

    def run(self):
        font = pygame.font.SysFont('arial', 64)

        surface = pygame.Surface((370, 80))
        surface.fill((70, 70, 70))
        surface.blit(font.render('Карта уровней:', 1, 'red', ), (0, 0))

        self.display_surface.blit(surface, (screen_width / 2 - 150, 50))

        self.input()
        self.update_icon_pos()
        self.icon.update()
        self.draw_paths()
        self.nodes.draw(self.display_surface)
        self.icon.draw(self.display_surface)


class Download:
    def __init__(self, level, surface, create_level):

        self.display_surface = surface
        self.level = level
        self.create_level = create_level
        self.time = 0

        self.backgrounds = []
        for i in range(4):
            image = pygame.image.load('../graphics/fon' + str(i+1) + '.jpg').convert_alpha()
            self.backgrounds.append(image)

    def run(self):
        font = pygame.font.SysFont('arial', 80)

        surface = pygame.Surface((370, 80))
        rect = surface.get_rect()
        surface.fill((170, 170, 170))
        surface.blit(font.render('Загрузка...', 1, 'black', ), (0, 0))

        self.display_surface.blit(self.backgrounds[random.randint(0, 3)], (0, 0))
        self.display_surface.blit(surface, (screen_width / 2 - rect.centerx, screen_height / 2 - rect.centery))

        self.time += 1
        if self.time > 1:
            self.create_level(self.level)