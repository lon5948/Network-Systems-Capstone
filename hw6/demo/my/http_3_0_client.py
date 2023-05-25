import time, threading
from collections import deque
from my.QUIC.quic_client import QUICClient 

def recv_response(client):
    print("enter thread")
    br = True
    while br:
        br = False
        time.sleep(0.2)
        print("----------waite to receive----------")
        sid, data, flags = client.quic_client.recv()
        print("receive ok")
        if flags == False and len(client.responses[sid].contents) > 0 and len(client.responses[sid].contents[-1]) < 4096:
            client.responses[sid].contents[-1] += data
            client.responses[sid].complete = flags
            client.test[sid] += len(data)
            print(sid, "total length: ", client.test[sid])
            continue
        types = data[0]
        length = int.from_bytes(data[1:5], byteorder='big')
        payload = data[5:]
        if types == 0:
            client.responses[sid].contents.append(payload)
            client.responses[sid].complete = flags
            #print("complete: ", flags)
            client.test[sid] += len(payload)
            print(sid, "total length: ", client.test[sid])
        elif types == 1:
            #print("header", len(payload), length)
            #print("get header frame")
            payload = payload.decode()
            #print(payload)
            payload = payload.split('\r\n')
            client.responses[sid].status = payload[0]
            client.responses[sid].headers = {
                payload[1].split(':')[0].lower(): payload[1].split(':')[1],
                payload[2].split(':')[0].lower(): payload[2].split(':')[1],
            }

        for _, resp in client.responses.items():
            if len(client.responses) < 4 or resp.complete == False:
                br = True
                break

class HTTPClient(): # For HTTP/3
    def __init__(self) -> None:
        self.quic_client = QUICClient()
        self.num = 0
        self.stream_id = 1
        self.responses = {}
        self.test = {1: 0, 3: 0, 5: 0, 7: 0}
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
        response = Response(self.stream_id)
        self.responses[self.stream_id] = response
        print(self.stream_id)
        self.stream_id += 2
        print("return response")
        return response
    
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
        while not self.complete and len(self.contents) == 0:
            time.sleep(0.01)
        if len(self.contents) == 0: # contents is a buffer, busy waiting for new content
            return None
        content = self.contents.popleft() # pop content from deque
        return content # the part content of the HTTP response body