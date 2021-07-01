import pygame
import os
import button

pygame.init()

#ESTE SERA EL TAMAÑO DE NUESTRA VENTANA 
SCREEN_WIDTH = 600
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('KILL THE MONO BETA')

#SELECCIONAMOS LA LATENCIA DE LOS FRAMES POR SEGUNDO QUE QUEREMOS
clock = pygame.time.Clock()
FPS = 60


#LAS VARIABLES GLOBALES DE NUESTO CODIGO SE ENCUENTRAN DEFINIDAS EN LAS SIGUIENTES LINEAS, ESTAS NMOS AYUDARAN A 
#RETOMARLAS CUANDO LAS OCUPEMOS
GRAVITY = 0.40

ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21


#LAS VARIABLES DE ESTADO DEL JUGADOR Y DEL JUEGO
moving_left = False
moving_right = False
shoot = False
start_game=False #LO INICIAMOS EN FALSE PARA QUE NJO SE INICIE HASTA QUE LO INDIQUEMOS EN EL MENU


#EN ESTE FRAGMENTO ESTAREMOS CARGANDO TODAS LAS IMAGENES QUE VAMOS A ESTAR OCUPANDO
#BackGround
menu_img=pygame.image.load('Backgrounds\\4.png').convert_alpha()
library_img=pygame.image.load('Backgrounds\\1.png').convert_alpha()
mountain_img=pygame.image.load('Backgrounds\\0.png').convert_alpha()
#botones
start_img=pygame.image.load('Buttons\\1.png').convert_alpha()
exit_img=pygame.image.load('Buttons\\0.png').convert_alpha()
#AMMO
bullet_img = pygame.image.load('distance_damage\\0.png').convert_alpha()
health_box_img = pygame.image.load('Banners\\0.png').convert_alpha()
#OBJETOS
ammo_box_img = pygame.image.load('Banners\\2.png').convert_alpha()
item_boxes={
	'Health': health_box_img,
	'Ammo' 	: ammo_box_img
}


#CARGAMOS LOS FONDOS DEL MENU Y DE LA VENTANA DEL JUEGO 
def draw_bg():
	screen.blit(library_img,(0,0))
	screen.blit(mountain_img,(0,300))

