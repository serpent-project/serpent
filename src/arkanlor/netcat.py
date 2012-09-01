import socket, select

class Netcat:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
    def send(self, content):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.hostname, self.port))
        s.sendall(content)
        #s.shutdown(socket.SHUT_WR)
        while 1:
            data = s.recv(1024)
            if data == "":
                break
            print "Received:", repr(data)
        print "Connection closed."
        s.close()
