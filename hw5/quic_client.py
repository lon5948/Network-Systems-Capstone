import socket

class QUICClient:
    def __init__(self):
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # connect to the specific server
    def connect(self, socket_addr): 
        hello = "Client Hello" 
        self.socket_.sendto(hello.encode("utf-8"), socket_addr)
        hello_ack, server_addr = self.socket_.recvfrom(1024)
        print("Message:", hello_ack.decode("utf-8"), "from", server_addr)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
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
    client = QUICClient()
    client.connect(("127.0.0.1", 30000))
    recv_id, recv_data = client.recv()
    print(recv_data.decode("utf-8")) # SOME DATA, MAY EXCEED 1500 bytes
    client.send(2, b"Hello Server!")
    client.close()