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
        self._thread = Thread(target=self._daemon)
        self._thread.start()
    
    def _daemon(self):
        while self._alive:
            data, (addr, port) = self.recvfrom(self.bufsize)
            self.on_recv(addr, port, data)
        
    def on_recv(self, addr, port, data):
        """
        (Abstract method)
        Event callback for when the socket receives data.
        """
        raise Exception("Not implemented.")

def main():
    class PrintSocket(ThreadedUDPSocket):
        def __init__(self, *args, **kwargs):
            ThreadedUDPSocket.__init__(self, *args, **kwargs)
        
        def on_recv(self, addr, port, data):
            print(f"{addr}:{port} | {data}")

    class EchoSocket(ThreadedUDPSocket):
        def __init__(self, *args, **kwargs):
            ThreadedUDPSocket.__init__(self, *args, **kwargs)
        
        def on_recv(self, addr, port, data):
            self.sendto(data.upper(), (addr, port))

    client = PrintSocket(host='localhost', port=0)
    server = EchoSocket(host='', port=8888)

    client.sendto(b"hello", ('localhost', 8888))
    client.sendto(b"one", ('localhost', 8888))
    client.sendto(b"two", ('localhost', 8888))
    client.sendto(b"three", ('localhost', 8888))
    client.sendto(b"four", ('localhost', 8888))



if __name__ == "__main__":
    main()