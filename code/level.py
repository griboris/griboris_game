import pygame
from support import import_csv_layout, import_cut_graphics
from tiles import StaticTile, Furniture, Tile
from enemies import Enemy
from player import Player
from particles import SplashesEffect
from game_data import levels, screen_height, screen_width
from hit_points import HP
import math

class Level:
    def __init__(self, current_level, surface, create_overworld):
        # general setup
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.level_data = level_data

        self.tile_size = self.level_data['tile_size']
        self.level_width = self.level_data['level_width']
        self.level_height = self.level_data['level_height']

        self.new_max_level = self.level_data['unlock']
        self.create_overworld = create_overworld

        self.display_surface = surface
        self.world_shift = pygame.math.Vector2(0, 0)

        self.hp = pygame.sprite.Group()
        # цель, конец уровня
        self.goal = pygame.sprite.Group()

        # player
        player_layout = import_csv_layout(self.level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        # всплески при передвижении
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # фон
        self.bg_image = pygame.image.load(self.level_data['bg_image']).convert_alpha()
        self.bg_rect = self.bg_image.get_rect(topleft=(0, 0))

        # terrain setup
        terrain_layout = import_csv_layout(self.level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

        # furniture
        furniture_layout = import_csv_layout(self.level_data['furniture'])
        self.furniture_sprites = self.create_tile_group(furniture_layout, 'furniture')

        # enemy
        enemy_layout = import_csv_layout(level_data['enemy'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemy')

        # constraint
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraints')

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.create_overworld(self.current_level, 0)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * self.tile_size
                    y = row_index * self.tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('../graphics/terrain/Assets.png', self.tile_size)
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(self.tile_size, x, y, tile_surface)

                    if type == 'furniture':
                        terrain_tile_list = import_cut_graphics('../graphics/terrain/Assets.png', self.tile_size)
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = Furniture(self.tile_size, x, y, tile_surface)

                    if type == 'constraints':
                        sprite = Tile(self.tile_size, x, y)

                    if type == 'enemy':
                        sprite = Enemy(self.tile_size, x, y, 3, '../graphics/Monsters_Creatures_Fantasy/Skeleton')
                        hp = HP(sprite)
                        self.hp.add(hp)

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size
                if val == '0':
                    sprite = Player((x, y), self.display_surface, self.create_jump_splashes)
                    self.player.add(sprite)
                    hp = HP(sprite)
                    self.hp.add(hp)

                if val >= '1':
                    sprite = Tile(self.tile_size, x, y)
                    self.goal.add(sprite)

    # разворот npc при столкновении с границами(constraints)
    def npc_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            for border in self.constraint_sprites.sprites():
                offset_x = border.rect.x - enemy.rect.x
                offset_y = border.rect.y - enemy.rect.y
                if enemy.mask.overlap_area(border.mask, (offset_x, offset_y)):
                    enemy.reverse()

    def create_jump_splashes(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)
        jump_particle_sprite = SplashesEffect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        # окончание уровня
        for sprite in self.goal.sprites():
            if sprite.rect.colliderect(player.rect):
                if len(self.enemy_sprites.sprites()) < 1:
                    self.create_overworld(self.current_level, self.level_data['unlock'])

        collidable_sprites = (self.terrain_sprites.sprites()
                              + self.furniture_sprites.sprites()
                              + self.enemy_sprites.sprites())

        for sprite in collidable_sprites:
            offset_x = sprite.rect.x - player.rect.x
            offset_y = sprite.rect.y - player.rect.y
            # offset_x = player.rect.x - sprite.rect.x
            # offset_y = player.rect.y - sprite.rect.y
            if player.mask.overlap_area(sprite.mask, (offset_x, offset_y)):
                if player.direction.x < 0:
                    # player.rect.left = sprite.rect.right
                    # player.rect.left = sprite.rect.right - player.mask.overlap(sprite.mask, (offset_x, offset_y))[0]
                    player.rect.x += player.speed
                    player.direction.x *= -1
                    # player.direction.x = 0
                    player.on_left = True
                elif player.direction.x > 0:
                    # player.rect.right = sprite.rect.left - player.mask.overlap(sprite.mask, (offset_x, offset_y))[0]
                    player.rect.x -= player.speed
                    player.direction.x *= -1
                    # player.direction.x = 0
                    player.on_right = True

        for enemy in self.enemy_sprites.sprites():
            offset_x = sprite.rect.x - player.rect.x + 10*enemy.direction
            offset_y = sprite.rect.y - player.rect.y
            if player.mask.overlap_area(sprite.mask, (offset_x, offset_y)):
                if (player.facing_right and enemy.direction == -1) or (not player.facing_right and enemy.direction == 1):
                    enemy.attack = True

            offset_x = sprite.rect.x - player.rect.x

            if player.battle_mask.overlap_area(sprite.battle_mask, (offset_x, offset_y)):
                if enemy.attack:
                    if enemy.frame_index > len(enemy.animations[enemy.status])-2.5:
                        player.take_hit = True
                if player.attack:
                    if player.frame_index > len(player.animations[player.status])-2:
                        enemy.take_hit = True

            if math.ceil(enemy.frame_index) == len(enemy.animations[enemy.status]):
                if player.take_hit:
                    player.hit_points -= 1
                    player.take_hit = False

            if math.ceil(player.frame_index) == len(player.animations[player.status]):
                if enemy.take_hit:
                    enemy.hit_points -= 1
                    enemy.take_hit = False


        if player.on_left and player.direction.x >= 0:
            player.on_left = False
        if player.on_right and player.direction.x <= 0:
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        collidable_sprites = (self.terrain_sprites.sprites()
                              + self.furniture_sprites.sprites())

        for sprite in self.goal.sprites():
            if sprite.rect.colliderect(player.rect):
                if len(self.enemy_sprites.sprites()) < 1:
                    self.create_overworld(self.current_level, self.level_data['unlock'])

        for sprite in collidable_sprites:
            # offset_x = sprite.rect.x - player.rect.x
            # offset_y = sprite.rect.y - player.rect.y
            offset_x = player.rect.x - sprite.rect.x
            offset_y = player.rect.y - sprite.rect.y
            if sprite.mask.overlap(player.mask, (offset_x, offset_y)):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top + sprite.mask.overlap(player.mask, (offset_x, offset_y))[1]
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom + sprite.mask.overlap(player.mask, (offset_x, offset_y))[1]
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0.1:
            player.on_ceiling = False

    # прокрутка экрана, смещение всех объектов на нём
    def scroll(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        player_y = player.rect.centery
        direction_x = player.direction.x
        direction_y = player.direction.y

        if player_x < screen_width / 4 < player.left and direction_x < 0:
            player.speed = 0
            self.world_shift.x = 8
        elif (player_x > screen_width - (screen_width / 4) and direction_x > 0
              and player.right < self.level_width - (screen_width / 4)):
            self.world_shift.x = -8
            player.speed = 0
        else:
            self.world_shift.x = 0
            player.speed = 8

        if ((player_y <= screen_height / 4 <= player.top and direction_y < 0)
                or (player_y >= screen_height - (screen_height / 3) and player.bottom <= self.level_height - (
                        screen_height / 3) and direction_y > 0)):
            player.rect.y -= direction_y
            self.world_shift.y = -direction_y
        else:
            self.world_shift.y = 0

        if not (0 <= self.player.sprite.rect.bottom <= screen_height):
            self.world_shift.y = -10

        player.level_pos -= self.world_shift

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = SplashesEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def death_check(self):
        player = self.player.sprite
        for enemy in self.enemy_sprites.sprites():
            if player.hit_points <= 0:
                enemy.speed = 0
                enemy.animation_speed = 0.1
                enemy.status = 'Idle'
                player.animation_speed = 0.04
                if math.ceil(player.frame_index) == len(player.animations[player.status]):
                    self.create_overworld(self.current_level, 0)

            if enemy.hit_points <= 0:
                if enemy.status == 'Death':
                    enemy.animation_speed = 0.04
                    if math.ceil(enemy.frame_index) == len(enemy.animations[enemy.status]):
                        enemy.kill()


    def run(self):
        self.input()

        self.bg_rect.x += self.world_shift.x
        self.bg_rect.y += self.world_shift.y

        font = pygame.font.SysFont('arial', 32)
        self.bg_image.blit(font.render(self.level_data['text'], 1, 'white'), (200, self.bg_rect.height - 500))

        self.display_surface.blit(self.bg_image, self.bg_rect)

        # terrain
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        # furniture
        self.furniture_sprites.update(self.world_shift)
        self.furniture_sprites.draw(self.display_surface)

        # constraint
        self.constraint_sprites.update(self.world_shift)

        #npc
        self.enemy_sprites.update(self.world_shift, 3)
        self.enemy_sprites.draw(self.display_surface)
        self.npc_collision_reverse()
        self.death_check()

        # dust particles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # player sprites
        self.player.update()
        self.horizontal_movement_collision()

        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()

        self.scroll()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)

        self.hp.update()
        self.hp.draw(self.display_surface)