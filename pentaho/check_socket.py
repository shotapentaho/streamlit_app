import socket

host = "localhost"
port = 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex((host, port))

if result == 0:
    print("Port is open!")
else:
    print("Port is closed!")

sock.close()