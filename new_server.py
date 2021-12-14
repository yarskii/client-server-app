import argparse
import json
import logging
import select
import socket
import sys
import time

from utils import get_msg, send_msg
import logs.server_log_config
from decorators import log

SERVER_LOGGER = logging.getLogger('server')


@log
def client_message_handler(message, messages_list, client, clients, names):
    SERVER_LOGGER.debug(f'Parsing a message from a client: {message}')
    if 'action' in message and message['action'] == 'presence' and 'time' in message \
            and 'user' in message:
        if message['user']['account_name'] not in names.keys():
            names[message['user']['account_name']] = client
            send_msg(client, {'response: 200'})
        else:
            response = {'response': 400, 'error': 'The username is already taken.'}
            send_msg(client, response)
            clients.remove(client)
            client.close()
        return
    elif 'action' in message and message['action'] == 'message' and \
            'time' in message and 'message_text' in message and \
            'destination' in message and 'sender' in message:
        messages_list.append(message)
        return
    elif 'action' in message and message['action'] == 'exit' and 'account_name' in message:
        clients.remove(names[message["account_name"]])
        names[message['account_name']].close()
        del names[message['account_name']]
        return
    else:
        response = {'response': 400, 'error': 'The request is invalid.'}
        send_msg(client, response)
        return


@log
def process_message(message, names, listen_socks):
    if message['destination'] in names and names[message['destination']] in listen_socks:
        send_msg(names[message['destination']], message)
        SERVER_LOGGER.info(f'Message sent to user {message["destination"]} '
                           f'from user {message["sender"]}.')
    elif message['destination'] in names and names[message['destination']] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f'User {message["destination"]} not registered on the server, '
            f'sending the message is not possible.')


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=7771, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    address = namespace.a
    port = namespace.p

    if not 1023 < port < 65536:
        SERVER_LOGGER.critical(
            f'Attempting to start the server with an invalid port '
            f'{port}. Valid addresses are from 1024 to 65535.')
        sys.exit(1)

    return address, port


def main():
    address, port = arg_parser()

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((address, port))
    transport.settimeout(0.5)

    clients = []
    messages = []

    names = dict()

    transport.listen(5)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'PC connection established {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    client_message_handler(get_msg(client_with_message),
                                           messages, client_with_message, clients, names)
                except Exception:
                    SERVER_LOGGER.info(f'Client {client_with_message.getpeername()} '
                                       f'disconnected from the server.')
                    clients.remove(client_with_message)

        for i in messages:
            try:
                process_message(i, names, send_data_lst)
            except Exception:
                SERVER_LOGGER.info(f'Customer contact with name {i["destination"]} was lost')
                clients.remove(names[i['destination']])
                del names[i['destination']]
        messages.clear()


if __name__ == '__main__':
    main()
