import time
from multiprocessing import Pool, cpu_count

# Necessary to be able to start script manually from the terminal.
try:
    from .create_and_delete import *
    from .read_entry_age import *
    from .view_channels_and_channel_settings import *
except ImportError:
    from create_and_delete import *
    from read_entry_age import *
    from view_channels_and_channel_settings import *

USER_API_KEY = 'KWOJ1KJ7XY5HU60C'


def create_channel_wrapper(x):
    return create_channel(USER_API_KEY, field1='1', name=f'{x}')


def delete_channel_wrapper(x):
    return delete_channel(USER_API_KEY, x['id'])


if __name__ == '__main__':

    def create_with_pool():
        prev = time.time()

        inputs = list(range(32))
        num_cores = cpu_count()
        p = Pool(4)
        p.map(create_channel_wrapper, inputs)

        post = time.time()
        print(f'Create with pool: {post - prev}')


    def delete_with_pool():
        prev = time.time()

        inputs = list(list_your_channels(USER_API_KEY))
        num_cores = cpu_count()
        p = Pool(4)
        p.map(delete_channel_wrapper, inputs)

        post = time.time()
        print(f'Delete with pool: {post - prev}')


    def create_without_pool():
        prev = time.time()

        for i in range(32):
            create_channel(USER_API_KEY, field1='1', name=f'{i}')

        post = time.time()
        print(f'Create without pool: {post - prev}')


    def delete_without_pool():
        prev = time.time()

        for channel in list_your_channels(USER_API_KEY):
            delete_channel(USER_API_KEY, channel['id'])

        post = time.time()
        print(f'Delete without pool: {post - prev}')


    # create_with_pool()
    delete_with_pool()
    # create_without_pool()
    # delete_without_pool()
