import os.path
from os import environ

# import Python modules without installing
# import sys
# sys.path.append(os.path.dirname('../myexperiment'))
# print('os.path.dirname' + os.path.dirname('myexperiment'))
# sys.path.append(os.path.dirname('myexperiment'))

import sys

# print('current dir: ' + os.path.dirname(__file__))
# sys.path.append(os.path.dirname(__file__))

# sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


SESSION_CONFIGS = [
    dict(
        name='guess_two_thirds',
        display_name="Guess 2/3 of the Average",
        app_sequence=['guess_two_thirds', 'payment_info'],
        num_demo_participants=3,
    ),
    dict(
        name='survey', app_sequence=['survey', 'payment_info'], num_demo_participants=1
    ),
    dict(
        name='socket_testing', app_sequence=['socket_testing'], num_demo_participants=1
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['websocket']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
# ADMIN_PASSWORD = 'admin'

# AUTH_LEVEL = 'STUDY'

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""

SECRET_KEY = '4455030880430'

INSTALLED_APPS = ['otree']
