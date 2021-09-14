import sockets
import bson

class Connection:
	def __init__(self, addr, port):
		self.addr = addr
		self.port = port

class ClientConnection(Connection):
	def __init__(self, addr, port, *args, **kwargs):
		Connection

class ServerConnection:
	def __init__(self, addr, port):
		self.addr = addr
		self.port = port

class Server(sockets.ThreadedUDPSocket):
	def __init__(self, *args, **kwargs):
		sockets.ThreadedUDPSocket.__init__(self, *args, **kwargs)
		self.connections = []

	def broadcast(self, data):
		for conn in self.connections:
			conn.send(data)
	
	def on_recv(self, addr, port, data):
		self.sendto(data.upper(), (addr, port))