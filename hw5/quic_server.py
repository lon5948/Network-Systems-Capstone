import socket

class QUICServer:
    def __init__(self):
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # this method is to open the socket 
    def listen(self, socket_addr):
        self.socket_.bind(socket_addr)

    # this method is to indicate that the client can connect to the server now
    def accept(self):
        hello, client_addr = self.socket_.recvfrom(1024)
        print("Message:", hello.decode("utf-8"), "from", client_addr)
        hello_ack = "Hello ACK"
        self.socket_.sendto(hello_ack.encode("utf-8"), client_addr)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.bind(client_addr)
    
    # call this method to send data, with non-reputation stream_id
    def send(self, stream_id: int, data: bytes):
        pass
    
    # receive a stream, with stream_id
    def recv(self): # -> tuple[int, bytes] stream_id, data
        pass
    
    # close the connection and the socket
    def close(self):
        self.socket_.close()

if __name__ == "__main__":
    server = QUICServer()
    server.listen(("", 30000))
    server.accept()
    server.send(1, b"SOME DATA, MAY EXCEED 1500 bytes")
    recv_id, recv_data = server.recv()
    print(recv_data.decode("utf-8")) # Hello Server!
    server.close() 