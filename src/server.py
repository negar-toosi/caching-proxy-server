import logging

import asyncio
import socket
import os
from asyncio import AbstractEventLoop

from src.request import ClientRequest
from dotenv import load_dotenv
import signal

load_dotenv()

logger = logging.getLogger("server")


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
        self._client = ClientRequest()

    async def set_server(self):

        try:
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.setblocking(False)
            server_socket.bind((self._host, self._port))

            server_socket.listen()
            logger.info(f"server start with host {self._host} and port {self._port} ")

            for singname in {"SIGINT", "SIGTERM"}:
                self._loop.add_signal_handler(getattr(signal, singname), shutdown)
            await self._connection_listener(server_socket)
        except Exception as ex:
            logger.exception(f"an unexpected error happen: {ex}")
            raise ex

    async def _connection_listener(self, server_socket: socket):
        while True:
            connection, address = await self._loop.sock_accept(server_socket)
            connection.setblocking(False)
            logger.info(f"Got a connection from address {address}")
            task = asyncio.create_task(self._task(connection))
            logger.info(f"A new task created for connection {address}")
            self._tasks.append(task)

    async def _task(self, connection: socket):
        host, port = connection.getpeername()
        try:
            data = await self._loop.sock_recv(connection, 1024)
            data = data.decode("utf-8").strip()
            logger.info(f"Get {data} data from connection {host, port}")
            response = await self._client.fetch_content(data)

            await self._loop.sock_sendall(connection, response)
            logger.info(f"send response for connection {host, port}")
        except Exception as ex:
            await self._loop.sock_sendall(connection, bytes(str(ex), "utf-8"))
            logger.exception(ex)
        finally:
            connection.close()
            logger.info(f"Close the connection {host, port}")

    async def close_tasks(self):
        waiters = [asyncio.wait_for(task, 2) for task in self._tasks]
        logger.info("Start to close all task after user close the connection")
        for task in waiters:
            try:
                await task
            except asyncio.exceptions.TimeoutError:
                pass
        logger.info("Finish close all tasks")
