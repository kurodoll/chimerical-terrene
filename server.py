from log import log
from Game import Manager

import json
import os

import eventlet
import socketio


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#                                                                     Game Init
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
GameManager = Manager.Manager()


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#                                                                Socket.io Init
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
sio = socketio.Server()

# Load static files that are to be served to clients.
try:
    static_files = json.load(open(GameManager.config['files']['static_files']))
    log(
        'server.py',
        f'Loaded {GameManager.config["files"]["static_files"]} successfully.'
    )
except IOError:
    log(
        'server.py',
        f'Failed to open {GameManager.config["files"]["static_files"]}',
        'fatal error'
    )
    exit()

app = socketio.WSGIApp(sio, static_files=static_files)


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#                                                            Client Interaction
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
@sio.on('connect')
def connect(sid, env):
    log('server.py', f'Connected: {sid}', 'debug (network)')


@sio.on('disconnect')
def disconnect(sid):
    log('server.py', f'Disconnected: {sid}', 'debug (network)')


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#                                                                          Main
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
if __name__ == '__main__':
    port = GameManager.config['server']['default_port']

    # Check whether a port has been specified as an envvar (e.g. for Heroku).
    if 'PORT' in os.environ.keys():
        port = int(os.environ['PORT'])

    # Start the server.
    log('server.py', f'Starting server on port {port}.')
    eventlet.wsgi.server(eventlet.listen(('', port)), app)
