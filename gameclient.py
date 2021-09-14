import pygase
import time

class GameClient(pygase.Client):
	def __init__(self, *args, hostname='localhost', port=8080, **kwargs):
		pygase.Client.__init__(self, *args, **kwargs)
		self.connect_in_thread(hostname=hostname, port=port)

		"""
		all `on_X` functions will be bound to events with name `X`
		"""
		handlers = ['_'.join(fn.split('_')[1:]) for fn in dir(self) if fn.startswith('on_')]
		event_handlers = {handler : getattr(self, 'on_'+handler) for handler in handlers}

		for event, handler in event_handlers.items():
			self.register_event_handler(event, handler)

		while True:
			with self.access_game_state() as game_state:
				print(game_state.time_order, game_state.game_status)
				if game_state.time_order > 0: break
				try:
					print(game_state.position)
				except: pass
		print("READY!")
	
	def debug(self):
		with self.access_game_state() as game_state:
			# locks a copy of game state
			print(game_state.position, game_state.hp)
		self.dispatch_event("attack", attack_position=0.5)

	def on_info(self, *args):
		print(*args)

if __name__ == "__main__":
	client = GameClient()

	while True:
		client.debug()
		time.sleep(1)