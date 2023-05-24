import socket, threading, os, struct, time
CHUNK_SIZE = 4096
BUFFER_SIZE = 8192

def send_response(request_frame, client_socket, directory):
    header = request_frame[0:9]
    print(len(header))
    _, _, request_length, types, flags, _, _, _, stream_id = struct.unpack("BBBBBBBBB", header)
    
    request = request_frame[9:9+request_length].decode().split(' ')
    request_path = request[1]
    if request_path == "/":
        d_payload = "<html><header></header><body>"
        files = os.listdir(directory)
        for i in range(3):
            d_payload += f"<a href='/static/{files[i]}'>{files[i]}</a>"
            if i == 2:
                break
            d_payload += "<br/>"
        d_payload += "</body></html>"
        d_frame = struct.pack("BBBBBBBBB", 0x00, 0x00, len(d_payload), 0, 1, 0x00, 0x00, 0x00, stream_id) + d_payload.encode()

        h_payload = f"200 OK\r\nContent-Type:text/html\r\nContent-Length:{len(d_payload)}"
        h_frame = struct.pack("BBBBBBBBB", 0x00, 0x00, len(h_payload), 1, 1, 0x00, 0x00, 0x00, stream_id) + h_payload.encode()

        client_socket.send(h_frame)
        client_socket.send(d_frame)

    elif request_path.startswith('/static'):
        full_path = directory + request_path[7:]
        file_size = os.path.getsize(full_path)

        h_payload = f"200 OK\r\nContent-Type:text/html\r\nContent-Length:{file_size}"
        h_frame = struct.pack("BBBBBBBBB", 0x00, 0x00, len(h_payload), 1, 1, 0x00, 0x00, 0x00, stream_id) + h_payload.encode()
        client_socket.send(h_frame)
        with open(full_path, "rb") as file:
            flag = True
            complete = 0
            while complete == 0:
                if flag:
                    d_payload = file.read(CHUNK_SIZE)
                    flag = False
                else:
                    d_payload = d_payload_next
                d_payload_next = file.read(CHUNK_SIZE)
                if not d_payload_next:
                    complete = 1
                d_frame = struct.pack("BBBBBBBBB", 0x00, 0x00, len(d_payload), 0, complete, 0x00, 0x00, 0x00, stream_id) + d_payload
                client_socket.send(d_frame)
    else:
        d_payload = "<html><header></header><body></body></html>"
        d_frame = struct.pack("BBBBBBBBB", 0x00, 0x00, len(d_payload), 0, 1, 0x00, 0x00, 0x00, stream_id) + d_payload.encode()
        h_payload = f"404 Not Found\r\nContent-Type:text/html\r\nContent-Length:{len(d_payload)}"
        h_frame = struct.pack("BBBBBBBBB", 0x00, 0x00, len(h_payload), 1, 1, 0x00, 0x00, 0x00, stream_id) + h_payload.encode()
        client_socket.send(h_frame)
        client_socket.send(d_frame)
        

class HTTPServer():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        self.server_addr = (host, port)
        self.server_socket = None
        self.threads = []
        
    def run(self):
        # Create the server socket and start accepting connections.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_addr)
        self.server_socket.listen(1)
        self.client_socket, client_addr = self.server_socket.accept()
        print(f"{client_addr} is connected.")
        self.client_socket.settimeout(5)
        while True:
            try:
                request_frame = self.client_socket.recv(BUFFER_SIZE)
                if len(request_frame) == 0:
                    print("Finish")
                    break
                thread = threading.Thread(target=send_response, args=(request_frame, self.client_socket, self.directory, ))
                self.threads.append(thread)
                thread.start()
            except socket.timeout:
                continue
            except socket.error as e:
                print('[SOCKET ERROR]', e)
                break
        for th in self.threads:
            th.join()

    def set_static(self, path):
        # Set the static directory so that when the client sends a GET request to the resource
        # "/static/<file_name>", the file located in the static directory is sent back in the response.
        self.directory = path

    def close(self):
        # Close the server socket.
        self.server_socket.close()
        self.client_socket.close()
