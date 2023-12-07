import pygame 
from support import import_folder, load_sprite_sheets
import math

class Player(pygame.sprite.Sprite):
	def __init__(self,pos,surface,create_jump_particles):
		super().__init__()
		load_sprite_sheets(self, "../graphics/character/Huntress_Sprites", 120, 30, 100, 68)
		self.frame_index = 0
		self.animation_speed = 0.15
		self.image = self.animations['Idle'][self.frame_index]
		self.rect = self.image.get_rect(topleft=pos)
		
		# dust particles 
		self.import_dust_run_particles()
		self.dust_frame_index = 0
		self.dust_animation_speed = 0.15
		self.display_surface = surface
		self.create_jump_particles = create_jump_particles

		# player movement
		self.direction = pygame.math.Vector2(0,0)
		self.speed = 10
		self.gravity = 0.8013
		self.jump_speed = -16.3

		# player status
		self.status = 'Idle'
		self.facing_right = True
		self.on_ground = False
		self.on_ceiling = False
		self.on_left = False
		self.on_right = False

		#  чтобы scroll не выходил за размеры уровня, и не было пустот
		self.level_pos = pygame.math.Vector2(0,0)

		self.mask = pygame.mask.from_surface(self.image)
		self.battle_mask = pygame.mask.from_surface(self.image)

		self.attack = False
		self.space_pressed = False

		self.hit_points = 6
		self.take_hit = False

	def import_dust_run_particles(self):
		self.dust_run_particles = import_folder('../graphics/character/dust_particles/run')

	def animate(self):
		animation = self.animations[self.status]

		# loop over frame index
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		image = animation[int(self.frame_index)]

		if self.facing_right:
			self.image = image
		else:
			flipped_image = pygame.transform.flip(image,True,False)
			self.image = flipped_image

		# set the rect
		if self.on_ground and self.on_right:
			self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
		elif self.on_ground and self.on_left:
			self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
		elif self.on_ground:
			self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		elif self.on_ceiling and self.on_right:
			self.rect = self.image.get_rect(topright = self.rect.topright)
		elif self.on_ceiling and self.on_left:
			self.rect = self.image.get_rect(topleft = self.rect.topleft)
		elif self.on_ceiling:
			self.rect = self.image.get_rect(midtop = self.rect.midtop)

		self.battle_mask = pygame.mask.from_surface(self.image)

	def run_dust_animation(self):
		if self.status == 'Run' and self.on_ground:
			self.dust_frame_index += self.dust_animation_speed
			if self.dust_frame_index >= len(self.dust_run_particles):
				self.dust_frame_index = 0

			dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

			if self.facing_right:
				pos = self.rect.bottomleft - pygame.math.Vector2(6,10)
				self.display_surface.blit(dust_particle,pos)
			else:
				pos = self.rect.bottomright - pygame.math.Vector2(6,10)
				flipped_dust_particle = pygame.transform.flip(dust_particle,True,False)
				self.display_surface.blit(flipped_dust_particle,pos)

	def get_input(self):
		keys = pygame.key.get_pressed()

		if self.status != 'Death':
			if not keys[pygame.K_x] and not keys[pygame.K_c] and not keys[pygame.K_z]:
				self.space_pressed = False
			elif not self.space_pressed:
				self.attack = True
				self.direction.x = 0
				self.space_pressed = True
				if keys[pygame.K_x]:
					self.status = 'Attack1'
				if keys[pygame.K_c]:
					self.status = 'Attack2'
				if keys[pygame.K_z]:
					self.status = 'Attack3'

			if math.ceil(self.frame_index) == len(self.animations[self.status]) and self.attack:
				self.attack = False

			if not self.space_pressed:
				if keys[pygame.K_RIGHT]:
					self.direction.x = 1
					self.facing_right = True
				elif keys[pygame.K_LEFT]:
					self.direction.x = -1
					self.facing_right = False
				else:
					self.direction.x = 0

			if keys[pygame.K_UP] and self.on_ground:
				self.jump()
				self.create_jump_particles(self.rect.midbottom)

	def get_status(self):
		if self.hit_points <= 0:
			self.direction.x = 0
			self.status = 'Death'
		elif not self.attack:
			if self.direction.y < 0:
				self.status = 'Jump'
			elif self.direction.y > 1:
				self.status = 'Fall'
			else:
				if self.direction.x != 0:
					self.status = 'Run'
				else:
					self.status = 'Idle'


	def apply_gravity(self):
		self.direction.y += self.gravity
		self.rect.y += self.direction.y

	def jump(self):
		self.direction.y = self.jump_speed

	def update(self):
		self.left = self.rect.left + self.level_pos.x + 40
		self.right = self.rect.right + self.level_pos.x - 40
		self.top = self.rect.top + self.level_pos.y + 48
		self.bottom = self.rect.bottom + self.level_pos.y - 48

		self.get_input()
		self.get_status()
		self.animate()
		self.run_dust_animation()
		