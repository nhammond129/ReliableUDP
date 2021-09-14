
PACKETS = {}

def packet(id):
	def wrapper(klass):
		PACKETS[id] = klass
		klass.packet_id = id
		return klass
	return wrapper

class UndecodedPacket:
	def __init__(self, packet_id, data):
		self.packet_id = packet_id
		self.data = data
	
	def encode(self):
		return self.data
	
	@classmethod
	def decode(cls, data):
		return cls(0, data)