import asyncio
import json
import multiprocessing
from multiprocessing import Process

import websockets


# PARTICIPANT_LABELS = open('../../../_rooms/econ101.txt').read().split()
PARTICIPANT_LABELS = ['Alice', 'Bob', 'Charlie', 'Alex', 'Max', 'Isaac', 'Jakob', 'Tim', 'Fredi', 'Elly', 'Sarah',
                      'Hanna', 'Debora', 'Fabian']


def run(participant_label: str):
    asyncio.run(connect_participant(participant_label))


async def connect_participant(participant_label: str):
    url = "ws://127.0.0.1:8001"
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


"""if __name__ == '__main__':
    p = Pool(2)
    p.map(connect_participant, PARTICIPANT_LABELS)"""

multiprocessing.set_start_method('fork')

for participant_label in PARTICIPANT_LABELS:
    p = Process(target=run, args=(participant_label,))
    p.start()
    print('Process: ' + participant_label)
    asyncio.sleep(.5)
