import socket


class HTTPRequest:
    raw_contents: bytes

    def __init__(self, raw_contents: bytes):
        self.raw_contents = raw_contents

    @property
    def method(self):
        return self.status_line().split(b" ")[0].decode("utf-8")

    @property
    def path(self):
        return self.status_line().split(b" ")[1].decode("utf-8")

    @property
    def protocol(self):
        return self.status_line().split(b" ")[2].decode("utf-8")

    def __repr__(self):
        return f"<HTTPRequest {self.method} {self.path}>"

    def status_line(self):
        return self.raw_contents.split(b"\r\n")[0]


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, addr = server_socket.accept()  # wait for client
    print("Client connected", addr)

    request = HTTPRequest(conn.recv(1024))
    print(request)

    if request.path == "/":
        conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    else:
        conn.sendall(b"HTTP/1.1 404 NOT FOUND\r\n\r\n")


if __name__ == "__main__":
    main()
