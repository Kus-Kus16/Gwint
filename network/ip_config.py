import os

IP_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'userdata', 'ip.txt')
IP_FILE_PATH = os.path.abspath(IP_FILE_PATH)

def load_ip():
    try:
        with open(IP_FILE_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "127.0.0.1"  # domyślne IP

def save_ip(ip):
    with open(IP_FILE_PATH, 'w') as f:
        f.write(ip)
