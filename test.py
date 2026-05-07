import asyncio
from src.server import WebsocketServer, GracefulExit

loop = asyncio.new_event_loop()
server = WebsocketServer(loop)

try:
    loop.run_until_complete(server.set_server())
except GracefulExit:
    loop.run_until_complete(server.close_tasks())
finally:
    loop.close()
