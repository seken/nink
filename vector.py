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
import math

class Vector:
	def __init__(self, *args, **kwargs):
		if len(args) > 0:
			self.x = float(args[0])
			self.y = float(args[1])
			self.z = float(args[2])
		else:
			self.x = 0.0
			self.y = 0.0
			self.z = 0.0
		
	def __add__(self, other):
		return Vector(self.x+other.x, self.y+other.y, self.z+other.z)
		
	def __sub__(self, other):
		return Vector(self.x-other.x, self.y-other.y, self.z-other.z)
		
	def __mul__(self, other):
		return Vector(self.x * other, self.y * other, self.z * other)

	def __div__(self, other):
		return Vector(self.x / other.x, self.y / other.y, self.z / other.z)

	def norm(self, s=None):
		if s == None:
			s = self.len()
		else:
			s = self.len()/s
		if s != 0:
			self.x = float(self.x) / s
			self.y = float(self.y) / s
			self.z = float(self.z) / s
		else:
			self.x = 0
			self.y = 0
			self.z = 1
		
	def len(self):
		return math.sqrt(math.pow(self.x,2) + math.pow(self.y,2) + math.pow(self.z,2))
		
	def rotatey(self, angle):
		return Vector(self.x * math.cos(angle*2*math.pi) + self.z * math.sin(angle*2*math.pi), self.y, self.x * math.sin(angle*2*math.pi) + self.z * math.cos(angle*2*math.pi))
		
	def tuple(self):
		return (self.x, self.y, self.z)
		
	def toAngle(self):
		return math.atan2(self.x, self.z)/(2*math.pi)