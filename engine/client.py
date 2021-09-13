import pygase

class Client(pygase.Client):
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