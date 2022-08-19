import json

import websockets
import asyncio


async def listen():
    url = "ws://127.0.0.1:8001"
    # url = 'ws://o-tree-playground.herokuapp.com:80'
    # url = 'ws://localhost:8001'
    # url = 'wss://tmp-testing.herokuapp.com'
    # url = 'ws://127.0.0.1:8080/ws'
    # url = 'wss://tmp-testing.herokuapp.com/ws'
    # 7892

    async with websockets.connect(url) as ws:
        # await ws.send('Hello Server')
        auth_credentials = {
            'admin_username': 'admin',
            'admin_password': None,
            'participant_label': 'Bob',
        }
        await ws.send(json.dumps(auth_credentials))
        # await ws.send('Bob')
        await ws.send('Hello Server')

        while True:
            msg = await ws.recv()
            print(msg)


asyncio.get_event_loop().run_until_complete(listen())
