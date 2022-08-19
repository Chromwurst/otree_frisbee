from otree.api import *

from .otree_extension import server_echo
from .otree_extension.server_ws import FrisbeeCom, Instructions

from pathlib import Path

from otree import settings

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'socket_testing'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


def creating_session(subsession: Subsession):
    pass
    # created = FrisbeeCom()
    # conns = created.create_com()
    # print('Created FrisbeeCom')


# PAGES
class MyPage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict()

    # server_echo.start()

    @staticmethod
    def live_method(player: Player, data):
        if data == 1:
            created.start_recording()
        if data == 2:
            created.pause_recording()
        if data == 3:
            created.stop_recording()


# test_multiprocessing
created = FrisbeeCom(host='127.0.0.1', port=8001)
print(f'HOST: {created._host}')
print(f'Port: {created._port}')
conns = created.start_ws_server()
Path("/tmp/app-initialized").touch()
conns[0].send('Test send')
print(f'User: {settings.ADMIN_USERNAME} with Password: {settings.ADMIN_PASSWORD}')


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
