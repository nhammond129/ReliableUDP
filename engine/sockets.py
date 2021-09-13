import socket
import socketserver
from threading import Thread

class UDPSocket(socket.socket):
    def __init__(self, host, port, *args, **kwargs):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        self.bind((host, port))

class ThreadedUDPSocket(UDPSocket):
    def __init__(self, *args, bufsize=4096, **kwargs):
        UDPSocket.__init__(self, *args, **kwargs)
        self.bufsize = bufsize
        self._alive = True
        self._thread = Thread(target=self.daemon)
        self._thread.start()
    
    def daemon(self):
        while self._alive:
            data, (addr, port) = self.recvfrom(self.bufsize)
            self.on_recv(addr, port, data)
        
    def on_recv(self, addr, port, data):
        """
        (Abstract method)
        Event callback for when the socket receives data.
        """
        raise Exception("Not implemented.")

class RequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        socketserver.BaseRequestHandler.__init__(self, *args, **kwargs)
        


class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    timeout = 30
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("client: {}, wrote: {}".format(self.client_address, data))
        socket.sendto(data.upper(), self.client_address)

        while True:
            try:
                data, (addr, port) = socket.recvfrom(4096)
            except socket.timeout:
                break


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

def main():
    class PrintSocket(ThreadedUDPSocket):
        def __init__(self, *args, **kwargs):
            ThreadedUDPSocket.__init__(self, *args, **kwargs)
        
        def on_recv(self, addr, port, data):
            print(f"{addr}:{port} | {data}")
    
    client = PrintSocket(host='localhost', port=0)
    server = ThreadedUDPServer(('', 8888), ThreadedUDPRequestHandler)
    Thread(target=server.serve_forever).start()

    client.sendto(b"hello", ('localhost', 8888))



if __name__ == "__main__":
    main()