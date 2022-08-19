import json
import multiprocessing
from dataclasses import dataclass

import websockets
from websockets import exceptions
import asyncio

from multiprocessing import Process, Pipe

from enum import Enum

from otree import settings


# TODO Fix possible corruption in pipe

class FrisbeeCom:

    def __init__(self, *, host: str = 'localhost', port: int = 8001):
        """
        :param host: Network interfaces the server is bound to, defaults to `localhost` (optional)
        :param port: TCP port the server listens on, defaults to `8001` (optional)
        """
        self._host = host
        self._port = port

        self._connected_clients = set()

        self._parent_conn = None  # set when WebSocket server is started TODO Find better solution.
        self._child_conn = None  # set when WebSocket server is started

        # participant_labels_file = open(
        #    "/Users/wuest/Documents/wkspaces/oTreePlayground/myexperiment/_rooms/econ101.txt", "r")
        # participant_labels_file = open('_rooms/econ101.txt', 'r')
        # self._participant_labels = participant_labels_file.read().split()
        self._participant_labels = open('_rooms/econ101.txt', 'r').read().split()

    async def _handler(self, websocket, path, child_conn):
        """
        Receive and send messages on the same WebSocket connection.
        The coroutines `input_handler` and `output_handler` are automatically scheduled as Tasks and run concurrently.
        """

        # self._connected_clients.add(websocket)

        if websocket not in self._connected_clients:
            print("Authenticating client ...")
            token = await websocket.recv()
            auth_credentials = json.loads(token)

            if settings.AUTH_LEVEL == 'STUDY' or settings.AUTH_LEVEL == 'DEMO':

                # authenticate client by admin credentials
                if (
                        auth_credentials.get('admin_username') != settings.ADMIN_USERNAME
                        or auth_credentials.get('admin_password') != settings.ADMIN_PASSWORD
                ):
                    # 1011 — Server error — internal server error while operating
                    print("Authentication failed. Invalid admin username or admin password. Closing connection ...")
                    await websocket.close(1011, 'Authentication failed. Invalid admin username or admin password.')
                    return

                # authenticate client by participant label
                if (
                        auth_credentials.get('participant_label') not in self._participant_labels
                ):
                    print("Authentication failed. Invalid participant label. Closing connection ...")
                    await websocket.close(1011, 'Authentication failed. Invalid participant label.')
                    return

                # check if participant is already connected TODO Add later
        
            print('Authentication successful.')
            self._connected_clients.add(websocket)
            await websocket.send(json.dumps({'status': 'connected'}))

        await asyncio.gather(
            self._input_handler(websocket),
            self._output_handler(websocket, child_conn),
        )

    async def _main(self, child_conn):
        """
        Start a WebSocket server that calls the connection handler `handler` when a client connects.
        """
        bound_handler = partial(self._handler, child_conn=child_conn)
        # async with websockets.unix_serve(bound_handler, path='/tmp/nginx.socket'):
        #    await asyncio.Future()
        async with websockets.serve(bound_handler, self._host, self._port):
            await asyncio.Future()

    def _run(self, child_conn):
        asyncio.run(self._main(child_conn))

    def start_ws_server(self):
        """
        Start setup of WebSocket server in a separate process.
        Create a pipe between the parent and child process, and then start the child process.

        :return: The parent and child connection objects representing the ends of a pipe.
        """

        parent_conn, child_conn = Pipe()
        multiprocessing.set_start_method('fork')
        p = Process(target=self._run, args=(child_conn,))
        p.start()

        self._parent_conn = parent_conn
        self._child_conn = child_conn

        return [parent_conn, child_conn]

    async def _input_handler(self, websocket):
        """
        Receive messages from the WebSocket connection and pass them to a consumer coroutine.
        Iteration terminates when the client disconnects.
        TODO Implement consumer coroutine.
        """
        print('A client just connected')
        self._connected_clients.add(websocket)
        try:
            async for message in websocket:
                print('Received a message from client: ' + message)
                for client in self._connected_clients:
                    if client != websocket:
                        await client.send('Someone said: ' + message)
                # await websocket.send('Pong: ' + message)
        except websockets.exceptions.ConnectionClosed as e:
            print('A client just disconnected')
        finally:
            self._connected_clients.remove(websocket)

    # TODO: Add support for multiple clients
    async def _output_handler(self, websocket, child_conn):
        """
        Get messages from producer coroutine and send them to the WebSocket connection.
        Iteration terminates when the client disconnects because send() raises a ConnectionClosed exception,
        which breaks out of the while True loop.
        """

        # works with sleep
        async def producer():
            """Get the next message (from the parent process) to send on the WebSocket connection."""
            # await asyncio.sleep(1)

            is_data_available = False

            def poll_data():
                # Define the is_data_available variable as non-local, causing it to bind
                # to the nearest non-global variable also called is_data_available.
                nonlocal is_data_available

                is_data_available = child_conn.poll()

            # TODO get rid of following line by using child_conn.poll(None)?
            await asyncio.get_event_loop().run_in_executor(None, poll_data)

            if is_data_available:
                # print("Data available") TODO avoid that data is sent multiple times
                return child_conn.recv()

            return -1

        while True:
            data = await producer()
            # message = await asyncio.get_event_loop().run_in_executor(None, producer)

            if data != -1:
                print(data)
                participant_label = data[0]
                message = data[1]

                # await websocket.send(str(message))
                # print('An instruction was just sent')

                if participant_label is None:
                    websockets.broadcast(self._connected_clients, json.dumps(message))
                    # for client in self._connected_clients:
                    #    await client.send(json.dumps(message))
                else:
                    # TODO get specific client
                    await websocket.send(json.dumps(message))

            # await asyncio.sleep(1)
            # print(str(conn))

        # msg = conn.recv()
        # for client in self.CONNECTED_CLIENTS:
        # await client.send(msg)

        # while True:
        # print(conn)
        # msg = conn.recv()
        # print(msg)
        # await websocket.send(str(msg))

        # async with conn.recv():
        #   websocket.send("Instruction received ... ")

    @property
    def connected_clients(self):
        return self._connected_clients

    @property
    def parent_conn(self):
        return self._parent_conn

    # Functionality for managing Connections
    def start_recording(self, *, participant_label=None):
        print('Start recording!')
        self._parent_conn.send((participant_label, {'recording': 'start'}))

    def pause_recording(self, *, participant_label=None):
        print('Pause recording')
        self._parent_conn.send((participant_label, {'recording': 'pause'}))

    def stop_recording(self, *, participant_label=None):
        print('Stop recording')
        self._parent_conn.send((participant_label, {'recording': 'stop'}))

    """
    def send_thingspeak_conf(self, *, participant_label=None):
        print('ThingSpeak Configuration sent')
        self._parent_conn.send((participant_label, {}))

    def send_custom_data(self, *, participant_label=None, custom_data={}):
        print('Custom data sent')
        assert isinstance(custom_data, dict), "Data has to be dict"
        self._parent_conn.send((participant_label, custom_data))
    """


class StandardData:
    pass


class Instructions(Enum):
    START_RECORDING = 1
    PAUSE_RECORDING = 2
    STOP_RECORDING = 3


@dataclass
class Client:
    """Class for keeping track of a connected participants in connected clients."""
    '''Class for keeping track of an item in inventory.'''
    participant_label: str
    websocket: websockets.WebSocketServerProtocol
    time_of_authentication: float


def partial(func, /, *args, **keywords):
    """
    Re-implementation of `functools.partial` using the documentation implementation example.
    Workaround to use `functools.partial` on class methods.

    See:
    https://docs.python.org/3/library/functools.html#functools.partial
    https://stackoverflow.com/questions/16626789/functools-partial-on-class-method
    """

    def newfunc(*fargs, **fkeywords):
        newkeywords = {**keywords, **fkeywords}
        return func(*args, *fargs, **newkeywords)

    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc


def print_ws_info(self, websocket, path, child_conn):
    print(f"Self: {self}")
    print(f"Websocket: {websocket}")
    print(f"Path: {path}")
    print(f"Child_conn: {child_conn}")
