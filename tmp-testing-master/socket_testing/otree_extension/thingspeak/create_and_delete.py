from typing import List, Dict

import requests

URL = 'https://api.thingspeak.com/'


def create_channel(
        api_key: str,
        description: str = None,
        field1: str = None,
        fieldX: Dict[str, str] = None,
        latitude: float = None,
        longitude: float = None,
        metadata: str = None,
        name: str = None,
        public_flag: bool = False,
        tags: List = None,
        url: str = None):
    """Create new channel with HTTP POST.

    See `MathWorks API Reference <https://de.mathworks.com/help/thingspeak/createchannel.html>`_ for more information.

    :param api_key: (Required) Specify User API Key, which you can find in your profile.
        This key is different from the channel API keys.
    :param description: (Optional) Specify an ID or name for the client making the request.
    :param field1: (Optional) Field 1 name.
    :param fieldX: (Optional) Field X name, where X is the field ID. Maximum of 8 fields.
        If the field1 key is passed again, the final value will be taken from here.
    :param latitude: (Optional) Latitude in degrees.
    :param longitude: (Optional) Longitude in degrees.
    :param metadata: (Optional) Metadata for the channel, which can include JSON, XML, or any other data.
    :param name: (Optional) Name of the channel.
    :param public_flag: (Optional) Whether the channel is public. The default is false.
    :param tags: (Optional) Comma-separated list of tags.
    :param url: (Optional) Web page URL for the channel.
    :return: Returns the json-encoded content of a response to the POST request, if any.
    """
    url_request = f'{URL}channels.json'
    data = {
        'api_key': api_key,
        'description': description,
        'field1': field1,
        'latitude': latitude,
        'longitude': longitude,
        'metadata': metadata,
        'name': name,
        'public_flag': 'true' if public_flag else 'false',
        'tags': ','.join(tags) if tags is not None else '',
        'url': url
    }
    if fieldX is not None:
        data.update(fieldX)

    response = requests.post(url_request, data=data)
    return response.json()


def clear_channel(api_key: str, channel_id: int):
    """Clear all data from channel with HTTP DELETE.

    See `MathWorks API Reference <https://de.mathworks.com/help/thingspeak/clearchannel.html>`_ for more information.

    :param api_key: (Required) Specify User API Key, which you can find in your profile.
        This key is different from the channel API keys.
    :param channel_id: (Required) Channel ID for the channel of interest, specified as an integer.
    :return: Returns the json-encoded content of a response to the DELETE request, if any.
    """
    url_request = f'{URL}channels/{channel_id}/feeds.json'
    data = {'api_key': api_key}

    response = requests.delete(url_request, data=data)
    return response.json()


def delete_channel(api_key: str, channel_id: int):
    """Delete channel with HTTP DELETE.

    See `MathWorks API Reference <https://de.mathworks.com/help/thingspeak/deletechannel.html>`_ for more information.

    :param api_key: (Required) Specify User API Key, which you can find in your profile.
        This key is different from the channel API keys.
    :param channel_id: (Required) Channel ID for the channel of interest, specified as an integer.
    :return: Returns the json-encoded content of a response to the DELETE request, if any.
    """
    url_request = f'{URL}channels/{channel_id}.json'
    data = {'api_key': api_key}

    response = requests.delete(url_request, data=data)
    return response.json()
