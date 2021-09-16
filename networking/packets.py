from .encoding import pack, unpack
PACKETS = {}

def packet(id):
	def wrapper(klass):
		PACKETS[id] = klass
		klass.packet_id = id
		return klass
	return wrapper