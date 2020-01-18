import socket 
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5000      # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'GET / HTTP/1.0\n\nHost: 127.0.0.1\n\n')
    try:
     for i in range(10):
      data = s.recv(1)
      print(data)
    except Exception:
     pass
	

print('Received', repr(data))
