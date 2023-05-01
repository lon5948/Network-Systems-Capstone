import socket, struct
import threading, heapq

BUFFER_SIZE = 4096

class QUICServer:
    def __init__(self):
        self.send_buffer = dict()
        self.recv_buffer = dict()
        self.congestion_window = 2

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
        th = threading.Thread(target=self.func)
        th.start()
    
    def func(self):
        """ 
        [SEND BUFFER] { stream_id : { 'data': data, 'next': offset, 'wait_ack': list() }}
        [RECV BUFFER] { stream_id: { finish: True, total_num: 5, payload : { offset: "This is data." }}}
        """
        while True:
            for stream_id, data in self.send_buffer.items():
                for i in range(self.congestion_window):
                    if data['next'] == len(data['data']):
                        offset = data['wait_ack'][0]
                        data['wait_ack'].remove(offset)
                    else:
                        offset = data['next']
                    next_offset = offset + 1500
                    if next_offset > len(data['data']):
                        next_offset = len(data['data'])
                    # stream_id, type, offset, finish, payload
                    stream_frame = struct.pack("i3sii1500s",stream_id, "STR", offset, 0, data['data'][offset:next_offset])
                    self.socket_.sendto(stream_frame, self.client_addr)
                    self.send_buffer[stream_id]['wait_ack'].append(offset)
                    if next_offset != len(data['data']):
                        data['next'] = data['next'] + 1500
            
            self.socket_.settimeout(3)
            while True:
                try:
                    frame, c_addr = self.socket_.recvfrom(2048)
                except socket.timeout as e:
                    self.socket_.gettimeout()   
                    break
                stream_id, type, offset, finish, payload = struct.unpack("i3sii1500s", frame)
                if type == "STR":
                    if stream_id not in self.recv_buffer:
                        self.recv_buffer[stream_id] = {'finish':False, 'total_num':0, 'payload':dict()}
                    if finish == 1:
                        self.recv_buffer[stream_id]['finish'] = True
                        self.recv_buffer[stream_id]['total_num'] = offset/1500 + 1
                    self.recv_buffer[stream_id]['payload'][offset] = payload
                    ack = struct.pack("i3sii1500s",stream_id, "ACK", offset, 0, '0')
                    self.socket_.sendto(ack, self.client_addr)
                elif type == "ACK":
                    count = self.send_buffer[stream_id]['wait_ack'].count(offset)
                    for c in count:
                        self.send_buffer[stream_id]['wait_ack'].remove(offset)
                    if len(self.send_buffer[stream_id]['wait_ack']) == 0:
                        del self.send_buffer[stream_id]

    # call this method to send data, with non-reputation stream_id
    def send(self, stream_id: int, data: bytes):
        self.send_buffer[stream_id] = {'payload':data, 'next':0, 'ack':list()}
    
    # receive a stream, with stream_id
    def recv(self): # -> tuple[int, bytes] stream_id, data
        for stream_id, data in self.recv_buffer.items():
            if data['finish'] == True and len(data['payload']) == data['total_num']:
                ret = ""
                for i in range(data['total_num']):
                    ret += data['payload'][i*1500]
                del self.recv_buffer[stream_id]
                return (stream_id, ret)
                    
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