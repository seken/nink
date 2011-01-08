from protagonist import Protagonist
from vector import Vector

class Enemy(Protagonist):
	def __init__(self, texture, program, x, y, position, collisionMap):
		super(Enemy, self).__init__(texture, program, x, y, position, collisionMap)
		self.cooldown = 0.0
		
	def update(self, delta, state):
		self.cooldown -= delta
		
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
			if distance.len() > 0.8:
				self.move(Vector(1.8, 0, 0)*delta)
			if distance.len() < 1.2 and self.cooldown < 0:
				state.hurt_sound.play()
				self.cooldown = 1.0
				person.hit()
			return True
		return False
		