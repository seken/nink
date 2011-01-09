from protagonist import Protagonist
from vector import Vector

class Friendly(Protagonist):
	def __init__(self, texture, program, x, y, position, collisionMap, mesh):
		super(Friendly, self).__init__(texture, program, x, y, position, collisionMap, mesh)
		self.husband = False
		self.pokeTimer = 0.0
		self.gold = 0.0
		
	def update(self, delta, state):
		
		self.pokeTimer-=delta
		
		# Repel away from other friends
		if (self.position - state.player.position).len() < 15:
			for i in state.friendly:
				distance = self.position - i.position
				if distance.len() < 0.5:
					if not self.collisionMap.collision(self.position + (distance*0.1), self.x/4):
						self.position = self.position + (distance*0.1)
		
		uMoved = False
		
		# Follow the money
		if self.pokeTimer < 0:
			for i in state.gold:
				distance = i.position - self.position
				if distance.len() < 8.0 and self.within(state.player.position):
					# find the rotation between self and gold
					self.point(-distance.toAngle() + 0.25)
					if distance.len() > 1.0:
						self.move(Vector(2.0, 0, 0)*delta)
					else:
						if i.value > delta:
							self.gold += delta
							i.value -= delta
						else:
							self.gold += i.value
							i.value = 0
					uMoved = True
					break
					
		# Kill the bad guys
		if (self.position - state.player.position).len() < 15:
			for i in state.enemy:
				distance = i.position - self.position
			
				if self.husband:
					if distance.len() < 4.0 and self.within(state.player.position):
						self.point(-distance.toAngle() + 0.25)
						state.fire_arrow(self)
						uMoved = True
						break
				else:
					if distance.len() < 1.0:
						self.point(-distance.toAngle() + 0.25)
						state.fire_sword(self, i)
						uMoved = True
						break
		
			# Follow the girl
			distance = state.player.position - self.position
			if (not uMoved) and distance.len() < 5.0 and self.within(state.player.position):
				# find the rotation between self and player
				self.point(-distance.toAngle() + 0.25)
				if distance.len() > 2.0:
					self.move(Vector(2.0, 0, 0)*delta)
			super(Friendly, self).update(delta, state)
			
		return self.health <= 0
		
	def poked(self):
		self.pokeTimer = 4.0