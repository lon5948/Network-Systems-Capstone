import time, threading
from collections import deque
from my.QUIC.quic_client import QUICClient 

def recv_response(client):
    print("enter thread")
    test = {1: 0, 3: 0, 5: 0, 7: 0}
    remain_lens = {1: -1, 3: -1, 5: -1, 7: -1}
    stop = {1: False, 3: False, 5: False, 7: False}
    while True:
        #time.sleep(0.01)
        sid, data, flags = client.quic_client.recv()
        if flags:
            stop[sid] = True
            client.responses[sid].complete = True
        if remain_lens[sid] == -1:
            print(sid, "header")
            types = data[0]
            length = int.from_bytes(data[1:5], byteorder='big')
            remain_lens[sid] = 0
            payload = data[5:]
            payload = payload.decode()
            payload = payload.split('\r\n')
            client.responses[sid].status = payload[0]
            client.responses[sid].headers = {
                payload[1].split(':')[0].lower(): payload[1].split(':')[1],
                payload[2].split(':')[0].lower(): payload[2].split(':')[1],
            }
        elif remain_lens[sid] == 0:
            types = data[0]
            length = int.from_bytes(data[1:5], byteorder='big')
            payload = data[5:]
            remain_lens[sid] = length - len(payload)
            client.responses[sid].contents.append(payload)
            test[sid] += len(payload)
            print(test)
        elif len(data) <= remain_lens[sid]:
            payload = data
            remain_lens[sid] -= len(payload)
            client.responses[sid].contents.append(payload)
            test[sid] += len(payload)
            print(test)
        else:
            client.responses[sid].contents.append(data[:remain_lens[sid]])
            test[sid] += remain_lens[sid]
            print(test)
            d = data[remain_lens[sid]:]
            types = d[0]
            length = int.from_bytes(d[1:5], byteorder='big')
            payload = d[5:]
            remain_lens[sid] = length - len(payload)
            client.responses[sid].contents.append(payload)
            test[sid] += len(payload)
            print(test)
        if(all(st for _, st in stop.items())):
            break
    print("break thread")
        

class HTTPClient(): # For HTTP/3
    def __init__(self) -> None:
        self.quic_client = QUICClient()
        self.num = 0
        self.stream_id = 1
        self.responses = {}
        for i in range(1, 9, 2):
            self.responses[i] = Response(i)
        self.thread = threading.Thread(target=recv_response, args=(self,))
        self.thread.start()

    def get(self, url, headers=None):
        server_ip, server_port, path = self.parse_url(url)
        if path == '/':
            self.quic_client.connect((server_ip, server_port))
        request = f"GET {path} http {server_ip}:{server_port}"
        request_length = len(request)
        header = (1).to_bytes(1, byteorder='big') + request_length.to_bytes(4, byteorder='big')
        h_frame = header + request.encode()
        self.quic_client.send(self.stream_id, h_frame, end=True)
        # response = Response(self.stream_id)
        #self.responses[self.stream_id] = response
        print(self.stream_id)
        s = self.stream_id
        self.stream_id += 2
        return self.responses[s]
    
    def parse_url(self, url):
        if url.startswith("http://"):
            url = url[7:]
        elif url.startswith("https://"):
            url = url[8:]
        url = url.split(':')
        ip = url[0]
        port = url[1].split('/')[0]
        path = url[1][len(port):]
        return ip, int(port), path
    
class Response():
    def __init__(self, stream_id, headers = {}, status = "Not yet") -> None:
        self.stream_id = stream_id
        self.headers = headers
        self.status = status
        self.body = b""
        self.contents = deque()
        self.complete = False
        
    def get_headers(self):
        while self.status == "Not yet" or not self.complete:
            time.sleep(0.01)
        return self.headers
    
    def get_full_body(self): # used for handling short body
        while not self.complete:
            time.sleep(0.01)
        while len(self.contents) > 0:
            self.body += self.contents.popleft()
        return self.body # the full content of HTTP response body
    
    def get_stream_content(self): # used for handling long body
        while not self.complete and len(self.contents) == 0:
            time.sleep(0.01)
        if len(self.contents) == 0: # contents is a buffer, busy waiting for new content
            return None
        content = self.contents.popleft() # pop content from deque
        return content # the part content of the HTTP response body
        