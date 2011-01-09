# This file is part of Nink.
# 
# Nink is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Nink is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Nink.  If not, see <http://www.gnu.org/licenses/>.
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