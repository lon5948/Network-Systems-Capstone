import socket, struct
import threading, heapq

def create_stream(stream_id, data, client_addr, server_addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(client_addr)
    length = len(data)
    """ streamID, offset, finish, payload"""
    for i in range(0, length, 1500):
        if i + 1500 < length:
            frame = struct.pack("iii1500s",stream_id, i, 0, data[i:i+1500])
        else:
            frame = struct.pack("iii1500s",stream_id, i, 1, data[i:length])
        s.sendto(frame, server_addr)
        ack, s_addr = s.recvfrom(2048)
        if ack.decode("utf-8") != "ACK":
            print("[ERROR] ACK FROM SERVER IS INCORRECT")
            exit(0)

def recv_packet(client_addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(client_addr)
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

class QUICClient:
    # connect to the specific server
    def connect(self, socket_addr): 
        self.addr = socket_addr
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hello = "Client Hello" 
        self.socket_.sendto(hello.encode("utf-8"), socket_addr)
        hello_ack, server_addr = self.socket_.recvfrom(2048)
        self.server_addr = server_addr
        print("Message:", hello_ack.decode("utf-8"), "from", server_addr)
    
    # call this method to send data, with non-reputation stream_id
    def send(self, stream_id: int, data: bytes):
        s_th = threading.Thread(target=create_stream, args=(stream_id, data, self.addr, self.server_addr))
        s_th.start()
    
    # receive a stream, with stream_id
    def recv(self): # -> tuple[int, bytes] stream_id, data
        r_th = threading.Thread(target=recv_packet, args=(self.addr))
        r_th.start()
    
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