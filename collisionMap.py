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
