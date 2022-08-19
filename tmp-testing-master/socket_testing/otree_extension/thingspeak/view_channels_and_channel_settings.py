from typing import List, Dict

import requests

URL = 'https://api.thingspeak.com/'


def list_your_public_channels(user_id: str, tag: str = None) -> dict:
    """List channels for username with HTTP GET.

    See `MathWorks API Reference <https://de.mathworks.com/help/thingspeak/listyourpublicchannels.html>`_
    for more information.

    :param user_id: (Required) User ID for the channels of interest.
    :param tag: (Optional) Specify a tag to search for in public channels.
    :return: Returns the json-encoded content of a response to the GET request, if any.
    """
    url_request = f'{URL}users/{user_id}/channels.json'
    params = {'tag': tag}

    # The response is a JSON array of channel settings.
    response = requests.get(url_request, params=params)
    return response.json()


def list_your_channels(api_key: str, tag: str = None) -> List[dict]:
    """List your channels with HTTP GET.

    See `MathWorks API Reference <https://de.mathworks.com/help/thingspeak/listyourchannels.html>`_
    for more information.

    :param api_key: (Required) Specify User API Key, which you can find in your profile.
        This key is different from the channel API keys.
    :param tag: (Optional) Specify a tag to search for in your channels.
    :return: Returns the json-encoded content of a response to the GET request, if any.
    """
    url_request = f'{URL}channels.json'
    params = {
        'api_key': api_key,
        'tag': tag
    }

    # The response is a JSON object of your channels and has the license_id tag, if you are using a paid account.
    response = requests.get(url_request, params=params)
    return response.json()


def list_channels() -> dict:
    """List public channels with HTTP GET.

    See `MathWorks API Reference <https://de.mathworks.com/help/thingspeak/listchannels.html>`_ for more information.

    :return: Returns the json-encoded content of a response to the GET request, if any.
    """
    url_request = f'{URL}channels/public.json'

    # The response is a JSON object of public channels.
    response = requests.get(url_request)
    return response.json()


def read_settings(api_key: str, channel_id: int) -> dict:
    """Read channel settings with HTTP GET.

    See `MathWorks API Reference <https://de.mathworks.com/help/thingspeak/readsettings.html>`_ for more information.

    :param api_key: (Required for private channels) Specify User API Key, which you can find in your profile.
        This key is different from the channel API keys.
    :param channel_id: (Required) Channel ID for the channel of interest.
    :return: Returns the json-encoded content of a response to the GET request, if any.
    """
    url_request = f'{URL}channels/{channel_id}.json'
    params = {'api_key': api_key}

    # The response is a JSON object of the channel settings of (public) channel channel_id.
    response = requests.get(url_request, params=params)
    return response.json()


def write_settings(
        api_key: str,
        channel_id: int,
        description: str = None,
        field1: str = None,
        fieldX: Dict[str, str] = None,
        latitude: float = None,
        longitude: float = None,
        elevation: int = None,
        metadata: str = None,
        name: str = None,
        public_flag: bool = False,
        tags: List = None,
        url: str = None) -> dict:
    """Update channel settings with HTTP PUT.

    Use this request to write channel settings. Channel settings include channel description, field names,
    channel location, metadata, public or private status, and the name of the channel.

    See `MathWorks API Reference <https://de.mathworks.com/help/thingspeak/writesettings.html>`_ for more information.

    :param api_key: (Required) Specify User API Key, which you can find in your profile.
        This key is different from the channel API keys.
    :param channel_id: (Required) Channel ID for the channel of interest.
    :param description: (Optional) Description of the channel.
    :param field1: (Optional) Field 1 name.
    :param fieldX: (Optional) Field X name, where X is the field ID. Maximum of 8 fields.
        If the field1 key is passed again, the final value will be taken from here.
    :param latitude: (Optional) Latitude in degrees, specified as a value between -90 and 90.
    :param longitude: (Optional) Longitude in degrees, specified as a value between -180 and 180.
    :param elevation: (Optional) Elevation in meters.
    :param metadata: (Optional) Metadata for the channel, which can include JSON, XML, or any other data.
    :param name: (Optional) Name of the channel.
    :param public_flag: (Optional) Whether the channel is public. The default is false.
    :param tags: (Optional) Comma-separated list of tags.
    :param url: (Optional) Webpage URL for the channel.
    :return: Returns the json-encoded content of a response to the PUT request, if any.
    """
    url_request = f'{URL}channels/{channel_id}.json'
    data = {
        'api_key': api_key,
        'description': description,
        'field1': field1,
        'latitude': latitude,
        'longitude': longitude,
        'elevation': elevation,
        'metadata': metadata,
        'name': name,
        'public_flag': 'true' if public_flag else 'false',
        'tags': ','.join(tags) if tags is not None else '',
        'url': url
    }
    if fieldX is not None:
        data.update(fieldX)

    # The response is a JSON object of the updated channel information.
    response = requests.put(url_request, data=data)
    return response.json()
