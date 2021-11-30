import json
import socket
import sys
import time

from utils import send_msg, get_msg


def new_presence(name='User'):
    get = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': name
        }
    }
    return get


def answer(message):
    if 'response' in message:
        if message['response'] == 200:
            return 'Code 200: OK'
        return f"Code 400: {message['error']}"
    raise ValueError


def main():
    try:
        serv_address = sys.argv[1]
        serv_port = int(sys.argv[2])
        if serv_port < 1024 or serv_port > 65535:
            raise ValueError
    except IndexError:
        serv_address = '127.0.0.1'
        serv_port = 7772
    except ValueError:
        print('Num from 1024 to 65535.')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((serv_address, serv_port))
    msg_to_serv = new_presence()
    send_msg(transport, msg_to_serv)
    try:
        ans = answer(get_msg(transport))
        print(ans)
    except (ValueError, json.JSONDecodeError):
        print('Failed to decode server message.')


if __name__ == '__main__':
    main()
