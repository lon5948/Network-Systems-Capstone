import socket, struct
import threading, heapq

class QUICServer:
    def __init__(self):
        self.send_window_size = 10


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
    
    def create_stream(self, stream_id, data):
        length = len(data)
        windows = 0
        packet_id = 0
        ack_id = 0
        i = 0
        packets = dict()
        """ streamID, packet_id, offset, finish, payload """
        while True:
            if i < length and windows < self.send_window_size:
                if i + 1500 < length:
                    stream_frame = struct.pack("iiii1500s",stream_id, packet_id, i, 0, data[i:i+1500])
                else:
                    stream_frame = struct.pack("iiii1500s",stream_id, packet_id, i, 1, data[i:length])
                packets[packet_id] = stream_frame
                self.socket_.sendto(stream_frame, self.client_addr)
                i += 1500
                packet_id += 1
                windows += 1
            if windows == self.send_window_size:
                ack_frame, c_addr = self.socket_.recvfrom(2048)
                id, ack = struct.unpack("i3s", ack_frame)
                if ack.decode("utf-8") != "ACK":
                    print("[ERROR] ACK IS INCORRECT")
                    exit(0)
                if id == ack_id:
                    ack_id += 1
                    windows -= 1
                else:
                    self.socket_.sendto(packets[packet_id], self.client_addr)
    
    # call this method to send data, with non-reputation stream_id
    def send(self, stream_id: int, data: bytes):
        s_th = threading.Thread(target=self.create_stream, args=(stream_id, data))
        s_th.start()

    def recv_packet(self):
        flag = False
        total_num = 0
        d = dict()
        while True:
            stream_frame, c_addr = self.socket_.recvfrom(2048)
            stream_id, packet_id, offset, finish, payload = struct.unpack("iiii1500s", stream_frame)
            total_num = max(total_num, offset/1500 + 1)
            d[offset] = payload
            ack_frame = struct.pack("i3s", packet_id, "ACK")
            self.socket_.sendto(ack_frame, self.client_addr)
            if finish == 1:
                flag = True
            if flag and len(d) == total_num:
                break
        data = ""
        for i in range(total_num):
            data += d[i*1500]
        return (stream_id, data)
    
    # receive a stream, with stream_id
    def recv(self): # -> tuple[int, bytes] stream_id, data
        r_th = threading.Thread(target=self.recv_packet)
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