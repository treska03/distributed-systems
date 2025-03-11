import socket
import struct
from threading import Thread

from ascii_art import ART
from common import MESSAGE_EXIT, MULTICAST_ADDR, MULTICAST_PORT, SERVER_ADDR, SERVER_PORT

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_ADDR, SERVER_PORT))
id = client.recv(1024).decode()
print("Your id is " + id)

client_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

multicast_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
multicast_recv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
multicast_recv.bind(('', MULTICAST_PORT))
group = socket.inet_aton(MULTICAST_ADDR)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
multicast_recv.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

multicast_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
multicast_send.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

def print_group_chat():
  while True:
    try:
      data, (ip, port) = multicast_recv.recvfrom(1024)
      print(data.decode())
    except OSError:
      break  

def print_chat():
  while True:
    try:
      print(client.recv(1024).decode())
    except OSError:
      break

def close_client():
  client.close()
  client_udp.close()
  multicast_recv.close()
  multicast_send.close()
  exit()

def send_to_chat():
  try:
    while True:
      msg = input()
      
      if msg == MESSAGE_EXIT:
        print("exit message")
        close_client()
      
      if msg == "U":
        client_udp.sendto(bytes(ART.encode()), (SERVER_ADDR, int(id)))
      elif msg == "M":
        multicast_send.sendto(bytes(ART.encode()), (MULTICAST_ADDR, MULTICAST_PORT))
      else:
        client.send(bytes(msg.encode()))

  except Exception as e:
    print(e)
    exit()


t1 = Thread(target=print_chat)
t2 = Thread(target=send_to_chat)
t3 = Thread(target=print_group_chat)
t1.start()
t2.start()
t3.start()
t1.join()
t2.join()
t3.join()
