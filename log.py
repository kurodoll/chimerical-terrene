import datetime
from colorama import init, Fore, Style

init()  # colorama

Manager = None
last_msgs = []

log_levels = [ 'debug(2)', 'debug (network)', 'debug', 'log', 'warning', 'error', 'fatal error' ]  # noqa
log_level = 1


def logSetVars(Manager_):
    global Manager
    Manager = Manager_


def log(caller, message, level='log'):
    log_level_index = log_levels.index(level)
    if log_level_index < log_level:
        return

    # Print the current date & time.
    now = datetime.datetime.now()
    print(f'{Fore.BLACK}{Style.BRIGHT}{now}{Style.RESET_ALL}', end=' ')

    # Set appropriate colour for the specified log level.
    if level == 'fatal error':
        print(f'[{Fore.MAGENTA}', end='')
    elif level == 'error':
        print(f'[{Fore.RED}', end='')
    elif level == 'warning':
        print(f'[{Fore.YELLOW}', end='')
    elif level == 'log':
        print(f'[{Fore.GREEN}', end='')
    elif level == 'debug':
        print(f'[{Fore.CYAN}', end='')
    elif level == 'debug(2)':
        print(f'[{Fore.CYAN}', end='')
    elif level == 'debug (network)':
        print(f'[{Fore.BLUE}', end='')
    else:
        print('[', end='')

    # Print the caller and the message.
    print(f'{caller}{Style.RESET_ALL}] {message}')

    # Keep a record of recent messages.
    msg = str(now) + ' (' + level + ') [' + caller + '] ' + message

    last_msgs.append(msg)
    if len(last_msgs) > 10:
        last_msgs.pop(0)

    # Distribute log data to monitoring clients.
    if Manager:
        if 'log' in Manager.monitors:
            for sid in Manager.monitors['log']:
                Manager.sio.emit('monitor update', {
                    'monitor': 'log',
                    'data': {
                        'history': last_msgs
                    }
                }, room=sid)
