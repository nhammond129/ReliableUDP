import encoding
PACKETS = {}

def packet(id):
	def wrapper(klass):
		PACKETS[id] = klass
		klass.packet_id = id
		return klass
	return wrapper

class Packet:
	packet_id = 0
	format = '!I'
	