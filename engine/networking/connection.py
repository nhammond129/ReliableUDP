from engine.networking.encoding.encode import pack
from engine.networking.sockets import ThreadedUDPSocket
import engine.networking.encoding as encoding
import engine.networking.packets as packets

class Connection(ThreadedUDPSocket):
	"""
	Packets will have the following structure:
	[uint protocol id]
	[uint sequence]
	[uint ack]
	[uint ack bitfields]
	[uint payload length]
	[uint payload type]
	[ ... payload bytes ... ]

	Thus header length is 24 bytes.
	"""
	protocol_id = 6969
	def __init__(self, host, port, *args, **kwargs):
		ThreadedUDPSocket.__init__(self, host, port, *args, **kwargs)
		self.host = host
		self.port = port
		self.buffer = b''
		self.ack = 0
		self.ack_bitfields = 0
		self.unacked = {}
		self.sequence = 0
		self.last_received_seqnum = 0

		self.packet_recvd_buffer = []
	
	@classmethod
	def sequence_greater_than(seq1: int, seq2: int):
		"""
		Returns true if seq1 is 'greater' than seq2.
		Sequence numbers are 32bit unsigned ints

		If their difference is greater than 1/2 the max sequence number (2^33 - 1)
		we consider the *smaller* one more recent
		"""
		return (
			( seq1 > seq2 ) and ( seq1-seq2 <= 2^32) or		# "close" together
			( seq1 < seq2 ) and ( seq2-seq1 >  2^32)		# "far" apart
		)

	def encode_packet(self, packet):
		payload = packet.encode()
		data = encoding.pack('IIIIII*',
			self.protocol_id, self.sequence,
			self.ack, self.ack_bitfields,
			len(payload), packet.packet_id,
			payload
		)
		return data
	
	def read(self):
		if len(self.packet_recvd_buffer):
			return self.packet_recvd_buffer.pop(0)
		else:
			return None

	def on_recv(self, addr, port, data):
		self.buffer += data
		packets, self.buffer = self.decode(self.buffer)
		self.packet_recvd_buffer.extend(packets)

	def decode(self, data):
		"""
		returns (list: Packet, trailing)
		"""
		if not data: return [], b''
		start_idx = data.find(encoding.pack('I', self.protocol_id))
		if start_idx > 0:
			# found, but after some other data? - discard "old" bytes
			print(f"Discarding {start_idx} bytes to resync")
			data = data[start_idx:]
		elif start_idx == -1:
			# could not find - wait for more data
			print(f"Discarding {start_idx} bytes to resync")
			return [], b''
		
		length = len(data)
		if length < 24: # less than packet header, wait for more data.
			return [], data
		
		proto_id, seq, ack_seq, ack_bits, payload_len, payload_type, data = encoding.unpack(
			"IIIIII*", data
		)
		
		remaining_len = len(data)

		if payload_len > remaining_len:
			raise ValueError("Packet too short")

		if proto_id != self.protocol_id:
			raise ValueError("Incorrect protocol id")

		payload, trailing_data = data[:payload_len], data[payload_len:]

		decoded_pkts = []
		if payload_type in packets.PACKETS:
			pkt = packets.PACKETS[payload_type].decode(payload)
			decoded_pkts.append(pkt)
		else:
			raise Exception(f"Undecoded packet of type {payload_type}")

		# set last_recvd_seq to seq
		#	shift our local ack stuff in response
		
		# note down the ack_seq and ack_bits received, determine whether to resend old packets?
		# cache pkts on send, save until ack'd if "must_resend = true" (or similar flag?)
		
		rest, trailing_data = self.decode(trailing_data)

		return (decoded_pkts + rest, trailing_data)

class ClientConnection(Connection):
	def __init__(self, host, port, *args, **kwargs):
		Connection.__init__(self, host, 0, *args, **kwargs)
		self.port = port

	def send(self, packet):
		data = self.encode_packet(packet)
		self.sendto(data, (self.host, self.port))
		self.sequence += 1

class ServerConnection(Connection):
	def __init__(self, host, port, *args, **kwargs):
		Connection.__init__(self, host, port, *args, **kwargs)
		self.clients = set()
	def on_recv(self, addr, port, data):
		self.buffer += data
		packets, self.buffer = self.decode(self.buffer)
		self.packet_recvd_buffer.extend(packets)
		self.clients.add((addr, port))

	def send_all(self, packet):
		data = self.encode_packet(packet)
		self.sequence += 1
		for c in self.clients:
			self.sendto(data, c)