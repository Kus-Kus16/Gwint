import pickle
import socket

class Network:
    def __init__(self):
        self.client = None
        self.server_ip =  "192.168.1.44"
        self.port = 5555
        self.addr = (self.server_ip, self.port)
        self.connected = False

    def connect(self):
        if self.connected:
            return

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(self.addr)
            self.connected = True
        except (socket.error, ConnectionRefusedError) as e:
            print(f"Connection failed: {e}")
            self.connected = False
            raise ConnectionError

    def disconnect(self):
        if not self.connected:
            return

        try:
            self.client.close()
            self.connected = False
        except socket.error as e:
            print(f"Disconnection failed: {e}")

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))

        except (socket.error, pickle.PickleError, EOFError) as e:
            print(f"Communication error: {e}")
            raise ConnectionError