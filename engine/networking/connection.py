from engine.networking.sockets import ThreadedUDPSocket
import encoding
import packets

class Connection(ThreadedUDPSocket):
	"""
	Packets will have the following structure:
	[uint protocol id]
	[uint sequence]
	[uint ack]
	[uint ack bitfields]
	[uint payload length]
	[ ... payload bytes ... ]
	"""
	protocol_id = 123180273
	def __init__(self, *args, **kwargs):
		ThreadedUDPSocket.__init__(self, *args, **kwargs)
		self.ack = 0
		self.sequence = 0

	def send(self, packet: packets.Packet):
		payload = packet.encode()
		data = encoding.pack('IIIII*', )


	def decode(data):
		"""
		returns (list: Packet, trailing)
		"""
		if not data: return [], b''
		start_idx = data.find(self.protocol_id)
