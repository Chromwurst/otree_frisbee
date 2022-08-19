import asyncio
from functools import singledispatch
from typing import overload
import big_o


def stop_recording(*participant_labels):
    print('Stop recording')
    print(participant_labels)


participants = ['abc', 'def', 'xyz']


# stop_recording('abc', 'def', 'xyz')


def send(*args):
    pass


# Version 1
def stop_recording1(*participant_labels, to_all=False):
    send(participant_labels)
    if to_all:
        print('Send to all')
    else:
        print(f'Send to {participant_labels}')
        print(*participant_labels)


# stop_recording1('Alice', 'Bob', 'Charlie')
# stop_recording1(to_all=True)


# Version 2
@singledispatch
def stop_recording2(*participant_labels, to_all=False):
    send(participant_labels)
    print(*participant_labels)
    print(to_all)


@stop_recording2.register(list)
def _(participant_labels: list, to_all=False):
    print('Call overload')
    stop_recording2(*participant_labels, to_all=to_all)


"""@stop_recording2.register()
def _(to_all=False):
    print('Call overload none')
    stop_recording2(None, to_all=to_all)"""

"""def noting(to_all):
    stop_recording2(to_all=to_all)


stop_recording2.register(type(None), noting(True))"""


@stop_recording2.register(type(None))
def _(participant_label, to_all=True):
    print('None')
    stop_recording2('', to_all=to_all)


"""@stop_recording2.register(str)
def _(participant_labels: str, to_all=False):
    print('Call overload string')
    stop_recording2(participant_labels, to_all=to_all)"""


# stop_recording2(['Alice', 'Bob', 'Charlie'])
# stop_recording2(None, to_all=True)


def stop_recording3(*participant_labels, to_all=False):
    pass


@singledispatch
def _helper_stop_recording(participant_labels, to_all=False):
    print('single')
    print(participant_labels)
    print(to_all)


@_helper_stop_recording.register(list)
def _(participant_labels, to_all=False):
    print('list')
    print(participant_labels)
    print(to_all)


def stop_recoding4(*participant_labels):
    _helper_stop_recording(participant_labels)


# stop_recoding4('Alice', 'Bob', 'Charlie')


def pause_recording(*participant_labels, to_all=False):
    # assert (participant_labels is not None and to_all is True), \
    #     'Please pass one or more participant labels or set to_all=True'

    for participant_label in participant_labels:
        print(1)

    every = ('Alice', 'Bob', 'Charlie')
    for one in every:
        print('One')


# pause_recording()


def test(*args):
    print(args)
    print(type(args))


def test_len():
    test_list = list()
    test_list.append("Bob")
    test_set = set()
    test_set.add("Bob")
    test_tuple = ("Bob",)

    print(f'Type list {type(test_list)}')
    print(f'Type set {type(test_set)}')
    print(f'Type tuple {type(test_tuple)}')

    print(f'len list {len(test_list)}')
    print(f'len set {len(test_set)}')
    print(f'len tuple {len(test_tuple)}')

    test_list, = test_list
    test_set, = test_set
    test_tuple, = test_tuple

    print(f'Unpacked Type list {type(test_list)}')
    print(f'Unpacked Type set {type(test_set)}')
    print(f'Unpacked Type tuple {type(test_tuple)}')

    print(f'Unpacked Value list {test_list}')
    print(f'Unpacked Value set {test_set}')
    print(f'Unpacked Value tuple {test_tuple}')

    """test = "Bob"
    print(test)
    test, = test
    print(test)
    """


# test_len()

test_list = ['Alice', 'Bob']
# print(type(test_list))

converted = tuple(test_list)

# print(type(converted))


from server_ws import FrisbeeCom as fc


def test_unpack():
    # Case 1 - TypeError: object of type 'NoneType' has no len()
    # labels = None
    # print(f'Unpack case 1: {fc.unpack(labels)} and {type(fc(labels))}')

    # Case 2
    labels = ('Alice',)
    unpacked_labels = fc.unpack(labels)
    print(f'Unpack case 2: {unpacked_labels} and {type(unpacked_labels)}')

    # Case 3
    labels = ('Alice', 'Bob')
    unpacked_labels = fc.unpack(labels)
    print(f'Unpack case 3: {unpacked_labels} and {type(unpacked_labels)}')

    # Case 4
    labels = (['Alice'],)
    unpacked_labels = fc.unpack(labels)
    print(f'Unpack case 4: {unpacked_labels} and {type(unpacked_labels)}')

    # Case 5
    labels = (['Alice', 'Bob'],)
    unpacked_labels = fc.unpack(labels)
    print(f'Unpack case 5: {unpacked_labels} and {type(unpacked_labels)}')

    # Case chaos
    labels = ('Alice', ['Bob', 'Charlie'])
    # unpacked_labels = fc.unpack(labels)
    unpacked_labels = enumerate(labels)
    print(f'Unpack case chaos: {unpacked_labels} and {type(unpacked_labels)}')
    for label in unpacked_labels:
        print(label)


# test_unpack()


def test_with_cache(labels):
    # labels = ('Alice', ['Bob', 'Charlie'], 'Alex', ['Fabian', 'Max'], 'Jakob')
    # cache = list()

    for label in labels:

        to_cache = fc.unpack(label)  # tuple

        while True:
            if all(isinstance(l, str) for l in to_cache):

                if isinstance(to_cache, str):
                    # cache.append(to_cache)
                    yield to_cache
                else:
                    for l in to_cache:
                        # cache.append(l)
                        yield l
                break
            else:
                to_cache = fc.unpack(to_cache)

    # return cache


# participant_labels = ('Alice', ('Debora', 'Hanna'), ['Sarah'], ['Bob', 'Charlie'], 'Alex', ['Fabian', 'Max'], 'Jakob')
participant_labels = (['Alice', 'Bob'],)
# print(test_with_cache(participant_labels))

"""
y = list()
for t in test_with_cache(participant_labels):
    print(t)
    y.append(t)

print(y) """

# Generating random test strings of length 100
# sample_strings = lambda n: big_o.datagen.strings(100)
sample_strings = lambda n: ('Alice', ['Bob', 'Charlie'], 'Alex', ['Fabian', 'Max'], 'Jakob')

# Calculating the Time complexity
# best, others = big_o.big_o(test_with_cache, sample_strings, n_measures=1000000)
# best, others = big_o.big_o(test_with_cache, sample_strings, n_repeats=100, n_measures=100)
# print(best)
# print(others)


async def first():
    for i in range(10):
        print(f'First {i}')
        await asyncio.sleep(1)


async def second():
    for i in range(10):
        print(f'Second {i}')
        await asyncio.sleep(1)


loop = asyncio.get_event_loop()
loop.run_until_complete(first())
loop.run_until_complete(second())
loop.close()
