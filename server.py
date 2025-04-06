import socket
from _thread import *
import sys

server = "192.168.0.157"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	s.bind((server, port))
except socket.error as e:
	print(str(e))
	sys.exit()

s.listen(2)
print("Waiting for a connection, Server Started")

# Globalny licznik
global_counter = 0
# Lista aktywnych połączeń
clients = []


def threaded_client(conn):
	global global_counter
	clients.append(conn)

	# Na początku wysyłamy aktualny stan licznika do nowego klienta
	try:
		conn.send(str(global_counter).encode())
	except:
		pass

	while True:
		try:
			data = conn.recv(2048).decode()
			if not data:
				print("Disconnected")
				break

			# Próbujemy skonwertować odebrane dane na liczbę.
			# Zakładamy, że klient wysyła nową wartość licznika.
			try:
				new_value = int(data)
				global_counter = new_value
			except ValueError:
				print("Otrzymano nieprawidłowe dane:", data)
				continue

			print("Nowy globalny licznik:", global_counter)
			# Rozsyłamy nowy stan licznika do wszystkich klientów
			for client in clients:
				try:
					client.send(str(global_counter).encode())
				except:
					pass
		except Exception as e:
			print("Exception:", e)
			break

	print("Lost connection")
	clients.remove(conn)
	conn.close()


while True:
	conn, addr = s.accept()
	print("Connected to:", addr)
	start_new_thread(threaded_client, (conn,))
