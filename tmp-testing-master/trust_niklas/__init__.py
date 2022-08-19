from otree.api import *
import requests
import time
from pathlib import Path

from os import environ
import os
import sys

import asyncio

# sys.path.append(os.path.dirname(f'{os.getcwd()}/'))
from otree_extension import thingspeak
from otree_extension.server_ws import FrisbeeCom, FrisbeeComConfig

import json

doc = """
This is a standard 2-player trust game where the amount sent by player 1 gets
tripled. The trust game was first proposed by
<a href="http://econweb.ucsd.edu/~jandreon/Econ264/papers/Berg%20et%20al%20GEB%201995.pdf" target="_blank">
    Berg, Dickhaut, and McCabe (1995)
</a>.
"""

server_config = FrisbeeComConfig(host='127.0.0.1',
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
# print(f'User: {settings.ADMIN_USERNAME} with Password: {settings.ADMIN_PASSWORD}')


class C(BaseConstants):
    NAME_IN_URL = 'trust'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    INSTRUCTIONS_TEMPLATE = 'trust/instructions.html'
    # Initial amount allocated to each player
    ENDOWMENT = cu(100)
    MULTIPLIER = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    sent_amount = models.CurrencyField(
        min=0,
        max=C.ENDOWMENT,
        doc="""Amount sent by P1""",
        label="Please enter an amount from 0 to 100:",
    )
    sent_back_amount = models.CurrencyField(doc="""Amount sent back by P2""", min=cu(0))


class Player(BasePlayer):
    actHeartRate = models.IntegerField(initial=0)


class HeartRate(ExtraModel):
    player = models.Link(Player)
    heartRate = models.IntegerField()
    time = models.LongStringField()


# FUNCTIONS
def sent_back_amount_max(group: Group):
    return group.sent_amount * C.MULTIPLIER


def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    p1.payoff = C.ENDOWMENT - group.sent_amount + group.sent_back_amount
    p2.payoff = group.sent_amount * C.MULTIPLIER - group.sent_back_amount


def getHeartRate(playerID, channelID, apiKey):
    playerID = 1

    url = "https://api.thingspeak.com/channels/" + str(channelID) + "/fields/" + str(
        playerID) + "/last.json?api_key=" + str(apiKey)
    res = requests.get(url)
    js = res.json()
    if not js == -1:
        heartRate = js["field1"]
        timeStamp = js["created_at"]
        return dict(heartRate=heartRate, timeStamp=timeStamp)
    else:
        return 0


def match_maker(group: Group):
    number_of_players = len(group.get_players())
    print(f'Number of Players: {number_of_players}')

    connected_clients_info = created.get_connected_clients_info()
    print(f'Connected Clients Info: {connected_clients_info}')

    number_of_connected_participants = len(connected_clients_info)
    print(f'Number of connected participants: {number_of_connected_participants}')

    # Get All Clients
    while number_of_connected_participants != number_of_players:
        connected_clients_info = created.get_connected_clients_info()
        number_of_connected_participants = len(connected_clients_info)

    print('Match finished')

    """async def get_all_clients():
        number_of_connected_participants = 0

        while number_of_connected_participants != number_of_players:
            connected_clients_info = created.get_connected_clients_info()
            number_of_connected_participants = len(connected_clients_info)
            await asyncio.sleep(0.1)

    asyncio.run(get_all_clients())"""

    for player in group.get_players():
        for client in connected_clients_info:
            if client is not None and player.participant.label != client['participant_label']:
                player.participant.ch_settings = client['thingspeak_ch_settings']
                client = None  # "Delete"
                break


# PAGES
class ConnectWaitPage(WaitPage):
    title_text = 'Wait for all Clients to Connect'
    body_text = 'Waiting for client software to connect.'

    """@staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1"""

    """@staticmethod
    def group_by_arrival_time_method(subsession, waiting_players):
        return [waiting_players[0], waiting_players[1]]"""

    @staticmethod
    def after_all_players_arrive(group: Group):
        match_maker(group)

    """wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        for group in subsession.get_groups():
            print(f'Matching... {group}')
            players = group.get_players()
            print(f'Players in Groupe: {players[0].participant.label} and {players[1].participant.label}')
            # match_maker(group)"""

    """while len(created.get_connected_clients_info()) < 1:
        print('waiting ...')
        time.sleep(1)"""

    """if group.get_player_by_id(2).id_in_group == 2:
        connected_clients = created.get_connected_clients_info()

        player = group.get_player_by_id(2)

        for client in connected_clients:
            if client['participant_label'] == player.participant.label:
                print(client['thingspeak_ch_settings'])
                player.participant.ch_settings = client['thingspeak_ch_settings']
                print(f'Player {player.participant.ch_settings}')"""


class Introduction(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):

        """if player.id_in_group == 2:
            connected_clients = created.get_connected_clients_info()

            for client in connected_clients:
                if client['participant_label'] == player.participant.label:
                    print(client['thingspeak_ch_settings'])
                    player.participant.ch_settings = client['thingspeak_ch_settings']
                    print(f'Player {player.participant.ch_settings}')"""
        created.start_recording(player.participant.label)
        pass


class Send(Page):
    """This page is only for P1
    P1 sends amount (all, some, or none) to P2
    This amount is tripled by experimenter,
    i.e if sent amount by P1 is 5, amount received by P2 is 15"""

    form_model = 'group'
    form_fields = ['sent_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

    @staticmethod
    def live_method(player: Player, data):
        """if not player.group.get_player_by_id(2):
            print('Not')
            return"""

        channel_id = player.participant.ch_settings['id']
        read_api_key = player.participant.ch_settings['api_keys'][1]['api_key']

        # other_player = player.group.get_player_by_id(2)
        # print(other_player)
        # print(other_player.participant.label)
        # channel_id = other_player.participant.ch_settings['id']
        # read_api_key = other_player.participant.ch_settings['api_keys'][1]['api_key']
        # channel_id = player.participant.ch_settings['id']
        # read_api_key = player.participant.ch_settings['api_keys'][1]['api_key']
        # print(f'Channel ID: {channel_id}')
        # print(f'Read API Key: {read_api_key}')"""

        resp = getHeartRate(player.id_in_group, channel_id, read_api_key)
        if resp != 0:
            heartRate = resp["heartRate"]
            thingSpeakTime = resp["timeStamp"]
            oTreeTime = time.asctime()
            HeartRate.create(player=player, heartRate=heartRate, time=thingSpeakTime)
            player.actHeartRate = int(heartRate)
            result = {
                "heartRate": heartRate,
                "thingSpeakTime": thingSpeakTime,
                "oTreeTime": oTreeTime
            }
            return {0: result}
        else:
            return 0


class SendBackWaitPage(WaitPage):
    pass


class SendBack(Page):
    """This page is only for P2
    P2 sends back some amount (of the tripled amount received) to P1"""

    form_model = 'group'
    form_fields = ['sent_back_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        tripled_amount = group.sent_amount * C.MULTIPLIER
        return dict(tripled_amount=tripled_amount)


class ResultsWaitPage(WaitPage):
    # after_all_players_arrive = set_payoffs
    @staticmethod
    def after_all_players_arrive(group: Group):
        for player in group.get_players():
            created.stop_recording(player.participant.label)

        set_payoffs(group)


class Results(Page):
    """This page displays the earnings of each player"""

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        return dict(tripled_amount=group.sent_amount * C.MULTIPLIER)


page_sequence = [
    ConnectWaitPage,
    Introduction,
    Send,
    SendBackWaitPage,
    SendBack,
    ResultsWaitPage,
    Results,
]
