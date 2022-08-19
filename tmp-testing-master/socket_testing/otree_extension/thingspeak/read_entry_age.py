from typing import Optional

import requests

URL = 'https://api.thingspeak.com/'


def read_last_entry_age(read_api_key: Optional[str], channel_id: int) -> dict:
    """Read number of seconds since last entry in channel with HTTP GET.

    See `MathWorks API Reference <https://de.mathworks.com/help/thingspeak/readlastentryage.html>`_
    for more information.

    :param read_api_key: (Required) Specify Read API Key for the channel of interest.
        Not required for public channels, None can be passed instead.
    :param channel_id: (Required) Channel ID for the channel of interest.
    :return: Returns the json-encoded content of a response to the GET request, if any.
        If you do not have access to the channel, the response is -1.
    """
    url_request = f'{URL}channels/{channel_id}/feeds/last_data_age.json'
    data = {'api_key': read_api_key}

    # The response is a JSON object with the age of the most recent value, in seconds.
    response = requests.get(url_request, data=data)
    return response.json()


def read_last_field_entry_age(read_api_key: Optional[str], channel_id: int, field_id: int) -> dict:
    """Read number of seconds since last entry in field with HTTP GET.

    See `MathWorks API Reference <https://de.mathworks.com/help/thingspeak/readlastfieldentryage.html>`_
    for more information.

    :param read_api_key: (Required) Specify Read API Key for the channel of interest.
        Not required for public channels, None can be passed instead.
    :param channel_id: (Required) Channel ID for the channel of interest.
    :param field_id: (Required) Field ID for the field of interest.
    :return: Returns the json-encoded content of a response to the GET request, if any.
        If you do not have access to the channel, the response is -1.
    """
    url_request = f'{URL}channels/{channel_id}/fields/{field_id}/last_data_age.json'
    data = {'api_key': read_api_key}

    # The response is a JSON object with the age of the most recent value, in seconds.
    response = requests.get(url_request, data=data)
    return response.json()
