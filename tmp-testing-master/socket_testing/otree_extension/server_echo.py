"""Simple WebSocket Echo Server"""

import asyncio
import os

import websockets
from websockets import exceptions

PORT = 7890
# PORT = os.environ['PORT']

print(f'Server listening on port {PORT}')


async def echo(websocket, path):
    print('A client just connected')
    try:
        async for message in websocket:
            print('Received a message from client: ' + message)
            await websocket.send('Pong: ' + message)
    except websockets.exceptions.ConnectionClosed as e:
        print('A client just disconnected')


async def start():
    async with websockets.serve(echo, '', PORT):
        await asyncio.Future()  # Run forever

    # start_server = websockets.serve(echo, '', PORT)
    # asyncio.get_event_loop().run_until_complete(start_server)
    # asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    # start()
    asyncio.run(start())
