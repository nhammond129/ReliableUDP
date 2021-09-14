import math

class Unit:
	def __init__(self, x, y):
		self.pos = (x, y)
		self.targetpos = (0, 0)
	
	@property
	def x(self):
		return self.pos[0]
	
	@property
	def y(self):
		return self.pos[1]
	
	def think(self, dt):
		tarx, tary = self.targetpos
		if math.dist(self.targetpos, self.pos) < 1:
			return

		theta = math.atan2(self.y - tary, self.x - tarx)
		dx, dy = (
			math.cos(theta),
			math.sin(theta)
		)

		self.pos = (self.x + dx, self.y + dy)

class GameWorld:
	def __init__(self):
		self.units = {}
	def new_unit(self, id, x=0, y=0):
		self.units[id] = Unit(x, y)
	def all_think(self, dt):
		for unit in self.units.values():
			unit.think(dt)