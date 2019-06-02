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
clients = {}


@sio.on('connect')
def connect(sid, env):
    log('server.py', f'Connected: {sid}', 'debug (network)')

    clients[sid] = {
        'online': True,
        'logged_in': False,
        'characters': {}
    }


# User is logging in.
# TODO: Actually handle user accounts.
# TODO: Prevent abuse via multiple logins and stuff. A user could login to the
#       same user from 2 different locations atm.
@sio.on('login')
def login(sid, details):
    if clients[sid]['logged_in']:
        return

    # Give user the name ANONYMOUS if they didn't enter a username.
    if (details['username'] == ''):
        details['username'] = 'ANONYMOUS'

    log('server.py', f'Login from {details["username"]}', 'debug (network)')

    clients[sid]['logged_in'] = True
    clients[sid]['username'] = details['username']

    sio.emit('logged in', room=sid)


@sio.on('character selected')
def character_selected(sid, details):
    if not clients[sid]['logged_in']:
        return

    # Give character the name ANONYMOUS if user didn't enter a name.
    if (details['name'] == ''):
        details['name'] = 'ANONYMOUS'

    if details['name'] in clients[sid]['characters']:
        pass  # TODO: Implement this.
    else:
        log(
            'server.py',
            f'{clients[sid]["username"]} made new character {details["name"]}',
            'debug'
        )

        character = GameManager.newCharacter(details)
        clients[sid]['characters'][details['name']] = character

        sio.emit('character initialized', room=sid)


# TODO: Clean up user account and character stuff on disconnect.
@sio.on('disconnect')
def disconnect(sid):
    log('server.py', f'Disconnected: {sid}', 'debug (network)')
    clients[sid]['online'] = False


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
