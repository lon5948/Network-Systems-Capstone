import socket

# Question:
# get_full_body(), get_stream_content() should modify or not ?
# does server need to consider param stream
# set socket time 5
# how to check the last packet(param complete)

class HTTPClient(): # For HTTP/1.X
    def get(self, url, headers=None, stream=False):
        # Send the request and return the response (Object)
        # url = "http://127.0.0.1:8080/static/xxx.txt"
        # If stream=True, the response should be returned immediately after the full headers have been received.
        server_ip, server_port, path = self.parse_url(url)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        print("Client is conneted.")
        request = f"GET {path} HTTP/1.0\r\nHost: {server_ip}\r\n'Content-Type': 'application/json'\r\n'Content-Length': '0'"
        client_socket.send(request.encode())
        print("Client finish to send request.")
        data = client_socket.recv(4096).decode()
        print("Client receive the response")
        data = data.split('\r\n')
        response = Response(client_socket, stream)
        response.version = data[0].split(' ')[0]
        print("response.version", response.version)
        response.status = data[0][8:]
        print("response.status", response.status)
        response.headers = { data[1].split(' ')[0].lower()[:-1]: data[1].split(' ')[1].lower() }
        print("response.headers", response.headers)
        response.body_length = int(data[2].split(' ')[1])
        print("response.body_length", response.body_length)
        response.recv_length += len(data[4])
        print("response.recv_length", response.recv_length)
        if response.recv_length == response.body_length:
            response.complete = True
        response.body = data[4].encode()
        client_socket.close()
        print("Client is closed.")
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
    def __init__(self, socket, stream) -> None:
        self.socket = socket
        self.stream = stream
        # fieleds
        self.version = "" # e.g. "HTTP/1.0"
        self.status = ""  # e.g., "200 OK"
        self.headers = {} # e.g., {content-type: application/json}
        self.body = b""  # e.g. "{'id': '123', 'key':'456'}"
        self.body_length = 0
        self.recv_length = 0
        self.complete = False
        self.__reamin_bytes = b""

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
        content = self.socket.recv(4096)
        self.recv_length += len(content)
        if self.recv_length == self.body_length:
            self.complete = True
        return content.decode()

