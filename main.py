from engine.networking.connection import ClientConnection, ServerConnection
from engine.networking.packets import TestPacket, TestPacket2

import time

def main():
    ServerConn = ServerConnection('', 8888)
    ClientConn = ClientConnection('localhost', 8888)

    while True:
        # print received packets
        while True:
            pkt = ServerConn.read()
            if pkt is not None: print(pkt)
            else: break
        while True:
            pkt = ClientConn.read()
            if pkt is not None: print(pkt)
            else: break
        
        ClientConn.send(TestPacket2(0.5))
        time.sleep(1)
        ServerConn.send_all(TestPacket(3))
        time.sleep(1)


if __name__ == "__main__":
	main()