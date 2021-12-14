import argparse
import json
import logging
import socket
import sys
import threading
import time

from utils import send_msg, get_msg
import logs.client_log_config
from decorators import log

LOG = logging.getLogger('client')


@log
def create_exit_message(account_name):
    return {
        'action': 'exit',
        'time': time.time(),
        'account_name': account_name
    }


@log
def message_from_server(sock, my_username):
    while True:
        try:
            message = get_msg(sock)
            if 'action' in message and message['action'] == 'message' and \
                    'sender' in message and 'destination' in message and \
                    'message_text' in message and message['destination'] == my_username:
                print(f'Received a message from the user '
                      f'{message["sender"]}:\n{message["message_text"]}')
                LOG.info(f'Received a message from the user '
                         f'{message["sender"]}:\n{message["message_text"]}')
            else:
                LOG.error(f'Received an invalid message from the server: {message}')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            LOG.critical(f'Lost connection to server.')
            break


@log
def create_message(sock, account_name='User'):
    to_user = input('Enter the recipient of the message: ')
    message = input('Enter a message to send: ')

    message_dict = {
        'action': 'message',
        'sender': account_name,
        'destination': to_user,
        'time': time.time(),
        'message_text': message
    }
    LOG.debug(f'The message dictionary has been formed: {message_dict}')
    try:
        send_msg(sock, message_dict)
        LOG.info(f'Message sent to user {to_user}')
    except:
        LOG.critical('Lost connection to server.')
        sys.exit(1)


@log
def user_interactive(sock, username):
    print_help()
    while True:
        command = input('Enter the command: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_msg(sock, create_exit_message(username))
            print('Termination of the connection.')
            LOG.info('Completion of work at the command of the user.')
            time.sleep(0.5)
            break
        else:
            print('Command not recognized, try again. help - display supported commands.')


def print_help():
    print('Supported commands:')
    print('message - send a message. Who and the text will be requested separately.')
    print('help - display command tips')
    print('exit - exit the program')


@log
def new_presence(account_name):
    get = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': account_name
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
    parser.add_argument('port', default=7771, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    serv_address = namespace.addr
    serv_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < serv_port < 65536:
        LOG.critical(
            f'Attempting to start a client with an invalid port number: {serv_port}. '
            f'Valid addresses are from 1024 to 65535. The client exits.')
        sys.exit(1)

    return serv_address, serv_port, client_mode


def main():
    serv_address, serv_port, client_name = arg_parser()

    print(f'Console messenger. Client module. Username: {client_name}')

    if not client_name:
        client_name = input('Enter your username: ')

    LOG.info(
        f'Launched client with parameters: server address: {serv_address}, '
        f'port: {serv_port}, operating mode: {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((serv_address, serv_port))
        send_msg(transport, new_presence(client_name))
        ans = answer(get_msg(transport))
        LOG.info(f'Received a response from the server {ans}')
        # print(ans)
    except (ValueError, json.JSONDecodeError):
        LOG.error('Failed to decode server message.')
        sys.exit(1)
    else:
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        LOG.debug('Processes started')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