#CLASE DEL CABALLERO 
class Caballero(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True			#ESTA VIVO
		self.char_type = char_type	#NOMBRE DEL MODELO
		self.speed = speed				
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		
		#CARGAMOS LAS IMAGENES DE LOS PERSONAJES
		#
		#EJEMPLO DE RUTA:C:\Users\Behendolrf\Desktop\UNIVERSIDAD\PYTHON\\Archangel_Male\sword_idle
		
		animation_types = ['idle', 'run', 'sword_idle','dead']
		for animation in animation_types:
			#RESET DE LA LISTA TEMPORAL
			temp_list = []
			#CONTADOR PARA NAVEGAR EN LOS ARCHIVOS
			num_of_frames = len(os.listdir(f'{self.char_type}\\{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'{self.char_type}\\{animation}\\{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)


	def update(self):
		self.update_animation()
		self.check_alive()
		#COOLDOWN DEL DISPARO
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right):
		#RESETEO DE LAS VARIABLES DE MOVIMIENTO 
		dx = 0
		dy = 0
	

		#GENERAMOS LAS VARIABLES DE MOVIMIENTO PARA VERIFICAR A DONDE SE MUEVE 
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		#SALTAR
		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True

		#FORMULA DE GRAVEDAD
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#COLISION CON EL SUELO 
		if self.rect.bottom + dy > 300:
			dy = 300 - self.rect.bottom
			self.in_air = False

		#ACTUALIZAMOS LA POSICION DEL SPRITE
		self.rect.x += dx
		self.rect.y += dy



	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			#reduce ammo
			self.ammo -= 1


	def update_animation(self):
		#ANIMACION ACTUALIZADA
		ANIMATION_COOLDOWN = 100
		#ACTUALIZAR SPRITE DEPENDIENDO DE EN EL QUE ESTA
		self.image = self.animation_list[self.action][self.frame_index]
		#VERIFICAR CUANTO TIEMPO PASO DEL ANTERIOR FRAME
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#CICLAR LÑA ANIMACION VIENDO SI ESTA VOLVIO A INDICE 0
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0



	def update_action(self, new_action):

		if new_action != self.action:
			self.action = new_action
			#ACTUALIZAR TODOS LOS SPRITES
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()



	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
#CLASE DE LOS OBJETOS
class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


	def update(self):
		#VERIFICAR SI EL JUGADOR RECOJIO ALGUN OBJETO
		if pygame.sprite.collide_rect(self, player):
			#VER QUE TIPO DE OBJETO ERA
			if self.item_type == 'Health':
				print(player.health)
				player.health += 25
				print(player.health)
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				print(player.ammo)
				player.ammo += 15
				print(player.ammo)

			#BORRAR EL OBJETO
			self.kill()
#CLASE DE  LA  MUNICION 
class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#move bullet
		self.rect.x += (self.direction * self.speed)
		#check if bullet has gone off screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()

		#check collision with characters

		if pygame.sprite.spritecollide(enemy, bullet_group, False):
			if enemy.alive:
				enemy.health -= 25
				self.kill()

#CREAMOS LOS BOTONES DEL MENU


start_button=button.Button(SCREEN_WIDTH//3-110,SCREEN_HEIGHT//2-100,start_img,2)
exit_button=button.Button(SCREEN_WIDTH//3-110,SCREEN_HEIGHT//2+80,exit_img,2)
#GRUPOS DE SPRITE: ESTOS SON CREADOS PARA GENERAR TODOS LOS SPRITES SIMILARES QUE TENEMOS QUE CARGAR O QUE SE USAN 
# VARIAS VECES PERO TIENEN DIFERENTES CARACTERISTICAS, EN EL CASO DE LAS ITEM BOX SON PARA GENERAR LOS DIFERENTES 
# OBJETOS DE LA VIDA Y EL OTRO ES DE LA MUNUICION 

bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

#CREACION DE LOS OBJETOS
item_box= ItemBox('Health',100, 250)
item_box_group.add(item_box )
item_box2= ItemBox('Ammo',500, 250)
item_box_group.add(item_box2 )

 

player = Caballero('Archangel_Male', 200, 200, 3, 5, 20)

enemy = Caballero('Archdemon_Male', 400, 220, 3, 5, 20)


run = True
while run:

	clock.tick(FPS)
	if start_game==False:
		#MENU
		screen.blit(menu_img,(0,0))
		if start_button.draw(screen):
			start_game=True
		if exit_button.draw(screen):
			run=False
	else:
		draw_bg()

		player.update()
		player.draw()

		enemy.update()
		enemy.draw()

		#VAMOS ACTUALIZANDO LOS GRUPOS DE LOS SPRITES
		bullet_group.update()
		bullet_group.draw(screen)
		item_box_group.update()
		item_box_group.draw(screen)



		#ACCIONES DEL JUGADOR
		if player.alive:
			#DISPAROS
			if shoot:
				player.shoot()
			if player.in_air:
				player.update_action(2)#2: jump
			elif moving_left or moving_right:
				player.update_action(1)#1: run
			else:
				player.update_action(0)#0: idle
			player.move(moving_left, moving_right)
			 


	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#ENTRADAS DEL TECLADO 
		# EN ESTAS ENTRAN CUANDO SOLO PRESIONAS LA TECLA
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
			if event.key == pygame.K_ESCAPE:
				run = False


		#SALIDA DEL TECLADO: 
		#CUANDO LEVANTTAS DEL DEDO DE LA TECLA 
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False




	pygame.display.update()

pygame.quit()