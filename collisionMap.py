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
class CollisionMap(object):
	def __init__(self, bitmap, minc, maxc, dimc):
		super(CollisionMap, self).__init__()
		self.bmp = bitmap
		self.min = minc
		self.max = maxc
		self.dim = dimc
		self.y = len(bitmap)
		self.x = len(bitmap[0])
	
	def collision(self, position, radius=0.5):
		position.y = position.z
		position = (position - self.min)
		position.x = (position.x / self.dim.x) * self.x
		position.y = (position.y / self.dim.y) * self.y
		if position.x < 0 or position.y < 0 or position.x >= self.x or position.y >= self.y:
			return True
		if self.bmp[int(position.y)][int(position.x)] == -1 and self.bmp[int(position.y+radius)][int(position.x+radius)] == -1 and self.bmp[int(position.y+radius)][int(position.x-radius)] == -1 and self.bmp[int(position.y-radius)][int(position.x+radius)] == -1 and self.bmp[int(position.y-radius)][int(position.x-radius)] == -1:
			return False
		return True
