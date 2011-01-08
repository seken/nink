from protagonist import Protagonist
from vector import Vector

class Friendly(Protagonist):
	def __init__(self, texture, program, x, y, position, collisionMap):
		super(Friendly, self).__init__(texture, program, x, y, position, collisionMap)
		self.husband = False
		
	def update(self, delta, state):
		distance = state.player.position - self.position
		if distance.len() < 5.0 and self.within(state.player.position):
			# find the rotation between self and player
			self.point(-distance.toAngle() + 0.25)
			if distance.len() > 2.0:
				self.move(Vector(2.0, 0, 0)*delta)
		super(Friendly, self).update(delta, state)