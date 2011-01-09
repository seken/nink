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

class Enemy(Protagonist):
	def __init__(self, texture, program, x, y, position, collisionMap, mesh):
		super(Enemy, self).__init__(texture, program, x, y, position, collisionMap, mesh)
		self.cooldown = 0.0
		self.health = 30
		
	def update(self, delta, state):
		self.cooldown -= delta
		
		if (self.position - state.player.position).len() < 15:
			attacked = False
			for i in state.friendly:
				attacked = self.attack_person(delta, i, state)
				if attacked:
					break
				
			if not attacked:
				self.attack_person(delta, state.player, state)
			
			super(Enemy, self).update(delta, state)
		
	def attack_person(self, delta, person, state):
		distance = person.position - self.position
		if distance.len() < 7.0 and self.within(person.position):
			# find the rotation between self and person
			finished = False
			self.point(-distance.toAngle() + 0.25)
			if distance.len() > 1.0:
				self.move(Vector(1.8, 0, 0)*delta)
			if distance.len() < 1.2 and self.cooldown < 0:
				state.hurt_sound.play()
				self.cooldown = 1.0
				person.hit()
			return True
		return False
		