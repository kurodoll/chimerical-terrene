from log import log
from log import logSetVars
from Game import Manager

import json
import os

import eventlet
import socketio


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#                                                                     Game Init
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
sio = socketio.Server()

GameManager = Manager.Manager(sio)
logSetVars(GameManager)


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#                                                                Socket.io Init
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
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

    sio.emit('logged in', sid, room=sid)


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

        character = GameManager.newCharacter(details, sid)
        clients[sid]['characters'][details['name']] = character
        clients[sid]['using_character'] = details['name']

        sio.emit('character initialized', room=sid)


# User wants the data of the level that their character is currently on.
@sio.on('get present level')
def get_present_level(sid):
    if not clients[sid]['online']:
        return

    character = clients[sid]['characters'][clients[sid]['using_character']]
    on_level = character.getComp('position').get('on_level')
    level = GameManager.WorldManager.getLevelJSON(on_level)

    sio.emit('present level', level, room=sid)

    sio.emit(
        'player stats',
        character.getComp('stats').toJSON(),
        room=sid
    )

    # Link the client to the level, so that they recieve updates to the level.
    GameManager.link(sid, on_level)


# User has played an action.
@sio.on('action')
def action(sid, type_, details):
    if not clients[sid]['online']:
        return

    GameManager.queueAction(sid, type_, details)


# User sent a console command.
# TODO: Only allow admins to send console commands.
@sio.on('console command')
def console_command(sid, command_str):
    command = command_str.split(' ')

    if len(command) == 2:
        if command[0] == 'monitor':
            GameManager.addMonitor(command[1], sid)


# TODO: Clean up user account and character stuff on disconnect.
@sio.on('disconnect')
def disconnect(sid):
    log('server.py', f'Disconnected: {sid}', 'debug (network)')
    clients[sid]['online'] = False

    if 'using_character' in clients[sid]:
        character = clients[sid]['characters'][clients[sid]['using_character']]
        GameManager.EntityManager.markDeleted(character.id)


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#                                                                       Threads
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def processTicks():
    while True:
        GameManager.processActions()
        GameManager.emitUpdates()

        sio.sleep(0.01)


def updateEntities():
    while True:
        GameManager.WorldManager.updateEntities()
        sio.sleep(2)


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#                                                                          Main
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
if __name__ == '__main__':
    port = GameManager.config['server']['default_port']

    # Check whether a port has been specified as an envvar (e.g. for Heroku).
    if 'PORT' in os.environ.keys():
        port = int(os.environ['PORT'])

    # Start threads.
    sio.start_background_task(processTicks)
    sio.start_background_task(updateEntities)

    # Start the server.
    log('server.py', f'Starting server on port {port}.')
    eventlet.wsgi.server(eventlet.listen(('', port)), app)
