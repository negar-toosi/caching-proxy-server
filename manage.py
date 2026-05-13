import asyncio

from src.server.ws import GracefulExit, WebsocketServer
import logging.config

logging.config.fileConfig("logging.conf")


def main():
    loop = asyncio.new_event_loop()
    server = WebsocketServer(loop)

    try:
        loop.run_until_complete(server.set_server())
    except GracefulExit:
        loop.run_until_complete(server.close_tasks())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
