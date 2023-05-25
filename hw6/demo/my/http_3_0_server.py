from my.QUIC.quic_server import QUICServer
import threading, os

CHUNK_SIZE = 4096

def send_response(quic_server, stream_id, data, finish, directory):
    types = data[0]
    request_length = int.from_bytes(data[1:5], byteorder='big')
    request = data[5:5+request_length].decode().split(' ')
    request_path = request[1]
    print(stream_id)
    if request_path == "/":
        d_payload = "<html><header></header><body>"
        files = os.listdir(directory)
        for i in range(3):
            d_payload += f"<a href='/static/{files[i]}'>{files[i]}</a>"
            if i == 2:
                break
            d_payload += "<br/>"
        d_payload += "</body></html>"
        d_frame = (0).to_bytes(1, byteorder='big') + len(d_payload).to_bytes(4, byteorder='big') + d_payload.encode()

        h_payload = f"200 OK\r\nContent-Type:text/html\r\nContent-Length:{len(d_payload)}"
        h_frame = (1).to_bytes(1, byteorder='big') + len(h_payload).to_bytes(4, byteorder='big') + h_payload.encode()
        print("send start")
        quic_server.send(stream_id, h_frame, end=True)
        quic_server.send(stream_id, d_frame, end=True)
        print("send finish")

    elif request_path.startswith('/static'):
        full_path = directory + request_path[7:]
        file_size = os.path.getsize(full_path)
        print("send start")
        h_payload = f"200 OK\r\nContent-Type:text/html\r\nContent-Length:{file_size}"
        h_frame = (1).to_bytes(1, byteorder='big') + len(h_payload).to_bytes(4, byteorder='big') + h_payload.encode()
        quic_server.send(stream_id, h_frame, end=True)
        test = 0
        with open(full_path, "rb") as file:
            flag = True
            complete = False
            while complete == False:
                if flag:
                    d_payload = file.read(CHUNK_SIZE)
                    flag = False
                else:
                    d_payload = d_payload_next
                d_payload_next = file.read(CHUNK_SIZE)
                if not d_payload_next:
                    complete = True
                d_frame = (0).to_bytes(1, byteorder='big') + len(d_payload).to_bytes(4, byteorder='big') + d_payload
                quic_server.send(stream_id, d_frame, end=complete)
                test += len(d_payload)
                print("sending length: ", test)
        print("send finish")
    else:
        d_payload = "<html><header></header><body></body></html>"
        d_frame = (0).to_bytes(1, byteorder='big') + len(d_payload).to_bytes(4, byteorder='big') + d_payload.encode()
        h_payload = f"404 Not Found\r\nContent-Type:text/html\r\nContent-Length:{len(d_payload)}"
        h_frame = (1).to_bytes(1, byteorder='big') + len(h_payload).to_bytes(4, byteorder='big') + h_payload.encode()
        quic_server.send(stream_id, h_frame, end=True)
        quic_server.send(stream_id, d_frame, end=True)
        
class HTTPServer():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        self.quic_server = QUICServer()
        self.server_addr = (host, port)
        self.threads = []

    def run(self):
        self.quic_server.listen(self.server_addr)
        self.quic_server.accept()
        while True:
            stream_id, data, finish = self.quic_server.recv()
            if not data:
                break
            thread = threading.Thread(target=send_response, args=(self.quic_server, stream_id, data, finish, self.directory))
            self.threads.append(thread)
            thread.start()
        for th in self.threads:
            th.join()

    def set_static(self, path):
        self.directory = path

    def close(self):
        self.quic_server.close()