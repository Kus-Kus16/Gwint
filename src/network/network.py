import logging
import pickle
import socket

from src.view import settings


class Network:
    def __init__(self):
        self.client = None
        self.port = 5555
        self.server_ip = settings.load_setting("ip")
        self.addr = (self.server_ip, self.port)
        self.connected = False
        settings.register_observer(self)

    def connect(self):
        if self.connected:
            return

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(5)
            self.client.connect(self.addr)
            self.client.settimeout(None)
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

    @property
    def server_ip(self):
        return self._server_ip

    @server_ip.setter
    def server_ip(self, new_ip):
        self._server_ip = new_ip
        self.addr = (self._server_ip, self.port)

    def on_settings_update(self):
        self.server_ip = settings.load_setting("ip")
        if self.connected:
            self.disconnect()
            self.connect()
