from __future__ import with_statement
from contextlib import nested
from pyglet.gl import *
import math
from gletools import ShaderProgram, Sampler2D, Matrix, Texture, VBO
from ctypes import c_float
from vector import Vector
from collisionMap import CollisionMap

class Walls(object):
	wallVals = [10, 11, 12, 13, 26, 28, 29, 30, 31, 32, 33, 46, 47, 48, 49, 50, 51]
	earthVal = 26
	
	def __init__(self, texture, tiles, tdim, res, minc, maxc, path):
		super(Walls, self).__init__()
		self.map = texture
		self.tiles = tiles
		self.prog = ShaderProgram.open(path+'/shaders/wall.shader')
		self.prog.vars.map = Sampler2D(GL_TEXTURE0)
		self.prog.vars.tiles = Sampler2D(GL_TEXTURE1)
		self.prog.vars.tNumX = tdim.x
		self.prog.vars.tNumY = tdim.y;
		self.prog.vars.tAmount = tdim.z;
		self.prog.vars.resX = 1.0/res.x
		self.prog.vars.resY = 1.0/res.y
		self.min = minc
		self.max = maxc
		self.dimc = Vector(maxc.x - minc.x, maxc.y - minc.y, maxc.z - minc.z)
		self.tdim = tdim
		self.height = 1.5
		with nested(self.map):
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		with nested(self.tiles):
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		self.create_mesh()
		
	def create_mesh(self):
		wallmap = []
		self.quads = []
		self.texCoords = []
		self.tile = []
		
		def placeQuad(x1,y1, x2,y2, value):
			self.quads.extend([x1, 0, y1, x2, 0, y2, x2, self.height, y2, x1, self.height, y1])
			self.texCoords.extend([0, 1, 1, 1, 1, 0, 0, 0])
			self.tile.extend([value, value, value, value])
			
		def placeRoof(ax, ay):
			x1 = (float(ax)/self.map.width)*self.dimc.x + self.min.x
			x2 = (float(ax+1)/self.map.width)*self.dimc.x + self.min.x
			y1 = (float(ay)/self.map.height)*self.dimc.y + self.min.y
			y2 = (float(ay+1)/self.map.height)*self.dimc.y + self.min.y
			self.quads.extend([x1, self.height, y1, x1, self.height, y2, x2, self.height, y2, x2, self.height, y1])
			self.texCoords.extend([0, 1, 1, 1, 1, 0, 0, 0])
			self.tile.extend([self.earthVal, self.earthVal, self.earthVal, self.earthVal])
			
		for y in range(self.map.height):
			wallmap.append([])
			for x in range(self.map.width):
				value = int(float(self.map.buffer[(x + y*self.map.width) *4 + 1])*(self.tdim.z-1)/255)
				if value in Walls.wallVals:
					wallmap[y].append(value)
				else:
					wallmap[y].append(-1)
					
		self.collisionMap = CollisionMap(wallmap, self.min, self.max, self.dimc)
					
		for y in range(self.map.height):
			for x in range(self.map.width):
				if wallmap[y][x] >= 0:
					if y+1 < self.map.height and wallmap[y+1][x] == -1:
						posx1 = (float(x)/self.map.width)*self.dimc.x + self.min.x
						posx2 = (float(x+1)/self.map.width)*self.dimc.x + self.min.x
						posy1 = (float(y+1)/self.map.height)*self.dimc.y + self.min.y
						posy2 = (float(y+1)/self.map.height)*self.dimc.y + self.min.y
						placeQuad(posx1, posy1, posx2, posy2, wallmap[y][x])
					if y-1 > 0 and wallmap[y-1][x] == -1:
						posx1 = (float(x)/self.map.width)*self.dimc.x + self.min.x
						posx2 = (float(x+1)/self.map.width)*self.dimc.x + self.min.x
						posy1 = (float(y)/self.map.height)*self.dimc.y + self.min.y
						posy2 = (float(y)/self.map.height)*self.dimc.y + self.min.y
						placeQuad(posx1, posy1, posx2, posy2, wallmap[y][x])
					if x-1 > 0 and wallmap[y][x-1] == -1:
						posx1 = (float(x)/self.map.width)*self.dimc.x + self.min.x
						posx2 = (float(x)/self.map.width)*self.dimc.x + self.min.x
						posy1 = (float(y)/self.map.height)*self.dimc.y + self.min.y
						posy2 = (float(y+1)/self.map.height)*self.dimc.y + self.min.y
						placeQuad(posx1, posy1, posx2, posy2, wallmap[y][x])
					if x+1 < self.map.height and wallmap[y][x+1] == -1:
						posx1 = (float(x+1)/self.map.width)*self.dimc.x + self.min.x
						posx2 = (float(x+1)/self.map.width)*self.dimc.x + self.min.x
						posy1 = (float(y)/self.map.height)*self.dimc.y + self.min.y
						posy2 = (float(y+1)/self.map.height)*self.dimc.y + self.min.y
						placeQuad(posx1, posy1, posx2, posy2, wallmap[y][x])
					placeRoof(x, y)
		
		position = (c_float*len(self.quads))(*self.quads)
		texCoord = (c_float*len(self.texCoords))(*self.texCoords)
		tile = (c_float*len(self.tile))(*self.tile)
		self.mesh = VBO(len(self.quads)/3,
			position_3=position,
			texCoord_2=texCoord,
			tile_1=tile)
			
	def update(self, delta):
		pass
		
	def draw(self, projection, camera, player_position, r):	
		self.prog.vars.mvp = projection * camera
		with nested(self.prog):
			self.map.bind(self.map.id)
			self.tiles.bind(self.tiles.id)
		with nested(self.prog, self.map, self.tiles):
			self.prog.vars.playerLight = r*0.1 + 0.9
			self.prog.vars.playerPosition = player_position.tuple()
			self.mesh.draw(GL_QUADS)
