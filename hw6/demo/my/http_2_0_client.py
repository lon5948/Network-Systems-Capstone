import socket, time, struct
from collections import deque

class HTTPClient(): # For HTTP/2
    def __init__(self) -> None:
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.num = 0
        self.stream_id = 1

    def get(self, url, headers=None):
        server_ip, server_port, path = self.parse_url(url)
        if path == '/':
            self.client_socket.connect((server_ip, server_port))
        request = f"GET {path} http {server_ip}:{server_port}"
        request_length = len(request)
        # payload length, type, flags, R, stream_id
        header = struct.pack("BBBBBBBBB", 0x00, 0x00, request_length, 1, 1, 0x00, 0x00, 0x00, self.stream_id)
        h_frame = header + request.encode()
        self.client_socket.send(h_frame)
        response = Response(self.stream_id)
        self.stream_id += 2
        while response.complete == False:
            data = self.client_socket.recv(9)
            _, _, length, types, flags, _, _, _, stream_id = struct.unpack("BBBBBBBBB", data)
            payload = b""
            while len(payload) != length:
                payload += self.client_socket.recv(length-len(payload))
            if types == 0:
                response.contents.append(payload)
                if flags == 1:
                    response.complete = True
            elif types == 1:
                payload = payload.decode()
                payload = payload.split('\r\n')
                response.status = payload[0]
                response.headers = {
                    payload[1].split(':')[0].lower(): payload[1].split(':')[1],
                    payload[2].split(':')[0].lower(): payload[2].split(':')[1],
                }
        self.num += 1
        if self.num == 4:
            self.client_socket.close()
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
        begin_time = time.time()
        while not self.complete:
            if time.time() - begin_time > 5:
                return None
        if len(self.body) > 0:
            return self.body
        while len(self.contents) > 0:
            self.body += self.contents.popleft()
        return self.body # the full content of HTTP response body
    
    def get_stream_content(self): # used for handling long body
        begin_time = time.time()
        while len(self.contents) == 0: # contents is a buffer, busy waiting for new content
            if self.complete or time.time() - begin_time > 5: # if response is complete or timeout
                return None
        content = self.contents.popleft() # pop content from deque
        return content # the part content of the HTTP response body