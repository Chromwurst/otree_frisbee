import json
from channels.generic.websocket import WebsocketConsumer


# from asgiref.sync import async_to_sync


class FbClientConsumer(WebsocketConsumer):
    def connect(self):
        """
        Execute code on connection start.
        """

        # self.accept()

        print('Trying to connect ...')

        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Client is now connected!'
        }))

        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print('Message', message)

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))

    def disconnect(self, code):
        return
