import nulltk as tk
import math
from engine.gameobject import GameObject

class MyGraph(tk.Graph):
	def __init__(self, *args, **kwargs):
		tk.Graph.__init__(self, *args, **kwargs)

		player = GameObject(self, "player")

		self.plotpoint(0,0)
		self.bind('<Button-3>', self.on_rmb)

		def tick():
			player.tick()
			self.after(10, tick)
		self.after(10, tick)

	def on_rmb(self, event):
		wx, wy = self.window_to_world(event.x, event.y)
		GameObject.objects['player'].set_target(wx, wy)

	def on_create_object(self, obj: GameObject):
		self.create_oval(
			*obj.get_new_coords(),
			fill='white',
			tags=(f"{obj.id}"))

	def on_update_object(self, obj: GameObject):
		self.coords(f"{obj.id}", *obj.get_new_coords())

def main():
	root = tk.Tk()

	graph = MyGraph(root, width=800, height=600)
	graph.pack()

	root.mainloop()

if __name__ == "__main__":
	main()