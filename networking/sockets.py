import socket
import socketserver
from threading import Thread

class UDPSocket(socket.socket):
    def __init__(self, host, port, *args, **kwargs):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        self.bind((host, port))

class ThreadedUDPSocket(UDPSocket):
    def __init__(self, *args, bufsize=4096, on_recv=None, **kwargs):
        UDPSocket.__init__(self, *args, **kwargs)
        self.on_recv_callback = on_recv
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
        if self.on_recv_callback:
            self.on_recv_callback(addr, port, data)
        else:
            raise Exception("Not implemented / no callback set")
