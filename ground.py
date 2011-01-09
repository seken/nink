from __future__ import with_statement
from contextlib import nested
from pyglet.gl import *
import math
from gletools import ShaderProgram, Sampler2D, Matrix, Texture, VBO
from ctypes import c_float

class Ground(object):
	def __init__(self, texture, tiles, tdim, res, minc, maxc):
		super(Ground, self).__init__()
		self.map = texture
		self.tiles = tiles
		self.prog = ShaderProgram.open('shaders/ground.shader')
		self.prog.vars.map = Sampler2D(GL_TEXTURE0)
		self.prog.vars.tiles = Sampler2D(GL_TEXTURE1)
		self.prog.vars.tNumX = tdim.x
		self.prog.vars.tNumY = tdim.y;
		self.prog.vars.tAmount = tdim.z;
		self.prog.vars.resX = 1.0/res.x
		self.prog.vars.resY = 1.0/res.y
		self.min = minc
		self.max = maxc
		with nested(self.map):
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		with nested(self.tiles):
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		position = [
				self.min.x, 0, self.min.y,
				self.min.x, 0, self.max.y,
				self.max.x, 0, self.max.y,
				self.max.x, 0, self.min.y,
		]
		texCoord = [
			0, 0,
			0, 1,
			1, 1,
			1, 0,
		]
		position = (c_float*len(position))(*position)
		texCoord = (c_float*len(texCoord))(*texCoord)
		self.mesh = VBO(4,
			position_3=position,
			texCoord_2=texCoord)
						
	def draw(self, projection, camera, player_position, r):	
		self.prog.vars.mvp = projection * camera
		with nested(self.prog):
			self.map.bind(self.map.id)
			self.tiles.bind(self.tiles.id)
		with nested(self.prog, self.map, self.tiles):
			self.prog.vars.playerLight = r*0.1 + 0.9
			self.prog.vars.playerPosition = player_position.tuple()
			self.mesh.draw(GL_QUADS)