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
from protagonist import Protagonist
from vector import Vector
from gletools import Matrix

class Arrow(Protagonist):
	def __init__(self, texture, program, x, y, position, collisionMap, mesh):
		super(Arrow, self).__init__(texture, program, x, y, position, collisionMap, mesh)
		self.cooldown = 2.0
		self.maxSpeed = 20
		self.velocity = Vector(20.0, 0.0, 0.0)

	def update(self, delta, state):
		self.velocity = self.velocity * 0.99
		facingVelocity = self.velocity.rotatey(self.angle)
		movedBy = facingVelocity * delta
		if not self.collisionMap.collision(self.position + movedBy, self.x/6):
			self.position = self.position + movedBy
			self.modelview = Matrix().translate(self.position.x, self.position.y, self.position.z) * Matrix().rotatey(-self.angle)
		else:
			self.velocity = self.velocity * 0.5
		
		self.cooldown -= delta
		if self.cooldown < 0:
			return False
		return True