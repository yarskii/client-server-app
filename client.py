import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import get_mess, send_mess


def create_presence(account_name='New_User'):
    getting = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return getting


def process_answer(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():
    try:
        serv_address = sys.argv[1]
        serv_port = int(sys.argv[2])
        if serv_port < 1024 or serv_port > 65535:
            raise ValueError
    except IndexError:
        serv_address = DEFAULT_IP_ADDRESS
        serv_port = DEFAULT_PORT
    except ValueError:
        print('Only a number in the range from 1024 to 65535 can be specified as a port.')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((serv_address, serv_port))
    mess_to_serv = create_presence()
    send_mess(transport, mess_to_serv)
    try:
        answer = process_answer(get_mess(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Failed to decode server message.')


if __name__ == '__main__':
    main()

