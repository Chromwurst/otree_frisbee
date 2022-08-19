import copy
from dataclasses import dataclass

from .create_and_delete import *
from .view_channels_and_channel_settings import *
from .read_entry_age import *


@dataclass(kw_only=True)  # kw_only requires Python 3.10
class ChannelConfig:
    api_key: str
    description: str = None
    field1: str = None
    fieldX: Dict[str, str] = None
    latitude: float = None
    longitude: float = None
    metadata: str = None
    name: str = None
    public_flag: bool = False
    tags: List = None
    url: str = None
    use_participant_specific_preface: bool = True


class ChannelManager:

    def __init__(self, ch_config: ChannelConfig):
        # , required_fields_per_channel: int
        # self.required_fields_per_channel = required_fields_per_channel
        self.ch_config = ch_config
        self.user_api_key = ch_config.api_key

        # when using assign_field
        self.field_counter = 0
        self.current_channel = None
        self.used_channels = list()

    def assign_channel(self, participant_label: str) -> dict:
        """Create a ThingSpeak channel and assign it to the participant defined in participant label.

        :param participant_label: (Required) Specify participant.
        :param fieldX: (Required) Field X name, where X is the field ID. Maximum of 8 fields.
        :return: Channel settings of the newly created channel.
        """
        cc = self.ch_config

        # Use participant specific preface / Add Frisbee Naming
        if self.ch_config.use_participant_specific_preface:
            # If the channel config is modified elsewhere in the future (for a specific participant),
            # the copy must be made before this if statement.
            cc = copy.deepcopy(self.ch_config)
            cc.description = f"Data sent from Client of Participant {participant_label}. " \
                             f"{cc.description if cc.description is not None else ''}"
            cc.name = f"{participant_label} {cc.name if cc.name is not None else ''}"
            if cc.tags is not None:
                cc.tags = ['frisbee', 'participant-data', *cc.tags]
            else:
                cc.tags = ['frisbee', 'participant-data']

        return create_channel(api_key=cc.api_key,
                              description=cc.description,
                              fieldX=cc.fieldX,
                              latitude=cc.latitude,
                              longitude=cc.longitude,
                              metadata=cc.metadata,
                              name=cc.name,
                              public_flag=cc.public_flag,
                              tags=cc.tags,
                              url=cc.url)

    # Don't use at the moment.
    def assign_field(self):
        if self.current_channel is None:
            delete_all_your_channels(self.user_api_key)
            response = create_channel(self.user_api_key, public_flag=False)

            self.current_channel = response['id']
            self.used_channels.append(self.current_channel)
            print(f'Current Channel ID: {self.current_channel}')
            print(f'Used channels: {self.used_channels}')

        if self.field_counter < 8:
            self.field_counter = self.field_counter + 1

        else:
            self.field_counter = 1
            response = create_channel(self.user_api_key, public_flag=False)

            self.current_channel = response['id']
            self.used_channels.append(self.current_channel)
            print(f'Current Channel ID: {self.current_channel}')
            print(f'Used channels: {self.used_channels}')

        config = write_settings(self.user_api_key, self.current_channel,
                                fieldX={f'field{self.field_counter}': f'participant-{self.field_counter}-data'})

        config = {
            'api_key': config['api_keys'][0]['api_key'],
            'channel_id': config['id'],
            'field_id': self.field_counter
        }

        return config


def delete_all_your_public_channels(api_key: str, user_id: str, tag: str = None) -> None:
    """Delete all public channels of the account specified by the User ID.

    Only public channels for which the corresponding User API key is known can be deleted.

    :param api_key: (Required) Specify User API Key, which you can find in your profile.
        This key is different from the channel API keys.
    :param user_id: (Required) User ID for the channels of interest.
    :param tag: (Optional) Specify a tag to search for in public channels.
    """
    all_channels = list_your_public_channels(user_id, tag)

    for channel in all_channels:
        delete_channel(api_key, channel['id'])


def delete_all_your_channels(api_key: str) -> None:
    """Delete all channels of the account specified by the User API Key.

    :param api_key: (Required) Specify User API Key, which you can find in your profile.
        This key is different from the channel API keys.
    """
    all_channels = list_your_channels(api_key)

    for channel in all_channels:
        delete_channel(api_key, channel['id'])
