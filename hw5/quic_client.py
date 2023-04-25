class QUICClient:
    def connect(socket_addr: tuple[str, int]):
        """connect to the specific server"""
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
    client = QUICClient()
    client.connect(("127.0.0.1", 30000))
    recv_id, recv_data = client.recv()
    print(recv_data.decode("utf-8")) # SOME DATA, MAY EXCEED 1500 bytes
    client.send(2, b"Hello Server!")
    client.close()