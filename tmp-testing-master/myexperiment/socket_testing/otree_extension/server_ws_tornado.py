# While this code still works, I would recommend using Fast API for websockets in modern applications.
# See: https://fastapi.tiangolo.com/advanced/websockets/

# Note this is targeted at python 3
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.websocket
import tornado.options

LISTEN_PORT = 8001
LISTEN_ADDRESS = '127.0.0.1'


class ChannelHandler(tornado.websocket.WebSocketHandler):
    """
    Handler that handles a websocket channel
    """

    @classmethod
    def urls(cls):
        return [
            (r'/web-socket/', cls, {}),  # Route/Handler/kwargs
        ]

    def initialize(self):
        self.channel = None

    def open(self, channel):
        """
        Client opens a websocket
        """
        self.channel = channel

    def on_message(self, message):
        """
        Message received on channel
        """

    def on_close(self):
        """
        Channel is closed
        """

    def check_origin(self, origin):
        """
        Override the origin check if needed
        """
        return True


def main(opts):
    # Create tornado application and supply URL routes
    app = tornado.web.Application(ChannelHandler.urls())

    # Setup HTTP Server
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(LISTEN_PORT, LISTEN_ADDRESS)

    # Start IO/Event loop
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()