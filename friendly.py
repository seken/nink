from protagonist import Protagonist
from vector import Vector

class Friendly(Protagonist):
	def __init__(self, texture, program, x, y, position, collisionMap):
		super(Friendly, self).__init__(texture, program, x, y, position, collisionMap)
		self.husband = False
		self.pokeTimer = 0.0
		
	def update(self, delta, state):
		
		self.pokeTimer-=delta
		
		uMoved = False
		
		if self.pokeTimer < 0:
			for i in state.gold:
				distance = i.position - self.position
				if distance.len() < 8.0 and self.within(state.player.position):
					# find the rotation between self and gold
					self.point(-distance.toAngle() + 0.25)
					if distance.len() > 1.0:
						self.move(Vector(2.0, 0, 0)*delta)
					uMoved = True
					
		distance = state.player.position - self.position
		if (not uMoved) and distance.len() < 5.0 and self.within(state.player.position):
			# find the rotation between self and player
			self.point(-distance.toAngle() + 0.25)
			if distance.len() > 2.0:
				self.move(Vector(2.0, 0, 0)*delta)
		super(Friendly, self).update(delta, state)
		
	def poked(self):
		self.pokeTimer = 4.0