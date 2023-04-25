class QUICServer:
    def listen(socket_addr: tuple[str, int]):
        """this method is to open the socket"""
        pass
    
    def accept():
        """this method is to indicate that the client
        can connect to the server now"""
        pass
    
    def send(stream_id: int, data: bytes):
        """call this method to send data, with non-reputation stream_id"""
        pass
    
    def recv() -> tuple[int, bytes]: # stream_id, data
        """receive a stream, with stream_id"""
        pass
    
    def close():
        """close the connection and the socket"""
        pass

if __name__ == "__main__":
    server = QUICServer()
    server.listen(("", 30000))
    server.accept()
    server.send(1, b"SOME DATA, MAY EXCEED 1500 bytes")
    recv_id, recv_data = server.recv()
    print(recv_data.decode("utf-8")) # Hello Server!
    server.close() 