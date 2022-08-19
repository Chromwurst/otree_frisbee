import websockets
from websockets import exceptions
import asyncio
import os

PORT = 7890
# PORT = os.environ['PORT']

# print('Server listening on port ' + str(PORT))


"""async def echo(websocket, path):
    print('A client just connected')
    try:
        async for message in websocket:
            print('Received a message from client: ' + message)
            await websocket.send('Pong: ' + message)
    except websockets.exceptions.ConnectionClosed as e:
        print('A client just disconnected')


def start():
    start_server = websockets.serve(echo, '', PORT)

    # asyncio.get_event_loop().run_until_complete(start_server)
    # asyncio.get_event_loop().run_forever()
"""

# start()
