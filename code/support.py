from csv import reader
from os import walk
import pygame
from os import listdir
from os.path import isfile, join

def load_sprite_sheets(character, path, x, y, width, height):

	images = [f for f in listdir(path) if isfile(join(path, f))]

	character.animations = {}

	for image in images:
		sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

		sprites = []
		for i in range(sprite_sheet.get_width() // 150):
			surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
			# surface.fill((90, 90, 90))
			rect = pygame.Rect((i + 1) * 150 - x, y, width, height)
			surface.blit(sprite_sheet, (0, 0), rect)
			sprites.append(pygame.transform.scale2x(surface))

		character.animations[image.replace(".png", "")] = sprites

def import_folder(path):
	surface_list = []

	for _,__,image_files in walk(path):
		for image in image_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_list.append(image_surf)

	return surface_list

def import_csv_layout(path):
	terrain_map = []
	with open(path) as map:
		level = reader(map,delimiter = ',')
		for row in level:
			terrain_map.append(list(row))
		return terrain_map

def import_cut_graphics(path, tile_size):
	surface = pygame.image.load(path).convert_alpha()
	tile_num_x = int(surface.get_size()[0] / tile_size)
	tile_num_y = int(surface.get_size()[1] / tile_size)

	cut_tiles = []
	for row in range(tile_num_y):
		for col in range(tile_num_x):
			x = col * tile_size
			y = row * tile_size
			new_surf = pygame.Surface((tile_size,tile_size),flags = pygame.SRCALPHA)
			new_surf.blit(surface,(0,0),pygame.Rect(x,y,tile_size,tile_size))
			cut_tiles.append(new_surf)

	return cut_tiles
