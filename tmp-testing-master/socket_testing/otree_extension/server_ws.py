import asyncio
import json
import multiprocessing
import time
from dataclasses import dataclass
from enum import Enum
from multiprocessing import Process, Pipe
from os import environ
from typing import Union, List, Set, Tuple

import websockets
from websockets import exceptions

import thingspeak


# TODO Fix possible corruption in pipe

@dataclass(kw_only=True)
class FrisbeeComConfig:
    host: str = '127.0.0.1'
    port: int = 8001
    participant_label_file: str = '_rooms/econ101.txt'


class FrisbeeCom:

    def __init__(self, *, host: str = 'localhost', port: int = 8001, participant_label_file,
                 channel_config: thingspeak.ChannelConfig):
        """
        :param host: Network interfaces the server is bound to, defaults to `localhost` (optional)
        :param port: TCP port the server listens on, defaults to `8001` (optional)
        """
        self._host = host
        self._port = port

        self._connected_clients = set()

        self._parent_conn = None  # set when WebSocket server is started TODO Find better solution.
        self._child_conn = None  # set when WebSocket server is started

        # for authentication
        self._auth_level = environ.get('OTREE_AUTH_LEVEL')
        self._admin_password = environ.get('OTREE_ADMIN_PASSWORD')
        self._participant_labels = open(participant_label_file, 'rt').read().split()

        self._channel_config = channel_config

    async def _handler(self, websocket, path, child_conn):
        """
        Receive and send messages on the same WebSocket connection.
        The coroutines `input_handler` and `output_handler` are automatically scheduled as Tasks and run concurrently.
        """

        # Authentication
        if websocket not in self._connected_clients:  # TODO Check whether if statement could be removed
            print("Authenticating client ...")
            token = await websocket.recv()
            auth_credentials = json.loads(token)

            if self._auth_level in {'STUDY', 'DEMO'}:

                # authenticate client by admin credentials
                if auth_credentials.get('admin_password') != self._admin_password:
                    # 1011 — Server error — internal server error while operating
                    print('Authentication failed. Invalid admin password. Closing connection ...')
                    # TODO is there a fix to leave out the following line?
                    await websocket.send(json.dumps({'exception': 'Authentication failed. Invalid admin password.'}))
                    await websocket.close(1011, 'Authentication failed. Invalid admin password.')
                    return

                # authenticate client by participant label
                if auth_credentials.get('participant_label') not in self._participant_labels:
                    print('Authentication failed. Invalid participant label. Closing connection ...')
                    await websocket.send(json.dumps({'exception': 'Authentication failed. Invalid participant label.'}))
                    await websocket.close(1011, 'Authentication failed. Invalid participant label.')
                    return

                # check if participant is already connected
                for client in self._connected_clients:
                    if client.participant_label == auth_credentials.get('participant_label'):
                        print('Authentication failed. Participant label is already in use. Closing connection ...')
                        await websocket.send(
                            json.dumps({'exception': 'Authentication failed. Participant label is already in use.'}))
                        await websocket.close(1011, 'Authentication failed. Participant label is already in use.')
                        return

            print('Authentication successful.')

            await websocket.send(json.dumps({'status': 'connected'}))  # send after channel is created?
            print(f'Client with Participant Label "{auth_credentials.get("participant_label")}\" just connected.')

            # Setup ThingSpeak Channel
            manager = thingspeak.ChannelManager(self._channel_config)
            ch_settings = manager.assign_channel(auth_credentials.get('participant_label'))
            await websocket.send(json.dumps({'config': ch_settings}))

            # Add new Client
            new_client = Client(auth_credentials.get('participant_label'), websocket, time.time(), ch_settings)
            self._connected_clients.add(new_client)

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
        async with websockets.serve(bound_handler, self._host, self._port, ping_timeout=40):
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
        # print('A client just connected')
        # self._connected_clients.add(websocket)
        try:
            async for message in websocket:
                print('Received a message from client: ' + message)
                for client in self._connected_clients:
                    if client.websocket != websocket:
                        # await client.websocket.send('Someone said: ' + message)
                        await client.websocket.send(json.dumps({'message': str('Someone said: ' + message)}))
                # await websocket.send('Pong: ' + message)
        except websockets.exceptions.ConnectionClosed as e:
            print('A client just disconnected')
        finally:
            disconnected_client = Client.get_by_websocket(websocket, self._connected_clients)
            self._connected_clients.remove(disconnected_client)

    # TODO: Add support for multiple clients
    async def _output_handler(self, websocket, child_conn):
        """
        Get messages from producer coroutine and send them to the WebSocket connection.
        Iteration terminates when the client disconnects because send() raises a ConnectionClosed exception,
        which breaks out of the while True loop.
        """

        # works with sleep
        def producer():
            """Get the next message (from the parent process) to send on the WebSocket connection."""
            # await asyncio.sleep(1)

            is_data_available = False

            def poll_data():
                # Define the is_data_available variable as non-local, causing it to bind
                # to the nearest non-global variable also called is_data_available.
                nonlocal is_data_available

                is_data_available = child_conn.poll()

            # TODO get rid of following line by using child_conn.poll(None)?
            # await asyncio.get_event_loop().run_in_executor(None, poll_data)
            poll_data()

            if is_data_available:
                # print("Data available") TODO avoid that data is sent multiple times
                return child_conn.recv()

            return -1

        while True:
            data = producer()
            # message = await asyncio.get_event_loop().run_in_executor(None, producer)

            if data != -1:
                print(f'Data from producer: {data}')
                participant_labels = data[0]
                message = json.dumps(data[1])

                # Send status updates about connected clients to oTree
                # No use of WebSockets. Direct communication with parent process (oTree) using Pipe.
                if participant_labels == 'connected_clients_status_info':

                    def status(client: Client):
                        return dict(
                            participant_label=client.participant_label,
                            time_of_authentication=client.time_of_authentication,
                            thingspeak_ch_settings=client.thingspeak_ch_settings,
                        )

                    status_info = [status(client) for client in self._connected_clients]
                    child_conn.send(status_info)

                # Outgoing communication to connected clients using WebSockets
                # To all participants
                elif participant_labels is None:
                    websockets.broadcast(Client.get_all_websockets(self._connected_clients), message)
                    # for client in self._connected_clients:
                    #    await client.send(json.dumps(message))
                else:
                    participant_labels = FrisbeeCom.unpack(participant_labels)

                    # To single participant
                    if len(participant_labels) == 1:
                        client = Client.get_by_participant_label(participant_labels[0], self._connected_clients)
                        await client.websocket.send(message)

                    # To multiple participants
                    else:
                        clients = set()
                        # TODO find more efficient solution
                        for participant_label in participant_labels:
                            client = Client.get_by_participant_label(participant_label, self._connected_clients)
                            clients.add(client.websocket)
                        websockets.broadcast(clients, message)

                        # TODO Maybe implement methods such as get_ws_by_participant_labels
                        # clients = Client.get_by_participant_labels(participant_labels)
                        # websockets.broadcast(Client.get_all_websockets(clients))

            await asyncio.sleep(0.02)

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
    def start_recording(self, *participant_labels: Union[str, List[str], Set[str], Tuple[str]], to_all=False):
        if to_all:
            participant_labels = None
        print('Start recording!')
        self._parent_conn.send((participant_labels, {'recording': 'start'}))

    # @start_recording.register(Union[List[str], Set[str], Tuple[str]])
    # def _(self, participant_labels: Union[List[str], Set[str], Tuple[str]], to_all=False):
    #     print('inherit')

    def pause_recording(self, *participant_labels: Union[str, List[str], Set[str], Tuple[str]], to_all=False):
        if to_all:
            participant_labels = None
        print('Pause recording')
        self._parent_conn.send((participant_labels, {'recording': 'pause'}))

    def stop_recording(self, *participant_labels: Union[str, List[str], Set[str], Tuple[str]], to_all=False):
        if to_all:
            participant_labels = None
        print('Stop recording')
        self._parent_conn.send((participant_labels, {'recording': 'stop'}))

    def get_connected_clients_info(self) -> dict:
        self._parent_conn.send(('connected_clients_status_info', 'status'))
        return self._parent_conn.recv()

    @staticmethod
    def unpack(participant_labels: tuple) -> Tuple[str]:

        if len(participant_labels) == 1:
            participant_labels, = participant_labels  # unpack

            if isinstance(participant_labels, str):
                tmp = participant_labels,
                print(f'Case 2 - {tmp} of type {type(tmp)}')
                return tmp

            if not isinstance(participant_labels, str) and len(participant_labels) == 1:
                participant_labels, = participant_labels
                tmp = participant_labels,
                print(f'Case 4 - {tmp} of type {type(tmp)}')
                return tmp

            if len(participant_labels) != 1:
                print(f'Case 5 - {tuple(participant_labels)} of type {type(tuple(participant_labels))}')
                return tuple(participant_labels)

        if len(participant_labels) != 1:
            print(f'Case 3 - {tuple(participant_labels)} of type {type(tuple(participant_labels))}')
            return tuple(participant_labels)

    @staticmethod
    def unpack_supercharge(participant_labels) -> Tuple[str]:
        # TODO implement
        pass

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
    time_of_authentication: float  # TODO Check: use LongStringField when working with oTree?
    thingspeak_ch_settings: dict

    def __hash__(self):
        return hash((self.participant_label, self.websocket, self.time_of_authentication))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        return (self.participant_label == other.participant_label
                and self.websocket == other.websocket
                and self.time_of_authentication == other.time_of_authentication)

    # TODO Add return statement in case no client is found?
    @staticmethod
    def get_by_participant_label(participant_label: str, clients: set):
        for client in clients:
            if client.participant_label == participant_label:
                return client  # TODO only use if just one label is passed

    @staticmethod
    def get_by_participant_labels(participant_labels: Union[List[str], Set[str], Tuple[str]], clients: set):
        return (client for client in clients if client.participant_label in participant_labels)

    @staticmethod
    def get_by_websocket(websocket: websockets.WebSocketServerProtocol, clients: set):
        for client in clients:
            if client.websocket == websocket:
                return client

    @staticmethod
    def get_all_websockets(clients: set):
        return (client.websocket for client in clients)


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
