import pygame
import math
from support import load_sprite_sheets


class Enemy(pygame.sprite.Sprite):
	def __init__(self, size, x, y, speed, path):
		super().__init__()
		load_sprite_sheets(self, path, 100, 31, 100, 70)
		self.frame_index = 0
		self.image = self.animations['Walk'][self.frame_index]
		self.rect = self.image.get_rect(bottomleft=(x-size, y+size))
		self.speed = speed
		self.direction = 1
		self.attack = False

		self.status = 'Walk'

		self.mask = pygame.mask.from_surface(self.image)
		self.battle_mask = pygame.mask.from_surface(self.image)

		self.hit_points = 6
		self.take_hit = False

		self.animation_speed = 0.15

	def animate(self):
		self.frame_index += self.animation_speed
		if self.frame_index >= len(self.animations[self.status]):
			self.frame_index = 0
		self.image = self.animations[self.status][int(self.frame_index)]

		self.battle_mask = pygame.mask.from_surface(self.image)

	def move(self):
		self.rect.x += self.direction * self.speed

	def reverse_image(self):
		if self.direction < 0:
			self.image = pygame.transform.flip(self.image,True,False)

	def reverse(self):
		self.direction *= -1
		self.rect.x += self.direction * 80

	def change_status(self, speed):
		if self.hit_points <= 0:
			self.speed = 0
			self.status = 'Death'
		elif self.attack:
			self.speed = 0
			self.status = 'Attack'
		else:
			self.speed = speed
			self.status = 'Walk'

		if math.ceil(self.frame_index) == len(self.animations[self.status]) and self.attack:
			self.attack = False



	def update(self, shift, speed):
		self.rect.x += shift.x
		self.rect.y += shift.y
		self.animate()
		self.change_status(speed)
		self.move()
		self.reverse_image()