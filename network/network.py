import pickle
import socket

class Network:
    def __init__(self):
        self.client = None
        self.server =  "172.20.10.2"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.connected = False

    def connect(self):
        if self.connected:
            return

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(self.addr)
            self.connected = True
        except:
            print("Connection failed")

    def disconnect(self):
        if not self.connected:
            return

        try:
            self.client.close()
            self.connected = False
        except Exception as e:
            print("Disconnection failed")

    def is_connected(self):
        return self.connected

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))

        except Exception as e:
            print(f"Błąd komunikacji: {e}")
            return None