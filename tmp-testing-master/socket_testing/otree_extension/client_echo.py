import sys
import json

import websockets
import asyncio


async def listen():
    url = "ws://127.0.0.1:8001"
    # url = 'ws://o-tree-playground.herokuapp.com:80'
    # url = 'ws://localhost:8001'
    # url = 'wss://tmp-testing.herokuapp.com'
    # url = 'ws://127.0.0.1:8080/ws'
    # url = 'ws://tmp-testing.herokuapp.com/ws'
    # 7892

    async with websockets.connect(url) as ws:
        # await ws.send('Hello Server')

        auth_credentials = {
            # 'admin_username': 'admin',
            'admin_password': 'admin',
            'participant_label': sys.argv[1],
        }

        await ws.send(json.dumps(auth_credentials))
        await ws.send('Hello Server')

        while True:
            msg = await ws.recv()
            print(msg)
            # time.sleep(3)
            # break

        # await ws.close()


asyncio.get_event_loop().run_until_complete(listen())
