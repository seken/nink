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

def dist(p1, p2):
	return math.sqrt(math.pow(p1[0]-p2[0], 2) + math.pow(p1[1]-p2[1], 2))
						
class Application(pyglet.window.Window):
	def __init__(self):
		super(Application, self).__init__(resizable=True)
		self.mapSize = 64
		self.mapTexture = Texture(self.mapSize, self.mapSize, data=[0,0,0,255]*(self.mapSize*self.mapSize))
		
		self.probContinue = 0.79
		self.minSquares = 10
		
		# keep away from start and friends (and gold)
		self.goblin_distance = 10
		
		# min distance from start
		self.husband_distance = 30
		
		# probability of placement
		self.prob_goblin = 0.1
		self.prob_friend = 0.1
		self.prob_gold = 0.1
		self.prob_king = 0.01
		self.prob_husband = 0.01
		
		self.new_map()
		
		self.program = ShaderProgram.open('shaders/main.shader')
		self.program.vars.tex = Sampler2D(GL_TEXTURE0)

	def on_draw(self):
		self.clear()
		
		with nested(self.program, self.mapTexture):
			self.program.vars.mvp = Matrix()
			self.program.vars.modelview = Matrix()
			self.program.vars.playerPosition = (0.0, 0.0, 0.0)
			self.program.vars.playerLight = 1.0
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
			VBO(4,
				position_3=position,
				texCoord_2=texCoord,
				normal_3=normal).draw(GL_QUADS)
	
	def save_map(self):
		tileId = float(255)/56
		halfId = float(255*2)/56
		
		for i in range(self.mapSize*self.mapSize):
			if self.mapTexture.buffer[i*4] == 255:
				self.mapTexture.buffer[i*4] = int(54*tileId + halfId)
				self.mapTexture.buffer[i*4 + 1] = 0
			elif self.mapTexture.buffer[i*4 + 1] == 255:
				self.mapTexture.buffer[i*4] = int(tileId*45 + halfId)
				self.mapTexture.buffer[i*4 + 1] = 0
			else:
				self.mapTexture.buffer[i*4 + 1] = int(tileId*47 + halfId)
		
		self.mapTexture.update()
		self.mapTexture.save('ground.png')
		
		p = open('points.txt', 'w')
		p.write('start, %d, %d\n'%(self.start_point[0], self.mapSize - self.start_point[1]))
		p.write('husband, %d, %d\n'%(self.husband[0], self.mapSize - self.husband[1]))
		if self.king_goblin != None:
			p.write('king, %d, %d\n'%(self.king_goblin[0], self.mapSize - self.king_goblin[1]))
		for i in self.friendly:
			p.write('friend, %d, %d\n'%(i[0], self.mapSize - i[1]))
		for i in self.gold:
			p.write('gold, %d, %d\n'%(i[0], self.mapSize - i[1]))
		for i in self.goblin:
			p.write('enemy, %d, %d\n'%(i[0], self.mapSize - i[1]))
		p.close()
	
	def new_map(self):
		
		for i in range(self.mapSize*self.mapSize):
			self.mapTexture.buffer[i*4] = 0
			self.mapTexture.buffer[i*4+1] = 0
			self.mapTexture.buffer[i*4+2] = 0
			self.mapTexture.buffer[i*4+3] = 255
		
		start_x = int((random.random()/2 + 0.25) * self.mapSize)
		start_y = int((random.random()/2 + 0.25) * self.mapSize)
		self.start_point = (start_x, start_y)
		
		self.friendly = []
		self.king_goblin = None
		self.goblin = []
		self.gold = []
		self.husband = None
		
		self.mapTexture.buffer[(start_y * self.mapSize + start_x) * 4] = 255
		
		#idea from http://properundead.com/2009/03/cave-generator.html
		points = [(start_x, start_y)]
		squares = 0
		
		while len(points) > 0:
			point = points[0]
			points = points[1:]
			
			if point[0] < 1 or point[0] >= self.mapSize-1:
				continue
			if point[1] < 1 or point[1] >= self.mapSize-1:
				continue
			
			if self.can_add(point):
				self.add_point(point)
				if random.random() < self.probContinue or squares < self.minSquares:
					r2 = int(random.random() * 4) + 1
					x = [0, 1, 2, 3]
					random.shuffle(x)
					
					for i in range(r2):
						if x[i] == 0:
							points.append((point[0]-1, point[1]))
						elif x[i] == 1:
							points.append((point[0]+1, point[1]))
						elif x[i] == 2:
							points.append((point[0], point[1]-1))
						elif x[i] == 3:
							points.append((point[0], point[1]+1))
				squares += 1
		
		# Prune unconnected		
		for y in range(self.mapSize):
			for x in range(self.mapSize):
				if x < 1 or x >= self.mapSize - 1:
					continue
				if y < 1 or y >= self.mapSize - 1:
					continue
				if start_x == x and start_y == y:
					continue
					
				if not self.can_add((x, y)):
					continue

				if (not self.can_add((x+1, y))) and (not self.can_add((x-1, y))) and (not self.can_add((x, y+1))) and (not self.can_add((x, y-1))):
					self.add_point((x, y))
		
		self.add_husband()
		for y in range(self.mapSize):
			for x in range(self.mapSize):
				if not self.can_add((x,y)):
					self.add_gold((x,y))
					self.add_goblin((x,y))
					self.add_goblin_king((x,y))
					self.add_friend((x,y))

		print 'goblins: %s'%(len(self.goblin))
		print 'friendly: %s'%(len(self.friendly))
		print 'gold: %s'%(len(self.gold))
		
		self.mapTexture.update()
		with nested(self.mapTexture):
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
			
	def add_gold(self, point):
		if random.random() < self.prob_gold:
			if dist(point, self.start_point) > 10 and random.random() > self.prob_gold:
				if self.king_goblin == None or dist(point, self.king_goblin) > self.goblin_distance:
					found = False
					for i in self.goblin:
						if dist(point, i) < self.goblin_distance:
							found = True
							break
							
					if not found:
						self.gold.append(point)

	def add_goblin(self, point):
		if random.random() < self.prob_gold:
			if dist(point, self.start_point) > 10 and random.random() > self.prob_goblin:
				if (self.king_goblin == None or dist(point, self.king_goblin) > self.goblin_distance) and (self.husband == None or dist(point, self.husband) > self.goblin_distance):
					found = False
					for i in self.friendly:
						if dist(point, i) < self.goblin_distance:
							found = True
							break
							
					if not found:
						self.goblin.append(point)
						
	def add_goblin_king(self, point):
		if random.random() < self.prob_king:
			if self.king_goblin == None and (self.husband == None or dist(point, self.husband) > self.goblin_distance):
				found = False
				for i in self.goblin:
					if dist(point, i) < self.goblin_distance:
						found = True
						break
						
				if not found:
					self.king_goblin = point

	def add_husband(self):
		while self.husband == None:
			for y in range(self.mapSize):
				for x in range(self.mapSize):
					if (not self.can_add((x,y))) and random.random() < self.prob_husband:
						self.husband = (x,y)
						

	def add_friend(self, point):
		if random.random() < self.prob_friend:
			if dist(point, self.start_point) > 10 and random.random() > self.prob_goblin:
				if self.king_goblin == None or dist(point, self.king_goblin) > self.goblin_distance:
					found = False
					for i in self.goblin:
						if dist(point, i) < self.goblin_distance:
							found = True
							break
							
					if not found:
						self.friendly.append(point)

	def can_add(self, point):
		return self.mapTexture.buffer[(point[1] * self.mapSize + point[0]) * 4+1] != 255
		
	def add_point(self, point):
		self.mapTexture.buffer[(point[1] * self.mapSize + point[0]) * 4+1] = 255
	
	def on_key_press(self, symbol, modifiers):
		if symbol == key.ENTER:
			self.save_map()
		elif symbol == key.SPACE:
			self.new_map()
		elif symbol == key.ESCAPE or symbol == key.Q:
			exit()
				
	def on_mouse_motion(self, x, y, dx, dy):
		return pyglet.event.EVENT_HANDLED
		
	def on_mouse_press(self, px, py, button, modifiers):
		x = float(px)/(self.width/2) -1
		y = float(py)/(self.height/2) -1
		print x
		print y
		return pyglet.event.EVENT_HANDLED

	def on_mouse_release(self, x, y, button, modifiers):
	    return pyglet.event.EVENT_HANDLED
	
	def on_mouse_drag(self, px, py, dx, dy, buttons, modifiers):
		x = float(px)/(self.width/2) -1
		y = float(py)/(self.height/2) -1
		return pyglet.event.EVENT_HANDLED
		
	def on_resize(self, width, height):
		# Override the default on_resize handler to create a 3D projection
		self.projection = Matrix.perspective(width, height, 60, 0.1, 1000)
		glViewport(0, 0, width, height)
		glClearColor(0,0,0, 255)
		return pyglet.event.EVENT_HANDLED

if __name__ == '__main__':
	window = Application()
	pyglet.app.run()