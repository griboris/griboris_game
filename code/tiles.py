import pygame 
from support import import_folder

class Tile(pygame.sprite.Sprite):
	def __init__(self,size,x,y):
		super().__init__()
		self.image = pygame.Surface((size,size))
		# self.image.fill((255, 255, 255))
		self.rect = self.image.get_rect(topleft=(x,y))

		self.mask = pygame.mask.from_surface(self.image)

	def update(self,shift):
		self.rect.x += shift.x
		self.rect.y += shift.y

class StaticTile(Tile):
	def __init__(self,size,x,y,surface):
		super().__init__(size,x,y)
		self.image = surface
		self.mask = pygame.mask.from_surface(surface)

	def update(self,shift):
		self.rect.x += shift.x
		self.rect.y += shift.y

class Furniture(StaticTile):
	def __init__(self,size,x,y, surface):
		super().__init__(size,x,y,surface)

		self.image.set_alpha(0)

	def update(self,shift):
		self.rect.x += shift.x
		self.rect.y += shift.y


class AnimatedTile(Tile):
	def __init__(self,size,x,y,path):
		super().__init__(size,x,y)
		self.frames = import_folder(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]

	def animate(self):
		self.frame_index += 0.15
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def update(self,shift):
		self.animate()
		self.rect.x += shift.x
		self.rect.y += shift.y