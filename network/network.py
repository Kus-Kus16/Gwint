import pickle
import socket

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.0.157"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
        except:
            print("Connection failed")


    def send(self, data):
        try:
            self.client.send(str.encode(data))

            received_data = self.client.recv(2048*2)

            try:
                return pickle.loads(received_data)

            except pickle.UnpicklingError:
                # Jeśli nie udało się deserializować, potraktuj jako zwykły string
                return received_data.decode()

        except Exception as e:
            print(f"Błąd komunikacji: {e}")
            return None