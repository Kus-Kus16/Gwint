import logging
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
            self.connected = False
            raise ConnectionError(f"Connection failed: {str(e)}")

    def disconnect(self):
        if not self.connected:
            return

        try:
            self.client.close()
            self.connected = False
        except socket.error as e:
            logging.info(print(f"Disconnecting failed: {str(e)}"))

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(8192))

        except (socket.error, pickle.PickleError, EOFError) as e:
            raise ConnectionError(f"Communication error: {str(e)}")