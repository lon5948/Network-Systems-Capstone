import socket, time, struct, threading
from collections import deque
BUFFER_SIZE = 8192

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
        header = struct.pack("iiiii", request_length, 1, 1, 0, self.stream_id)
        h_frame = header + request.encode()
        self.client_socket.send(h_frame)
        self.stream_id += 2

        response = Response(self.stream_id)
        while response.complete == False:
            data = self.client_socket.recv(BUFFER_SIZE)
            length, types, flags, R, stream_id = struct.unpack("iiiii", data[0:20])
            print(length, types, flags, R, stream_id)
            print("data length", len(data))
            payload = data[20:20+length].decode()
            if types == 0:
                response.contents.append(payload.encode())
                if flags == 1:
                    response.complete = True
            elif types == 1:
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
          if self.complete or time.time()-begin_time > 5: # if response is complete or timeout
              return None
        content = self.contents.popleft() # pop content from deque
        return content # the part content of the HTTP response body