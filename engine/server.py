import pygase

class Server(pygase.Server):
	database_file = 'data.db'
	def __init__(self, *args, **kwargs):
		pygase.Server.__init__(self, *args, **kwargs)
		self.run_in_thread()

		"""
		all `on_X` functions will be bound to events with name `X`
		"""
		handlers = ['_'.join(fn.split('_')[1:]) for fn in dir(self) if fn.startswith('on_')]
		event_handlers = {handler : getattr(self, 'on_'+handler) for handler in handlers}

		for event, handler in event_handlers.items():
			self.register_event_handler(event, handler)