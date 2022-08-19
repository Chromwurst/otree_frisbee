import json

import websockets
import asyncio

# participant_labels = ['Alice', 'Alice', 'Charlie', 'Alex', 'Max', 'Isaac', 'Jakob', 'Tim', 'Fredi',
#                           'Elly', 'Sarah', 'Hanna', 'Debora', 'Fabian']

PARTICIPANT_LABELS = open('../../_rooms/econ101.txt').read().split()

"""async def create_websocket_connection(participant_label):
    async def listen(participant_label):
        url = "ws://127.0.0.1:8001"
        # url = 'ws://o-tree-playground.herokuapp.com:80'
        # url = 'ws://localhost:8001'
        # url = 'wss://tmp-testing.herokuapp.com'
        # url = 'ws://127.0.0.1:8080/ws'
        # url = 'ws://tmp-testing.herokuapp.com/ws'

        async with websockets.connect(url) as ws:
            auth_credentials = {
                'admin_password': 'admin',
                'participant_label': participant_label,
            }

            await ws.send(json.dumps(auth_credentials))
            await ws.send('Hello Server')

            while True:
                msg = await ws.recv()
                print(msg)
                # time.sleep(3)
                # break

    asyncio.get_event_loop().run_until_complete(listen(participant_label))


for participant_label in PARTICIPANT_LABELS:
    task = asyncio.get_event_loop().create_task(create_websocket_connection(participant_label))"""

