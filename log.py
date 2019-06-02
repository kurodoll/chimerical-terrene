import datetime
from colorama import init, Fore, Style

init()  # colorama


def log(caller, message, level='log'):
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
    elif level == 'debug (network)':
        print(f'[{Fore.BLUE}', end='')
    else:
        print('[', end='')

    # Print the caller and the message.
    print(f'{caller}{Style.RESET_ALL}] {message}')
