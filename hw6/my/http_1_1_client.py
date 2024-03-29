import socket, time
BUFFER_SIZE = 8192

class HTTPClient(): # For HTTP/1.1
    def __init__(self) -> None:
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.num = 0
        
    def get(self, url, headers=None, stream=False):
        server_ip, server_port, path = self.parse_url(url)
        if path == '/':
            self.client_socket.connect((server_ip, server_port))
        request = f"GET {path} HTTP/1.1\r\nHost: {server_ip}\r\n'Content-Type': 'application/json'\r\n'Content-Length': '0'"
        self.num += 1
        self.client_socket.send(request.encode())
        data = self.client_socket.recv(BUFFER_SIZE).decode()
        data = data.split('\r\n', maxsplit=4)
        response = Response(self.client_socket, stream, self.num)
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
    def __init__(self, socket, stream, num) -> None:
        self.socket = socket
        self.stream = stream
        self.num = num
        # fieleds
        self.version = "" 
        self.status = ""  
        self.headers = {} 
        self.body = b""  
        self.body_length = 0
        self.recv_length = 0
        self.complete = False

    def get_full_body(self): # used for handling short body
        if self.stream or not self.complete:
            return None
        return self.body # the full content of HTTP response body
    
    def get_stream_content(self): # used for handling long body
        if not self.stream or self.complete:
            return None
        if self.body != b"":
            content = self.body
            self.body = b""
            return content
        content = self.get_remain_body() # recv remaining body data from socket
        return content # the part content of the HTTP response body

    def get_remain_body(self):
        content = self.socket.recv(BUFFER_SIZE)
        self.recv_length += len(content)
        if self.recv_length == self.body_length:
            self.complete = True
            if self.num == 4:
                self.socket.close()
        return content