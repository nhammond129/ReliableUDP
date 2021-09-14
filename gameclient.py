from engine.networking.sockets import ThreadedUDPSocket



class Client(ThreadedUDPSocket):
	def __init__(self, *args, **kwargs):
		ThreadedUDPSocket.__init__(self, *args, **kwargs)
	
	def on_recv(self, addr, port, data):
		print(f"{addr}:{port} | {data}")

def main():
	client = Client()
	while True:
		client.think()

if __name__ == "__main__":
	main()