import asyncio
import socket
import os
from asyncio import AbstractEventLoop

from request import request_task


class WebsocketServer:
    _host = os.getenv("SERVER_HOST")
    _port = os.getenv("SERVER_PORT")
    _loop: AbstractEventLoop = asyncio.new_event_loop()
    _tasks = []

    @classmethod
    async def _set_server(cls):
        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.setblocking(False)
        server_socket.bind((cls._host, cls._port))
        server_socket.listen()

        await cls._connection_listener(server_socket)

    @classmethod
    async def _connection_listener(cls, server_socket: socket):
        while True:
            connection, address = await cls._loop.sock_accept(server_socket)
            connection.setblocking(False)
            print(f"Got a connection from address {address}")
            task = asyncio.create_task(cls._task(connection))
            cls._tasks.append(task)

    @classmethod
    async def _task(cls, connection: socket):
        try:
            while data := await cls._loop.sock_recv(connection, 1024):
                response = await request_task(data)
                await cls._loop.sock_sendall(connection, response)
        finally:
            connection.close()

    @classmethod
    async def _close_tasks(cls):
        waiters = [asyncio.wait_for(task, 2) for task in cls._tasks]
        for task in waiters:
            try:
                await task
            except asyncio.exceptions.TimeoutError:
                pass

    async def start_server(cls):
        try:
            cls._loop.run_until_complete(cls._set_server())
        except Exception:
            cls._loop.run_until_complete(cls._close_tasks())
        finally:
            cls._loop.close()
