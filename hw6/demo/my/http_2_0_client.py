import socket, time
from collections import deque
BUFFER_SIZE = 8192

class HTTPClient(): # For HTTP/2
    def __init__(self) -> None:
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get(self, url, headers=None):
        server_ip, server_port, path = self.parse_url(url)
        if path == '/':
            self.client_socket.connect((server_ip, server_port))
        request = f"GET {path} http {server_ip}:{server_port}"
        self.client_socket.send(request.encode())
        data = self.client_socket.recv(BUFFER_SIZE).decode()
        data = data.split('\r\n', maxsplit=4)
        response = Response(self.client_socket, self.num)
        response.version = data[0].split(' ')[0]
        response.status = data[0][8:]
        response.headers = { data[1].split(' ')[0].lower()[:-1]: data[1].split(' ')[1].lower() }
        response.body_length = int(data[2].split(' ')[1])
        response.body += data[4].encode()
        response.recv_length += len(response.body)
        if response.recv_length == response.body_length:
            response.complete = True
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