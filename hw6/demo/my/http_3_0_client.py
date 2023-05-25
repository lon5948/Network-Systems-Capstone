import time, threading
from collections import deque
from my.QUIC.quic_client import QUICClient 

def recv_response(quic_client, response, path, server_ip, server_port):
    test = 0
    request = f"GET {path} http {server_ip}:{server_port}"
    request_length = len(request)
    header = (1).to_bytes(1, byteorder='big') + request_length.to_bytes(4, byteorder='big')
    h_frame = header + request.encode()
    quic_client.send(response.stream_id, h_frame, end=True)
    while response.complete == False:
        #print("-------wait to receive data---------")
        time.sleep(0.2)
        stream_id, data, flags = quic_client.recv()
        #print(data)
        types = data[0]
        length = int.from_bytes(data[1:5], byteorder='big')
        payload = data[5:]
        if types == 0:
            #print("data: ", len(payload), length)
            while len(payload) < length:
                time.sleep(0.2)
                sid, d, flags = quic_client.recv()
                payload += d
                #print("again: ", len(payload), length)
            response.contents.append(payload)
            response.complete = flags
            #print("complete: ", flags)
            test += len(payload)
            print("total length: ", test)
        elif types == 1:
            #print("header", len(payload), length)
            #print("get header frame")
            payload = payload.decode()
            #print(payload)
            payload = payload.split('\r\n')
            response.status = payload[0]
            response.headers = {
                payload[1].split(':')[0].lower(): payload[1].split(':')[1],
                payload[2].split(':')[0].lower(): payload[2].split(':')[1],
            }

class HTTPClient(): # For HTTP/3
    def __init__(self) -> None:
        self.quic_client = QUICClient()
        self.num = 0
        self.stream_id = 1
        self.threads = []
        self.responses = []

    def get(self, url, headers=None):
        server_ip, server_port, path = self.parse_url(url)
        if path == '/':
            self.quic_client.connect((server_ip, server_port))
        response = Response(self.stream_id)
        self.responses.append(response)
        print(self.stream_id)
        self.stream_id += 2
        thread = threading.Thread(target=recv_response, args=(self.quic_client, response, path, server_ip, server_port))
        self.threads.append(thread) 
        thread.start()
        return self.responses[-1]
    
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
        begin_time = time.time()
        while self.status == "Not yet":
            if time.time() - begin_time > 5:
                return None
        return self.headers
    
    def get_full_body(self): # used for handling short body
        while not self.complete:
            time.sleep(0.01)
        while len(self.contents) > 0:
            self.body += self.contents.popleft()
        return self.body # the full content of HTTP response body
    
    def get_stream_content(self): # used for handling long body
        while not self.complete:
            time.sleep(0.01)
        if len(self.contents) == 0: # contents is a buffer, busy waiting for new content
            return None
        content = self.contents.popleft() # pop content from deque
        return content # the part content of the HTTP response body