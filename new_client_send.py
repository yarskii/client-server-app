import argparse
import json
import logging
import socket
import sys
import time

from utils import send_msg, get_msg
import logs.client_log_config
from decorators import log

LOG = logging.getLogger('client')


@log
def message_from_server(message):
    if 'action' in message and message['action'] == 'message' and \
            'sender' in message and 'msg_text' in message:
        print(f'Received a message from the user '
              f'{message["sender"]}:\n{message["msg_text"]}')
        LOG.info(f'Received a message from the user '
                 f'{message["sender"]}:\n{message["msg_text"]}')
    else:
        LOG.error(f'Received an invalid message from the server: {message}')


@log
def create_message(sock, account_name='User'):
    message = input('Enter a message to send or \'!!! \' to shutdown: ')
    if message == '!!!':
        sock.close()
        LOG.info('Completion of work at the command of the user.')
        print('Thanks for using our service!')
        sys.exit(0)
    message_dict = {
        'action': 'message',
        'time': time.time(),
        'account_name': account_name,
        'msg_text': message
    }
    LOG.debug(f'The message dictionary has been formed: {message_dict}')
    return message_dict


@log
def new_presence(name='User'):
    get = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': name
        }
    }
    return get


@log
def answer(message):
    if 'response' in message:
        if message['response'] == 200:
            return 'Code 200: OK'
        return f"Code 400: {message['error']}"
    raise ValueError


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default='127.0.0.1', nargs='?')
    parser.add_argument('port', default=7770, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='send', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    serv_address = namespace.addr
    serv_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < serv_port < 65536:
        LOG.critical(
            f'Attempting to start a client with an invalid port number: {serv_port}. '
            f'Valid addresses are from 1024 to 65535. The client exits.')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        LOG.critical(f'Invalid operating mode specified {client_mode}, '
                     f'permissible modes: listen , send')
        sys.exit(1)

    return serv_address, serv_port, client_mode


def main():
    serv_address, serv_port, client_mode = arg_parser()

    LOG.info(
        f'Launched client with parameters: server address: {serv_address}, '
        f'port: {serv_port}, operating mode: {client_mode}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((serv_address, serv_port))
        msg_to_serv = new_presence()
        send_msg(transport, msg_to_serv)
        ans = answer(get_msg(transport))
        LOG.info(f'Received a response from the server {ans}')
        # print(ans)
    except (ValueError, json.JSONDecodeError):
        LOG.error('Failed to decode server message.')
        sys.exit(1)
    else:
        if client_mode == 'send':
            print('Mode of operation - sending messages.')
        else:
            print('Mode of operation - receiving messages.')
        while True:
            if client_mode == 'send':
                try:
                    send_msg(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    LOG.error(f'Server connection {serv_address} was lost.')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    message_from_server(get_msg(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    LOG.error(f'Server connection {serv_address} was lost.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
