from __future__ import with_statement
from contextlib import nested
from pyglet.gl import *
import math
from gletools import ShaderProgram, Sampler2D, Matrix, Texture, VBO
from ctypes import c_float
from vector import Vector
from protagonist import Protagonist

class Gold(Protagonist):
	def __init__(self, texture, program, x, y, position, collision_map, mesh):
		super(Gold, self).__init__(texture, program, x, y, position, collision_map, mesh)
		self.value = 5.0