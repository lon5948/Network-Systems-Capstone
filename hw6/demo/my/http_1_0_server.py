import socket, threading, sys, os
CHUNK_SIZE = 4096
BUFFER_SIZE = 8192

def receive_data(client_socket, directory):
    while True:
        try:
            request = client_socket.recv(BUFFER_SIZE)
            if len(request) == 0:
                client_socket.close()
                print("Client is closed.")
                break
            request = request.decode().split(' ')
            request_path = request[1]
            if request_path == "/":
                response_status = b"HTTP/1.0 200 OK\r\n"
                response_content_type = b"Content-Type: text/html\r\n"
                response_body = "<html><header></header><body>"
                files = os.listdir(directory)
                for i in range(3):
                    response_body += f"<a href='/static/{files[i]}'>{files[i]}</a>"
                    if i == 2:
                        break
                    response_body += "<br/>"
                response_body += "</body></html>"
                response_body = response_body.encode()
                response_content_length = f"Content-Length: {len(response_body)}\r\n\r\n".encode()
                response = response_status + response_content_type + response_content_length + response_body
                client_socket.send(response)
            elif request_path.startswith('/static'):
                full_path = directory + request_path[7:]
                file_size = os.path.getsize(full_path)
                response_status = b"HTTP/1.0 200 OK\r\n"
                response_content_type = b"Content-Type: text/plain\r\n"
                with open(full_path, "rb") as file:
                    flag = True
                    while True:
                        response_body = file.read(CHUNK_SIZE)
                        if not response_body:
                            break
                        if flag:
                            response_content_length = f"Content-Length: {file_size}\r\n\r\n".encode()
                            response = response_status + response_content_type + response_content_length + response_body
                            flag = False
                        else:
                            response = response_body
                        client_socket.send(response)
            else:
                response_status = b"HTTP/1.0 404 Not Found\r\n"
                response_content_type = b"Content-Type: text/html\r\n"
                response_body = "<html><header> </header><body></body></html>".encode()
                response_content_length = f"Content-Length: {len(response_body)}\r\n\r\n".encode()
                response = response_status + response_content_type + response_content_length + response_body
                client_socket.send(response)
        except socket.timeout:
            continue
        except socket.error as e:
            print('[SOCKET ERROR]', e)
            break

class HTTPServer():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        self.server_addr = (host, port)
        self.server_socket = None
        self.threads = []
    def run(self):
        # Create the server socket and start accepting connections.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_addr)
        self.server_socket.listen(10)
        while True:
            try:
                self.client_socket, client_addr = self.server_socket.accept()
                print(f"{client_addr} is connected.")
                self.client_socket.settimeout(5)
                thread = threading.Thread(target=receive_data, args=(self.client_socket, self.directory, ))
                self.threads.append(thread)
                thread.start()
                thread.join()
            except BlockingIOError:
                alive_flag = True
                for th in self.threads:
                    if th.is_alive():
                        alive_flag = False
                        break
                if len(self.threads) > 0 and alive_flag:
                    break
        print('finish')

    def set_static(self, path):
        # Set the static directory so that when the client sends a GET request to the resource
        # "/static/<file_name>", the file located in the static directory is sent back in the response.
        self.directory = path

    def close(self):
        # Close the server socket.
        self.server_socket.close()
        self.client_socket.close()
