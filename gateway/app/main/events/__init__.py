"""
This file exists to provide a route to websocket events.
"""
from .. import ws

from .webrtc_events import *
from .control_events import *
from .fl_events import *

from .socket_handler import SocketHandler

from ..codes import *

import json

# Websocket events routes
# This structure allows compatibility between javascript applications (syft.js/grid.js) and PyGrid.
routes = {
    CONTROL_EVENTS.SOCKET_PING: socket_ping,
    WEBRTC_EVENTS.JOIN_ROOM: scope_broadcast,
    WEBRTC_EVENTS.INTERNAL_MSG: internal_message,
    WEBRTC_EVENTS.PEER_LEFT: scope_broadcast,
    FL_EVENTS.AUTHENTICATE: authenticate,
    FL_EVENTS.CYCLE_REQUEST: cycle_request,
    FL_EVENTS.REPORT: report,
}


handler = SocketHandler()


def route_requests(message, socket):
    """ Handle a message from websocket connection and route them to the desired method.

        Args:
            message : message received.
        Returns:
            message_response : message response.
    """
    global routes

    message = json.loads(message)
    return routes[message[MSG_FIELD.TYPE]](message, socket)


@ws.route("/")
def socket_api(socket):
    """ Handle websocket connections and receive their messages.
    
        Args:
            socket : websocket instance.
    """
    while not socket.closed:
        message = socket.receive()
        if not message:
            continue
        else:
            # Process received message
            response = route_requests(message, socket)
            socket.send(response)

    worker_id = handler.remove(socket)
