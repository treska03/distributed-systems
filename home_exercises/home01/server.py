import socket
import threading
from common import MESSAGE_EXIT, MESSAGE_SHUTDOWN, SERVER_ADDR, SERVER_PORT

class ServerThread(threading.Thread):
  def __init__(self, ip: str, port: int, socket: socket.socket):
    threading.Thread.__init__(self)
    self.ip = ip
    self.port = port
    self.socket = socket
    self.clients = []
    self.lock = threading.Lock()
    print(f"[+] Server is running at {ip}:{port}")
  
  def run(self):
    self.socket.listen()
    self.socket.settimeout(1.0)
    print(self.socket)
    while True:
      try:
        conn, (cip, cport) = self.socket.accept()
        client = ClientThread(cip, cport, conn, self)
        self.clients.append(client)
        client.start()
      except socket.timeout:
        continue
      except OSError:
        self._disconnect_clients()
  
  def broadcast(self, message: str, author):
    for client in self.clients:
      if client is not author:
        client.socket.send(bytes(message.encode()))
  
  def remove_client(self, client):
    with self.lock:
      if client in self.clients:
        self.clients.remove(client)
        print(f"[-] Client {client.ip}:{client.port} disconnected.")

  def _disconnect_clients(self):
    clients_copy = [c for c in self.clients]
    for client in clients_copy:
      client.close_client()

  def shutdown_server(self):
    print("[!] Shutting down server...")
    self._disconnect_clients()
    try:
      self.socket.close()
    except OSError:
      pass
    print("[!] Server shut down successfully.")



class ClientThread(threading.Thread):

  def __init__(self, ip: str, port: int, conn: socket.socket, server: ServerThread):
    threading.Thread.__init__(self)
    self.ip = ip
    self.port = port
    self.socket = conn
    self.server = server

    self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp_socket.bind((self.ip, self.port))  # Bind to any available port

    print(f"[+] Client is running at {ip}:{port} with UDP {self.port}")

    self.udp_listener = threading.Thread(target=self.listen_udp)
    self.udp_listener.daemon = True
    self.udp_listener.start()


  def run(self):
    try:
      self.socket.send(bytes(str(self.port).encode()))
      while True:
        msg_raw = self.socket.recv(1024).decode()
        
        if not msg_raw or msg_raw == MESSAGE_EXIT:
          break

        if msg_raw == MESSAGE_SHUTDOWN:
          self.server.shutdown_server()
          break

        message = f"[{self.port}] {msg_raw}"
        print(message)
        
        self.server.broadcast(message=message, author=self)
    except Exception as e:
      print(f"[-] Error in client {self.ip}:{self.port} -> {e}")
    finally:
      self.close_client()
  
  def listen_udp(self):
      """ This should listen for 'U' Option """
      while True:
        try:
          data, addr = self.udp_socket.recvfrom(1024)
          if data:
            print(f"[UDP {self.port}] ART")
            self.server.broadcast(message=data.decode(), author=self)
        except Exception as e:
          print(f"[-] UDP error in client {self.ip}:{self.port} -> {e}")
          break

  def close_client(self):
    self.server.remove_client(self)
    self.socket.close()
    self.udp_socket.close()


def main():
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind((SERVER_ADDR, SERVER_PORT))

  server_thread = ServerThread(SERVER_ADDR, SERVER_PORT, server)

  server_thread.start()

  try:
    while True:
      threading.Event().wait(1)
  except KeyboardInterrupt:
    print("\n[!] Ctrl+C detected, shutting down server...")
  finally:
    server_thread.shutdown_server()
    exit(0)

if __name__ == "__main__":
  main()