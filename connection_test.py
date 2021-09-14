from engine.networking.connection import ClientConnection, Connection, ServerConnection
from engine.networking.packets import TestPacket, TestPacket2

import nulltk as tk
import time

class DebugLog(tk.Text):
    def __init__(self, master, *args, **kwargs):
        tk.Text.__init__(self, master, *args, **kwargs)
        self.config(state=tk.DISABLED)
    
    def log(self, msg):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, msg + '\n')
        self.see(tk.END)
        self.config(state=tk.DISABLED)

class ConnectionUI(tk.LabelFrame):
    def __init__(self, master, conn, *args, **kwargs):
        tk.LabelFrame.__init__(self, master, *args, **kwargs)
        self.conn = conn

        self.debuglog = DebugLog(self, width=80, height=5)
        self.debuglog.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        (
          self.buffer_label,
          self.ack_label,
          self.sequence_label,
          self.recvd_sequence_label,
          self.unacked_label
        ) = [tk.Label(self) for k in range(5)]
        for item in (
            self.buffer_label,
            self.ack_label,
            self.sequence_label,
            self.recvd_sequence_label,
            self.unacked_label ):
            item.pack(anchor=tk.NW)

        if self.conn.__class__ == ServerConnection:
            self.clients_label = tk.Label(self)
            self.clients_label.pack()

        self.after(100, self._read_loop)

    def _read_loop(self):
        self.buffer_label.config(text=f"buffer: {self.conn.buffer}")
        self.ack_label.config(text=f"ack: {self.conn.ack}, {self.conn.ack_bitfields:0b}")
        self.sequence_label.config(text=f"seq: {self.conn.sequence}")
        self.recvd_sequence_label.config(text=f"last recv'd seq: {self.conn.last_received_seqnum}")
        self.unacked_label.config(text=f"unacked pkts: {self.conn.unacked}")
        if self.conn.__class__ == ServerConnection:
            self.clients_label.config(text=f"{self.conn.clients}")
        while True:
            pkt = self.conn.read()
            if pkt is not None: self.debuglog.log(f"received {pkt} at {time.time()}")
            else: break
        self.after(100, self._read_loop)

def main():
    ServerConn = ServerConnection('', 8888)
    Client1Conn = ClientConnection('localhost', 8888)
    Client2Conn = ClientConnection('localhost', 8888)

    root = tk.Tk()

    serverui = ConnectionUI(root, ServerConn, text='Server')
    tk.Button(serverui, text="Send all a packet", command=lambda: ServerConn.send_all(TestPacket2(5.0))).pack()
    serverui.pack(fill=tk.BOTH, expand=True)

    clientui1 = ConnectionUI(tk.Toplevel(), Client1Conn, text='Client 1')
    tk.Button(clientui1, text="Send a packet", command=lambda: Client1Conn.send(TestPacket(69))).pack()
    clientui1.pack(fill=tk.BOTH, expand=True)

    clientui2 = ConnectionUI(tk.Toplevel(), Client2Conn, text='Client 2')
    tk.Button(clientui2, text="Send a packet", command=lambda: Client2Conn.send(TestPacket2(3.14))).pack()
    clientui2.pack(fill=tk.BOTH, expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()