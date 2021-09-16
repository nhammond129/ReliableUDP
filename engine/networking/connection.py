from threading import Thread
import ctypes
from engine.networking.encoding.encode import pack
from engine.networking.sockets import ThreadedUDPSocket
import engine.networking.encoding as encoding
import engine.networking.packets as packets

class Connection:
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
	protocol_id = 1342
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.buffer = b''
		self.ack: ctypes.uint32 = 0
		self.ack_bitfields: ctypes.uint32 = 0
		self.sequence: ctypes.uint32 = 0
		self.last_acked_seq: ctypes.uint32 = 0
		self.unacked = {}

		self.packet_recvd_buffer = []
	
	@classmethod
	def sequence_greater_than(klass, seq1: int, seq2: int):
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

	def send(self, packet):
		data = self.encode_packet(packet)
		self.socket.sendto(data, (self.host, self.port))
		self.unacked[self.sequence] = data
		self.sequence += 1
	
	def can_read(self):
		return (len(self.packet_recvd_buffer) > 0)

	def read_all(self):
		out = []
		while self.can_read():
			out.append(self.read())
		return out

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

		if Connection.sequence_greater_than(seq, self.ack):
			# received a newer packet, ack it and shift ack bits
			self.ack_bitfields << (seq - self.ack)
			self.ack = seq
		elif Connection.sequence_greater_than(seq, self.ack - 33):
			# set corresponding ack bit
			self.ack_bitfields & (1 << abs(self.ack - seq))
		else:
			# older than the the previous 33 packets
			# let it go unacked
			# TODO: let packets require acking, send special ack-packet for them if they drop too far?
			pass

		# sequence number was acked
		if ack_seq in self.unacked:
			del self.unacked[ack_seq]
		for ack_bit in range(0, 32):
			# is that seqnum's ack bit set?
			if ((ack_bits >> ack_bit) & 0x1):
				# it was acked
				ackable = (ack_seq - ack_bit)
				if ackable in self.unacked:
					del self.unacked[ackable]
		
		rest, trailing_data = self.decode(trailing_data)

		return (decoded_pkts + rest, trailing_data)

def Client(host, port, socketclass=ThreadedUDPSocket):
	conn = Connection(host, port)
	conn.socket = socketclass(host, 0, on_recv = conn.on_recv)
	return conn

class Server:
	def __init__(self, host, port, socketclass=ThreadedUDPSocket):
		self.socket = socketclass(host, port, on_recv=self.on_recv)
		self.connections = {}

	def add_client(self, addr, port):
		conn = Connection(addr, port)
		conn.socket = self.socket
		self.connections[(addr, port)] = conn

	def on_recv(self, addr, port, data):
		client = (addr, port)
		if client not in self.connections:
			self.add_client(addr, port)
		self.connections[client].on_recv(addr, port, data)

	def send_all(self, packet):
		for client, conn in tuple(self.connections.items()):
			conn.send(packet)
	
	def send_to(self, client, packet):
		self.connections[client].send(packet)

	def read(self):
		out = {}
		for client, conn in tuple(self.connections.items()):
			out[client] = conn.read()
		return out

	def read_all(self):
		out = {}
		for client, conn in tuple(self.connections.items()):
			out[client] = conn.read_all()
		return out