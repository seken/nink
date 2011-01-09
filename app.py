#!/usr/bin/python
from __future__ import with_statement
from contextlib import nested
import pyglet
from pyglet.window import key
from pyglet.gl import *
import math
from gletools import ShaderProgram, Sampler2D, Matrix, Texture, VBO
from pyglet.window import key
from ctypes import c_float
import random
import csv, os
from ground import Ground
from walls import Walls
from vector import Vector
from protagonist import Protagonist
from friendly import Friendly
from enemy import Enemy
from gold import Gold
from arrow import Arrow

def clamp(start, end, value):
	'''
	Clamp the value and position it between 0 and 1
	'''
	fv = float(min(max(value, start), end))
	return (fv - start)/(end - start)

def clamp2(start, end, value, cstart, cend):
	return (clamp(start, end, value) * (cend - cstart)) + cstart
	
def wclamp(start, end, value):
	fv = float(value - start)/(end - start)
	if fv < -0.125 or fv > 1.125:
		return 0
	elif fv < 0.125:
		return 1 - ((math.cos(4*math.pi*fv + math.pi/2)+1)/2)
	elif fv > 0.875:
		return 1 - ((math.cos(4*math.pi*fv - math.pi/2)+1)/2)
	else:
		return 1
		
def gaus2d(xc, yc, xs, ys, x, y):
	i=math.pow(x-xc,2)/(2*math.pow(xs,2))
	j=math.pow(y-yc,2)/(2*math.pow(ys,2))
	return math.pow(math.e, -(i+j))
						
