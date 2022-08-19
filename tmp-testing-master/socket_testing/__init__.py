import json
import time
from os import environ
from pathlib import Path

from otree import settings  # only use otree.api in the future
from otree.api import *

from .otree_extension.server_ws import FrisbeeCom, Instructions, FrisbeeComConfig
from .otree_extension import thingspeak


doc = """
Support Tool for Testing New Client Implementations
"""

# Setup WebSocket Server
"""server_config = FrisbeeComConfig(host='127.0.0.1',
                                 port=8001,
                                 participant_label_file='_rooms/econ101.txt')

channel_config = thingspeak.ChannelConfig(api_key='KWOJ1KJ7XY5HU60C',
                                          description='Heart rate. Trust Game.',
                                          fieldX={'field1': 'Heart Rate'},
                                          metadata=json.dumps({'Experimenter': 'Max Mustermann'}),
                                          name='Heart Rate',
                                          public_flag=False,
                                          tags=['Heart Rate', 'BPM', 'Trust Game'],
                                          url='www.otree-frisbee.com',
                                          use_participant_specific_preface=True)

# created = FrisbeeCom(frisbee_com_config, thingspeak_channel_config)
created = FrisbeeCom(host='127.0.0.1', port=8001, participant_label_file='_rooms/econ101.txt',
                     channel_config=channel_config)
print(f'HOST: {created._host}')
print(f'Port: {created._port}')
conns = created.start_ws_server()
Path("/tmp/app-initialized").touch()
# conns[0].send('Test send')
print(f'User: {settings.ADMIN_USERNAME} with Password: {settings.ADMIN_PASSWORD}')"""


class C(BaseConstants):
    NAME_IN_URL = 'socket_testing'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # For Server Info Section
    """OTREE_ADMIN_PASSWORD_SET = True if environ.get('OTREE_ADMIN_PASSWORD') else False
    AUTH_LEVEL = environ.get('OTREE_AUTH_LEVEL')
    PARTICIPANT_LABELS_SET = True if created._participant_labels else False
    PARTICIPANT_LABELS = created._participant_labels
"""

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


def creating_session(subsession: Subsession):
    pass


# PAGES
class Testing(Page):
    @staticmethod
    def vars_for_template(player: Player):
        pass

    @staticmethod
    def js_vars(player: Player):

        # Implementation not working because server runs in different process with its own memory space.
        # Process started by forking original process and therefore creating a copy of its memory
        # at the time of the fork.
        # https://stackoverflow.com/questions/37412345/instance-variables-not-being-updated-python-when-using-multiprocessing
        cache_dict = {}

        for client in created.connected_clients:
            print(f'Connected Clients: {client}')

        for index, client in enumerate(created.connected_clients):
            print(index)
            print(client)
            cache_dict[index] = client

        # print(f'Set: {cache_dict} + {len(created.connected_clients)}')

        return dict(
            connected_clients=cache_dict,
        )

    @staticmethod
    def live_method(player: Player, data):
        # data eg. [1, [''], False]
        to_all = data.pop()  # bool
        participant_labels = data.pop()  # list
        instruction = data.pop()  # int

        if instruction == 1:  # Start Recording
            created.start_recording(participant_labels, to_all=to_all)
        if instruction == 2:  # Pause Recording
            created.pause_recording(participant_labels, to_all=to_all)
        if instruction == 3:  # Stop Recording
            created.stop_recording(participant_labels, to_all=to_all)
        if instruction == 4:  # Refresh list of connected clients
            # Duration to retrieve list from child process
            prev = time.time_ns()
            status_info = created.get_connected_clients_info()
            post = time.time_ns()
            print(f'Duration in Nanoseconds: {post - prev}')
            print(f'Duration in Microseconds: {(post - prev) * 0.001}')
            print(f'Duration in Milliseconds: {(post - prev) * 1.0E-6}')
            print(f'Duration in Seconds: {(post - prev) * 1.0E-9}')

            return {0: status_info}


page_sequence = [Testing]
