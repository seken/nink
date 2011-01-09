from __future__ import with_statement
from contextlib import nested
from pyglet.gl import *
import math
from gletools import ShaderProgram, Sampler2D, Matrix, Texture, VBO
from ctypes import c_float
from vector import Vector

def xfrange(start, stop, step):
    while start < stop:
        yield start
        start += step

class Protagonist(object):
	def __init__(self, texture, program, x, y, position, collisionMap, mesh):
		super(Protagonist, self).__init__()
		self.tex = texture
		self.prog = program
		self.x = float(x)
		self.y = float(y)
		self.cooldown = 0.0
		self.collisionMap = collisionMap
		self.health = 100
		self.velocity = Vector(0.0, 0.0, 0.0)
		self.position = Vector(position[0], self.y/2, position[1])
		self.maxSpeed = 4
		self.modelview = Matrix().translate(position[0], self.y/2, position[1])
		self.moved = False
		self.angle = 0
		self.mesh = mesh
		with nested(self.tex):
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
	
	def update(self, delta, state):
		self.cooldown-= delta
		if self.moved:
			self.moved = False
		else:
			self.velocity = self.velocity * 0.8
			if self.velocity.len() < 0.1:
				self.velocity = Vector()
		facingVelocity = self.velocity.rotatey(self.angle)
		movedBy = facingVelocity * delta
		if not self.collisionMap.collision(self.position + movedBy, self.x/4):
			self.position = self.position + movedBy
			self.modelview = Matrix().translate(self.position.x, self.position.y, self.position.z) * Matrix().rotatey(-self.angle)
		
	def move(self, dvel):
		self.moved = True
		if self.velocity.len() == self.maxSpeed:
			return
		else:
			self.velocity = self.velocity + dvel
		if self.velocity.len() > self.maxSpeed:
			self.velocity.norm(self.maxSpeed)
			
	def teleport(self, x, y):
		self.position.x = x
		self.position.z = y
	
	def turn(self, angle):
		self.angle = self.angle + angle
		
	def point(self, angle):
		self.angle = angle
	
	def draw(self, projection, camera, player_position, r):
		self.prog.vars.mvp = projection * camera * self.modelview
		self.prog.vars.playerLight = r*0.1 + 0.9
		self.prog.vars.playerPosition = player_position.tuple()
		self.prog.vars.modelview = self.modelview
		with nested(self.prog, self.tex):
			self.mesh.draw(GL_QUADS)
			
	def hit(self):
		self.health -= 10
		
	def within(self, position):
		position = position - self.position
		
		for i in xfrange(0.0, 1.0, 0.05):
			point = self.position + (position * i)
			if self.collisionMap.collision(point, self.x/4):
				return False
		
		return True
		
	def depth(self, proj_cam):
		mat = proj_cam * self.modelview
		vector = mat.col(3)
		return -vector.z
		