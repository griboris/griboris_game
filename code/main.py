import pygame, sys
from game_data import screen_width, screen_height
from facesplaces import LevelMap, Download
from level import Level


class Game:
	def __init__(self):
		self.max_level = 1
		self.overworld = LevelMap(1, self.max_level, screen, self.create_download)
		self.status = 'overworld'

	def create_level(self, current_level):
		self.level = Level(current_level, screen, self.create_overworld)
		self.status = 'level'

	def create_overworld(self, current_level, new_max_level):
		self.max_level = max(self.max_level, new_max_level)
		self.overworld = LevelMap(current_level, self.max_level, screen, self.create_download)
		self.status = 'overworld'

	def create_download(self, current_level):
		self.status = 'download'
		self.download = Download(current_level, screen, self.create_level)

	def run(self):
		if self.status == 'overworld':
			self.overworld.run()
		elif self.status == 'download':
			self.download.run()
		else:
			self.level.run()


# Pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Игра Грибунова Бориса")
clock = pygame.time.Clock()
game = Game()

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
	
	screen.fill((40, 40, 40))
	game.run()

	pygame.display.update()
	clock.tick(60)