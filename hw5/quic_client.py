import socket, struct, threading, time

BUFFER_SIZE = 8192

class QUICClient:
    def __init__(self):
        self.send_buffer = dict()
        self.recv_buffer = dict()
        self.congestion_window = 4
        self.receive_window = 30
        self.sending_flag = True

    # connect to the specific server
    def connect(self, socket_addr): 
        self.server_addr = socket_addr
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = b"Client Hello" 
        hello = struct.pack("i12s", self.receive_window, msg)
        self.socket_.sendto(hello, self.server_addr)
        hello_ack, server_addr = self.socket_.recvfrom(2048)
        print("Message:", hello_ack.decode("utf-8"), "from", self.server_addr)
        self.threading = threading.Thread(target=self.func)
        self.threading.start()

    def func(self):
        """ 
        [SEND BUFFER] { stream_id : { 'payload': data, 'next': offset, 'wait_ack': list() }}
        [RECV BUFFER] { stream_id: { finish: True, total_num: 5, payload : { offset: "This is data." }}}
        """
        while True:
            if self.sending_flag:
                num = 0
                send_packet = b""
                for stream_id, data in self.send_buffer.items():
                    if data['next'] == len(data['payload']):
                        offset = data['wait_ack'][0]
                        data['wait_ack'].remove(offset)
                    else:
                        offset = data['next']
                    next_offset = offset + 1500
                    send_finish = 0
                    if next_offset > len(data['payload']):
                        next_offset = len(data['payload'])
                        send_finish = 1
                    # stream_id, type, offset, finish, payload
                    stream_frame = struct.pack("i3sii1500s",stream_id, b"STR", offset, send_finish, data['payload'][offset:next_offset])
                    send_packet += stream_frame
                    self.send_buffer[stream_id]['wait_ack'].append(offset)
                    data['next'] = next_offset
                    num += 1
                    if num >= self.congestion_window:
                        break
                if num > 0:
                    send_packet = str(num).encode('utf-8') + send_packet
                    self.socket_.sendto(send_packet, self.server_addr)
                    

            self.socket_.settimeout(3)
            ack_num = 0
            while True:
                try:
                    recv_packet, c_addr = self.socket_.recvfrom(BUFFER_SIZE)
                except socket.timeout as e:
                    self.socket_.gettimeout()   
                    break
                recv_packet_num = recv_packet[0] - 48
                for i in range(recv_packet_num):
                    stream_id, ftype, offset, finish, payload = struct.unpack("i3sii1500s", recv_packet[1516*i+1:1516*(i+1)+1])
                    ftype = ftype.decode('utf-8')
                    if ftype == "STR":
                        if stream_id not in self.recv_buffer:
                            self.recv_buffer[stream_id] = {'finish':False, 'total_num':0, 'payload':dict()}
                        if finish == 1:
                            self.recv_buffer[stream_id]['finish'] = True
                            self.recv_buffer[stream_id]['total_num'] = int(offset/1500) + 1
                        self.recv_buffer[stream_id]['payload'][offset] = payload
                        total_recv_num = 0
                        for v in self.recv_buffer.values():
                            total_recv_num += v['total_num']
                        if total_recv_num >= self.receive_window:
                            ack = struct.pack("i3sii1500s", stream_id, b"ACK", offset, 1, b"0")
                        else:
                            ack = struct.pack("i3sii1500s", stream_id, b"ACK", offset, 0, b"0")
                        ack = b"1" + ack
                        self.socket_.sendto(ack, self.server_addr)
                    elif ftype == "ACK":
                        self.sending_flag = (finish==0)
                        count = self.send_buffer[stream_id]['wait_ack'].count(offset)
                        ack_num += 1
                        for c in range(count):
                            self.send_buffer[stream_id]['wait_ack'].remove(offset)
                        if len(self.send_buffer[stream_id]['wait_ack']) == 0:
                            del self.send_buffer[stream_id]
                    
            if num > 0 and float(ack_num)/num < 0.6:
                self.congestion_window = int(self.congestion_window/2)
                    
    # call this method to send data, with non-reputation stream_id
    def send(self, stream_id: int, data: bytes):
        self.send_buffer[stream_id] = {'payload':data, 'next':0, 'wait_ack':list()}

    # receive a stream, with stream_id
    def recv(self): 
        while True:
            for stream_id, data in self.recv_buffer.items():
                if data['finish'] == True and len(data['payload']) == data['total_num']:
                    ret = b""
                    for i in range(data['total_num']):
                        ret += data['payload'][i*1500]
                    del self.recv_buffer[stream_id]
                    return (stream_id, ret)
            time.sleep(1)
    
    # close the connection and the socket
    def close(self):
        self.threading.join()
        self.socket_.close()

if __name__ == "__main__":
    client = QUICClient()
    client.connect(("127.0.0.1", 30000))
    recv_id, recv_data = client.recv()
    print(recv_data.decode("utf-8")) # SOME DATA, MAY EXCEED 1500 bytes
    client.send(2, b"Hello Server!")
    client.close()