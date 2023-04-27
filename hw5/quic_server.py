import socket, struct
import threading, heapq

def create_stream(stream_id, data, server_addr, client_addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(server_addr)
    length = len(data)
    """ streamID, offset, finish, payload"""
    for i in range(0, length, 1500):
        if i + 1500 < length:
            frame = struct.pack("iii1500s",stream_id, i, 0, data[i:i+1500])
        else:
            frame = struct.pack("iii1500s",stream_id, i, 1, data[i:length])
        s.sendto(frame, client_addr)
        ack, c_addr = s.recvfrom(2048)
        if ack.decode("utf-8") != "ACK":
            print("[ERROR] ACK IS INCORRECT")
            exit(0)

def recv_packet(server_addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(server_addr)
    flag = False
    frame_num = 0
    total_num = 0
    d = dict()
    while True:
        frame, c_addr = s.recvfrom(2048)
        stream_id, offset, finish, payload = struct.unpack("iii1500s", frame)
        frame_num += 1
        total_num = max(total_num, offset/1500 + 1)
        d[offset] = payload
        if finish == 1:
            flag = True
        if flag and frame_num == total_num:
            break
    data = ""
    for i in range(total_num):
        data += d[i*1500]
    return (stream_id, data)


class QUICServer:
    # this method is to open the socket 
    def listen(self, socket_addr):
        self.addr = socket_addr
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_.bind(socket_addr)
    
    # this method is to indicate that the client can connect to the server now
    def accept(self):
        hello, client_addr = self.socket_.recvfrom(2048)
        print("Message:", hello.decode("utf-8"), "from", client_addr)
        hello_ack = "Hello ACK"
        self.socket_.sendto(hello_ack.encode("utf-8"), client_addr)
        self.client_addr = client_addr
    
    # call this method to send data, with non-reputation stream_id
    def send(self, stream_id: int, data: bytes):
        s_th = threading.Thread(target=create_stream, args=(stream_id, data, self.addr, self.client_addr))
        s_th.start()
        
    # receive a stream, with stream_id
    def recv(self): # -> tuple[int, bytes] stream_id, data
        r_th = threading.Thread(target=recv_packet, args=(self.addr))
        r_th.start()
    
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