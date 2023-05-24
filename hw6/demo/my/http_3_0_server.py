from QUIC.quic_server import QUICServer

class HTTPServer():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        self.quic_server = QUICServer()
        self.sockaddr = (host, port)

    def run(self):
        self.quic_server.listen(self.sockaddr)
        self.quic_server.accept()

    def set_static(self, path):
        self.directory = path

    def close(self):
        self.quic_server.close()