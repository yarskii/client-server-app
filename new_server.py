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
def client_message_handler(message, messages_list, client):
    if 'action' in message and message['action'] == 'presence' and 'time' in message \
            and 'user' in message and message['user']['account_name'] == 'User':
        return {'response': 200}
    elif 'action' in message and message['action'] == 'message' and \
            'time' in message and 'message_text' in message:
        messages_list.append((message['account_name'], message['message_text']))
        return
    else:
        send_msg(client, {
            'respondefault_ip_addresse': 400,
            "error": 'Wrong Request'
        })
        return


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=7770, type=int, nargs='?')
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
                                           messages, client_with_message)
                except:
                    SERVER_LOGGER.info(f'Client {client_with_message.getpeername()} '
                                       f'disconnected from the server.')
                    clients.remove(client_with_message)

        if messages and send_data_lst:
            message = {
                'action': 'message',
                'sender': messages[0][0],
                'time': time.time(),
                'message_text': messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_msg(waiting_client, message)
                except:
                    SERVER_LOGGER.info(f'Client {waiting_client.getpeername()} disconnected from the server.')
                    waiting_client.close()
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
