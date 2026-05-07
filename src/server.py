import asyncio
import socket
import os
from asyncio import AbstractEventLoop

from src.request import request_task
from dotenv import load_dotenv
import signal

load_dotenv()


class GracefulExit(SystemExit):
    pass


def shutdown():
    raise GracefulExit


class WebsocketServer:
    def __init__(self, loop):
        self._port = int(os.getenv("SERVER_PORT"))
        self._host = os.getenv("SERVER_HOST")
        self._loop: AbstractEventLoop = loop
        self._tasks = []

    async def set_server(self):

        try:
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.setblocking(False)
            server_socket.bind((self._host, self._port))

            server_socket.listen()

            for singname in {"SIGINT", "SIGTERM"}:
                self._loop.add_signal_handler(getattr(signal, singname), shutdown)
            await self._connection_listener(server_socket)
        except Exception as ex:
            raise ex

    async def _connection_listener(self, server_socket: socket):
        while True:
            connection, address = await self._loop.sock_accept(server_socket)
            connection.setblocking(False)
            print(f"Got a connection from address {address}")
            task = asyncio.create_task(self._task(connection))
            self._tasks.append(task)

    async def _task(self, connection: socket):
        try:
            data = await self._loop.sock_recv(connection, 1024)
            response = await request_task(data)
            await self._loop.sock_sendall(connection, bytes(response, "utf-8"))
        finally:
            connection.close()

    async def close_tasks(self):
        waiters = [asyncio.wait_for(task, 2) for task in self._tasks]
        for task in waiters:
            try:
                await task
            except asyncio.exceptions.TimeoutError:
                pass
