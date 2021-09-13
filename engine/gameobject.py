from collections import defaultdict
from weakref import WeakSet

import math

class GameObject:
	__refs__ = defaultdict(WeakSet)
	objects = {}
	w, h = 10, 10
	def __init__(self, graph, id, x=0, y=0):
		self.tarx, self.tary = 0, 0

		self.graph = graph
		self.id = id
		self.x, self.y = x, y
		
		self.objects[self.id] = self

	@classmethod
	def get_instances(cls):
		return cls.__refs__[cls]

	@classmethod
	def get_instance_by_id(id):
		for instance in GameObject.get_instances():
			if instance.id == id: return instance
		return None
	
	def set_target(self, x, y):
		self.tarx, self.tary = x, y

	def move(self, dx, dy):
		self.x += dx
		self.y += dy
		self.graph.on_update_object(self)

	def tick(self):
		dist = math.dist((self.tarx, self.tary), (self.x, self.y))
		if dist < 1:
			return
		dir_radians = math.atan2(self.tary - self.y, self.tarx - self.x)

		dx = math.cos(dir_radians)
		dy = math.sin(dir_radians)
		self.move(
			min(dx*5, dx*dist, key=abs),
			min(dy*5, dy*dist, key=abs)
		)

	def get_new_coords(self):
		graph = self.graph
		w, h = self.w, self.h
		x, y = graph.world_to_canvas(self.x, self.y)
		return (x - w/graph.zoom, y - h/graph.zoom, x + w/graph.zoom, y + h/graph.zoom)