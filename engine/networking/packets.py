import engine.networking.encoding as encoding
PACKETS = {}

def packet(id):
	def wrapper(klass):
		PACKETS[id] = klass
		klass.packet_id = id
		return klass
	return wrapper

@packet(0)
class TestPacket:
	format = 'i'
	def __init__(self, test_number: int):
		self.test_number = test_number

	def encode(self):
		return encoding.pack(self.format, self.test_number)

	@classmethod
	def decode(cls, data):
		test_number, = encoding.unpack(cls.format, data)
		return cls(test_number)

	def __str__(self):
		return f"<TestPacket test_number={self.test_number}>"
@packet(1)
class TestPacket2:
	format = 'f'
	def __init__(self, test_number: float):
		self.test_number = test_number

	def encode(self):
		return encoding.pack(self.format, self.test_number)

	@classmethod
	def decode(cls, data):
		test_number, = encoding.unpack(cls.format, data)
		return cls(test_number)

	def __str__(self):
		return f"<TestPacket2 test_number={self.test_number}>"