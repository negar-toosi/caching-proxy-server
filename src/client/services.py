import socket
import typer
from typing_extensions import Annotated


def caching_proxy(
    port: Annotated[str, typer.Option(help="the port that you want to connect")],
    origin: Annotated[str, typer.Option(help="the url that you want to sent request")],
):

    client_socket = socket.socket()
    client_socket.connect(("127.0.0.1", int(port)))

    client_socket.send(origin.encode())
    data = b""
    while True:
        part = client_socket.recv(4096)
        data += part
        if len(part) < 4096:
            break

    client_socket.close()

    print(data)
