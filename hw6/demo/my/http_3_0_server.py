class HTTPServer():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        pass
    def run(self):
        # Create the server socket and start accepting connections.
        pass
    def set_static(self, path):
        pass
        # Set the static directory so that when the client sends a GET request to the resource "/static/<file_name>", the file located in the static directory is sent back in the response.
    def close(self):
        pass
        # Close the server socket.