import socket
import threading


class HTTPResponse:
    def __init__(self, status_code: int, body: bytes = None, headers: dict = None):
        self.status_code = status_code
        self.body = body
        self.headers = headers or {}

    @property
    def status_line(self):
        return f"HTTP/1.1 {self.status_code}"

    @property
    def headers_section(self):
        return "\r\n".join(
            f"{k}: {v}"
            for k, v in {
                "Content-Length": len(self.body) if self.body else 0,
                **self.headers,
            }.items()
        )

    def __bytes__(self):
        return (
            self.status_line.encode("utf-8")
            + b"\r\n"
            + self.headers_section.encode("utf-8")
            + b"\r\n\r\n"
            + (self.body or b"")
        )


class HTTPRequest:
    raw_contents: bytes

    def __init__(self, raw_contents: bytes):
        self.raw_contents = raw_contents

    @property
    def headers(self):
        return dict(
            [item.decode("utf-8") for item in line.split(b": ")]
            for line in self.headers_section.split(b"\r\n")
            if line
        )

    @property
    def method(self):
        return self.status_line.split(b" ")[0].decode("utf-8")

    @property
    def path(self):
        return self.status_line.split(b" ")[1].decode("utf-8")

    @property
    def protocol(self):
        return self.status_line.split(b" ")[2].decode("utf-8")

    @property
    def status_line(self):
        return self.raw_contents.split(b"\r\n")[0]

    @property
    def headers_section(self):
        return b"\r\n".join(self.raw_contents.split(b"\r\n")[1:])

    def __repr__(self):
        return f"<HTTPRequest {self.method} {self.path}>"


def handle_connection(conn):
    request = HTTPRequest(conn.recv(1024))
    print(request)

    if request.path == "/":
        conn.sendall(bytes(HTTPResponse(200)))
    elif request.path.startswith("/echo"):
        value = request.path.split("/echo/")[1]
        response = HTTPResponse(
            200, body=value.encode("utf-8"), headers={"Content-Type": "text/plain"}
        )
        conn.sendall(bytes(response))
    elif request.path == "/user-agent":
        response = HTTPResponse(
            200,
            body=request.headers["User-Agent"].encode(),
            headers={"Content-Type": "text/plain"},
        )
        conn.sendall(bytes(response))
    else:
        conn.sendall(bytes(HTTPResponse(404)))


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        conn, addr = server_socket.accept()  # wait for client
        print("Client connected", addr)

        thread = threading.Thread(target=handle_connection, args=(conn,))
        thread.start()


if __name__ == "__main__":
    main()