class Application(pyglet.window.Window):
	def __init__(self, map_name):
		super(Application, self).__init__(resizable=True, width=512, height=512, caption='Nink saves the town')
		
		# Start screen
		menuImage = pyglet.image.load('images/start.png')
		self.menuTexture = Texture(menuImage.width, menuImage.height, unit=GL_TEXTURE0, data=menuImage.get_data('RGBA', menuImage.width*4))
		menuImage = pyglet.image.load('images/husb_death.png')
		self.husbTexture = Texture(menuImage.width, menuImage.height, unit=GL_TEXTURE0, data=menuImage.get_data('RGBA', menuImage.width*4))
		menuImage = pyglet.image.load('images/nink_death.png')
		self.ninkTexture = Texture(menuImage.width, menuImage.height, unit=GL_TEXTURE0, data=menuImage.get_data('RGBA', menuImage.width*4))
		menuImage = pyglet.image.load('images/win.png')
		self.winTexture = Texture(menuImage.width, menuImage.height, unit=GL_TEXTURE0, data=menuImage.get_data('RGBA', menuImage.width*4))
		with nested(self.menuTexture):
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		with nested(self.husbTexture):
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		with nested(self.ninkTexture):
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		with nested(self.winTexture):
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		self.make_menu_mesh()
	
		# Sounds
		self.bg_music = pyglet.media.load('sound/TIGshot.mp3')
		self.win_sound = pyglet.media.load('sound/win.wav')
		self.hurt_sound = pyglet.media.StaticSource(pyglet.media.load('sound/hurt.wav'))
		self.pickup_sound = pyglet.media.StaticSource(pyglet.media.load('sound/pickup.wav'))
		self.arrow_sound = pyglet.media.StaticSource(pyglet.media.load('sound/arrow.wav'))
		self.death_sound = pyglet.media.StaticSource(pyglet.media.load('sound/death.wav'))
		self.goblin_death_sound = pyglet.media.StaticSource(pyglet.media.load('sound/goblin_death.wav'))
		self.follow_sound = pyglet.media.StaticSource(pyglet.media.load('sound/follow.wav'))
		
		self.scale = 96/2
		self.time = 0
		self.game = 0
		self.camera = Matrix()
		self.camera = self.camera.translate(0, -5, -10)
		self.program = ShaderProgram.open('shaders/main.shader')
		self.program.vars.tex = Sampler2D(GL_TEXTURE0)
		self.characters = pyglet.image.ImageGrid(pyglet.image.load('images/char.png'),16,31, 8, 8)
		
		# Map
		mapimg = pyglet.image.load('map/'+map_name+'.png')
		self.ground = self.create_ground(mapimg)
		self.walls = self.create_walls(mapimg)
		
		# Normal Mesh
		position = [
			-0.5, -0.5, 0,
			-0.5, 0.5, 0,
			0.5, 0.5, 0,
			0.5, -0.5, 0,
		]
		texCoord = [
			0, 0,
			0, 1,
			1, 1,
			1, 0,
		]
		normal = [
			0, 0, 1,
			0, 0, 1,
			0, 0, 1,
			0, 0, 1,
		]
		position = (c_float*len(position))(*position)
		texCoord = (c_float*len(texCoord))(*texCoord)
		normal = (c_float*len(normal))(*normal)
		self.normal_mesh = VBO(4,
			position_3=position,
			texCoord_2=texCoord,
			normal_3=normal)
		# Gold Mesh
		position = [
			-0.25, -0.25, 0,
			-0.25, 0.25, 0,
			0.25, 0.25, 0,
			0.25, -0.25, 0,
		]
		texCoord = [
			0, 0,
			0, 1,
			1, 1,
			1, 0,
		]
		normal = [
			0, 0, 1,
			0, 0, 1,
			0, 0, 1,
			0, 0, 1,
		]
		position = (c_float*len(position))(*position)
		texCoord = (c_float*len(texCoord))(*texCoord)
		normal = (c_float*len(normal))(*normal)
		self.gold_mesh = VBO(4,
			position_3=position,
			texCoord_2=texCoord,
			normal_3=normal)
		
		# Friend texture
		character = pyglet.image.load('images/others.png')
		self.friendTex = Texture(character.width, character.height, data=character.get_data('RGBA', character.width*4))
		
		# Gold texture
		gold = pyglet.image.load('images/gold.png')
		self.goldTex = Texture(gold.width, gold.height, data=gold.get_data('RGBA', gold.width*4))
		
		# Arrow texture
		arrow = pyglet.image.load('images/arrow.png')
		self.arrowTex = Texture(arrow.width, arrow.height, data=arrow.get_data('RGBA', arrow.width*4))
		
		# Game state
		self.arrows = []
		self.enemy = []
		self.friendly = []	
		self.gold = []
			
		# Datapoints
		points = csv.reader(open('map/'+map_name+'.txt', 'rb'), delimiter=',')
		for row in points:
			point = (((float(row[1])+0.5)/mapimg.width * self.scale*2) - self.scale, ((float(row[2])-0.5)/mapimg.width * self.scale*2) - self.scale)
			if row[0] == 'start':
				self.start_point = Vector(point[0], 0, point[1])
				self.player = self.create_protagonist(self.walls.collisionMap, point)
			elif row[0] == 'husband':
				h = self.create_husband(self.walls.collisionMap, point)
				h.husband = True
				self.friendly.append(h)
				self.husband = h
			elif row[0] == 'friend':
				self.friendly.append(self.create_friend(self.walls.collisionMap, point, self.friendTex))
			elif row[0] == 'gold':
				self.gold.append(self.create_gold(self.walls.collisionMap, point))
			elif row[0] == 'enemy':
				self.enemy.append(self.create_enemy(self.walls.collisionMap, point))
				
		pyglet.clock.schedule_interval(lambda x: self.on_update(x), 1.0/60.0)
		glEnable(GL_DEPTH_TEST)
		glDepthFunc(GL_LEQUAL)
		glEnable(GL_BLEND);
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
		self.keys = key.KeyStateHandler()
		self.push_handlers(self.keys)
		
	def create_husband(self, collision_map, position):
		character = pyglet.image.load('images/husband.png')
		character = Texture(character.width, character.height, data=character.get_data('RGBA', character.width*4))
		return Friendly(character, self.program, 1, 1, position, collision_map, self.normal_mesh)
		
	def create_friend(self, collision_map, position, texture):
		character = pyglet.image.load('images/others.png')
		character = Texture(character.width, character.height, data=character.get_data('RGBA', character.width*4))
		return Friendly(character, self.program, 1, 1, position, collision_map, self.normal_mesh)
		
	def create_gold(self, collision_map, position):
		gold = Gold(self.goldTex, self.program, 0.5, 0.5, position, collision_map, self.gold_mesh)
		return gold
		
	def create_enemy(self, collision_map, position):
		character = pyglet.image.load('images/enemy.png')
		character = Texture(character.width, character.height, data=character.get_data('RGBA', character.width*4))
		return Enemy(character, self.program, 1, 1, position, collision_map, self.normal_mesh)
		
	def create_ground(self, mapimg):
		gmap = mapimg
		gtex = Texture(gmap.width, gmap.height, unit=GL_TEXTURE0, data=gmap.get_data('RGBA', gmap.width*4))
		tiles = pyglet.image.load('images/groundandwalltiles.png')
		ttex = Texture(tiles.width, tiles.height, unit=GL_TEXTURE1, data=tiles.get_data('RGBA', tiles.width*4))
		tdim = Vector(tiles.width/8, tiles.height/8, 64-8)
		
		g = Ground(gtex, ttex, tdim, Vector(gmap.width, gmap.height, 0), Vector(-self.scale, -self.scale, 0), Vector(self.scale, self.scale, 0))
		return g
		
	def create_walls(self, mapimg):
		gmap = mapimg
		gtex = Texture(gmap.width, gmap.height, unit=GL_TEXTURE0, data=gmap.get_data('RGBA', gmap.width*4))
		tiles = pyglet.image.load('images/groundandwalltiles.png')
		ttex = Texture(tiles.width, tiles.height, unit=GL_TEXTURE1, data=tiles.get_data('RGBA', tiles.width*4))
		tdim = Vector(tiles.width/8, tiles.height/8, 64-8)
		
		w = Walls(gtex, ttex, tdim, Vector(gmap.width, gmap.height, 0), Vector(-self.scale, -self.scale, 0), Vector(self.scale, self.scale, 0))
		return w
		
	def create_protagonist(self, collisionMap, position):
		character = pyglet.image.load('images/nink.png')
		character = Texture(character.width, character.height, data=character.get_data('RGBA', character.width*4))
		return Protagonist(character, self.program, 1, 1, position, collisionMap, self.normal_mesh)
		
	def on_update(self, delta):
		
		self.time+= delta
		
		if self.keys[key.D]:
			self.player.move(Vector(2.5, 0, 0)*delta)
		if self.keys[key.A]:
			self.player.move(Vector(-2.5, 0, 0)*delta)
		if self.keys[key.W]:
			self.player.turn(-0.01)
		if self.keys[key.S]:
			self.player.turn(0.01)
		if self.keys[key.SPACE]:
			self.fire_arrow(self.player)
		if self.keys[key.M]:
			self.poke_friends()
			
		if self.game == 1:
			self.player.update(delta, self)
			self.update_camera()
			
			# Update and remove dead arrows
			arrow_delete = []
			for i in self.arrows:
				if not i.update(delta, self):
					arrow_delete.append(i)
			
			map(self.arrows.remove, arrow_delete)
			
			# Update friends
			map(lambda i : i.update(delta, self), self.friendly)
				
			# Update enemy
			map(lambda i : i.update(delta, self), self.enemy)
			
			# Update gold
			gold_delete = []
			for i in self.gold:
				if i.value == 0:
					gold_delete.append(i)
			map(self.gold.remove, gold_delete)
				
			# Collision Test
			self.test_arrows()
				
			# End condition tests
			if self.husband.health < 0:
				self.death_sound.play()
				self.bg_music.pause()
				self.game = 2
			if self.player.health < 0:
				self.death_sound.play()
				self.bg_music.pause()
				self.game = 3
			
			# Win condition
			distanceToSteps = (self.player.position - self.start_point) + (self.husband.position - self.start_point)
			if distanceToSteps.len() < 4:
				self.game = 4
				self.bg_music.pause()
				self.win_sound.play()
			
				
	def poke_friends(self):
		if self.player.cooldown < 0:
			self.player.cooldown = 0.75
			self.follow_sound.play()
			for i in self.friendly:
				i.poked()
	
	def fire_arrow(self, person):
		if person.cooldown < 0:
			person.cooldown = 0.75
			self.arrow_sound.play()
			position = (person.position.x, person.position.z)
			arrow = Arrow(self.arrowTex, self.program, 1, 1, position, person.collisionMap, self.normal_mesh)
			arrow.point(person.angle)
			self.arrows.append(arrow)
	
	def test_arrows(self):
		hit_enemies = []
		hit_arrows = []
		for a in self.arrows:
			for e in self.enemy:
				if (a.position - e.position).len() < e.x/2:
					hit_enemies.append(e)
					hit_arrows.append(a)
					self.goblin_death_sound.play()
					break
		remove = self.enemy.remove
		map(remove, hit_enemies)
		remove = self.arrows.remove
		map(remove, hit_arrows)
	
	def on_draw(self):
		self.clear()
		
		if self.game == 1:
			light = random.random()
			self.ground.draw(self.projection, self.camera, self.player.position, light)
			self.walls.draw(self.projection, self.camera, self.player.position, light)
			
			transparency = self.arrows + self.friendly + self.enemy + self.gold + [self.player]
			transparency.sort(key=lambda item:item.depth(self.projection * self.camera))
			
			for i in transparency:
				i.draw(self.projection, self.camera, self.player.position, light)
		else:
			self.draw_menu(self.game)
	
	def draw_menu(self, mode):
		# Menu
		self.program.vars.mvp = Matrix()
		self.program.vars.modelview = Matrix()
		self.program.vars.playerPosition = (0.0, 0.0, 0.0)
		self.program.vars.playerLight = random.random()*0.1 + 0.9
		
		tex = 0
		if mode == 0:
			tex = self.menuTexture
		elif mode == 2:
			tex = self.husbTexture
		elif mode == 3:
			tex = self.ninkTexture
		else:
			tex = self.winTexture
			
		with nested(self.program, tex):
			self.menu_mesh.draw(GL_QUADS)
	
	def make_menu_mesh(self):
		position = [
			-1, -1, 0,
			-1, 1, 0,
			1, 1, 0,
			1, -1, 0,
		]
		texCoord = [
			0, 0,
			0, 1,
			1, 1,
			1, 0,
		]
		normal = [
			0, 0, 1,
			0, 0, 1,
			0, 0, 1,
			0, 0, 1,
		]
		position = (c_float*len(position))(*position)
		texCoord = (c_float*len(texCoord))(*texCoord)
		normal = (c_float*len(normal))(*normal)
		self.menu_mesh = VBO(4,
			position_3=position,
			texCoord_2=texCoord,
			normal_3=normal)
	
	def update_camera(self):
		pPos = self.player.position
		self.camera = Matrix().rotatex(0.07) * Matrix().rotatey(self.player.angle) * Matrix().translate(-pPos.x, -pPos.y, -pPos.z) * Matrix().translate(-6*math.sin(-self.player.angle*2*math.pi), -3, -6*math.cos(-self.player.angle*2*math.pi))
	
	def on_key_press(self, symbol, modifiers):
		if symbol == key.ENTER:
			if self.game == 0:
				self.game = 1
				self.bg_music = self.bg_music.play()
			elif self.game == 2 or self.game == 3 or self.game == 4:
				exit()
		elif symbol == key.ESCAPE or symbol == key.Q:
			exit()
				
	def on_mouse_motion(self, x, y, dx, dy):
		return pyglet.event.EVENT_HANDLED
		
	def on_mouse_press(self, px, py, button, modifiers):
		x = float(px)/(self.width/2) -1
		y = float(py)/(self.height/2) -1
		if self.game:
			pass
		return pyglet.event.EVENT_HANDLED

	def on_mouse_release(self, x, y, button, modifiers):
	    return pyglet.event.EVENT_HANDLED
	
	def on_mouse_drag(self, px, py, dx, dy, buttons, modifiers):
		x = float(px)/(self.width/2) -1
		y = float(py)/(self.height/2) -1
		if self.game:
			pass
		return pyglet.event.EVENT_HANDLED
		
	def on_resize(self, width, height):
		# Override the default on_resize handler to create a 3D projection
		self.projection = Matrix.perspective(width, height, 60, 0.1, 1000)
		glViewport(0, 0, width, height)
		glClearColor(0,0,0, 255)
		return pyglet.event.EVENT_HANDLED

if __name__ == '__main__':
	window = Application('ground5')
	pyglet.app.run()