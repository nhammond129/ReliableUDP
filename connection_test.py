from networking.connection import Connection, Client, Server
from networking.encoding import pack, unpack
import networking.packets as packets

import nulltk as tk
import time

@packets.packet(0)
class TestPacket:
	format = 'i'
	def __init__(self, test_number: int):
		self.test_number = test_number

	def encode(self):
		return pack(self.format, self.test_number)

	@classmethod
	def decode(cls, data):
		test_number, = unpack(cls.format, data)
		return cls(test_number)

	def __str__(self):
		return f"<TestPacket test_number={self.test_number}>"

@packets.packet(1)
class TestPacket2:
	format = 'f'
	def __init__(self, test_number: float):
		self.test_number = test_number

	def encode(self):
		return pack(self.format, self.test_number)

	@classmethod
	def decode(cls, data):
		test_number, = unpack(cls.format, data)
		return cls(test_number)

	def __str__(self):
		return f"<TestPacket2 test_number={self.test_number}>"

def main():
    server = Server('localhost', 8888)
    client1 = Client('localhost', 8888)
    client2 = Client('localhost', 8888)

    def send_packets():
        client1.send(TestPacket(1))
        client2.send(TestPacket(2))
        server.send_all(TestPacket2(0.4))

    def read_packets():
        print("client1:\n\t", client1.read_all())
        print("client2:\n\t", client2.read_all())
        print("server:\n\t",  server.read_all())

    start_time = time.time()
    packets_sent = 0
    while True:
        send_packets()
        read_packets()
        packets_sent += 4
        secs = time.time() - start_time
        print("time elapsed:", secs, "seconds")
        print("packets per sec:", packets_sent/secs)

        for conn in (client1, client2, *server.connections.values()):
            lost = len(conn.unacked)
            print("packets sent / lost:", conn.sequence, lost)
            try:
                print("loss %:", lost/conn.sequence)
            except ZeroDivisionError:
                pass

if __name__ == "__main__":
    main()
