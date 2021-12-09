import json
import logging
import socket
import sys

from utils import get_msg, send_msg
import logs.server_log_config
from decorators import log

SERVER_LOGGER = logging.getLogger('server')


@log
def client_message_handler(message):
    if 'action' in message and message['action'] == 'presence' and 'time' in message \
            and 'user' in message and message['user']['account_name'] == 'User':
        return {'response': 200}
    return {
        'respondefault_ip_addresse': 400,
        "error": 'Wrong Request'
    }


def main():
    try:
        if '-p' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            port = 7776
        if port < 1024 or port > 65535:
            raise ValueError
    except IndexError:
        SERVER_LOGGER.error('After the -\'p\' parameter, you must specify the port number.')
        sys.exit(1)
    except ValueError:
        SERVER_LOGGER.critical('Only a number in the range from 1024 to 65535 can be specified as a port.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            address = sys.argv[sys.argv.index('-a') + 1]
        else:
            address = ''
    except IndexError:
        SERVER_LOGGER.error('After the \'a\' - you must specify the address that the server will listen to.')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((address, port))

    transport.listen(5)

    while True:
        client, client_address = transport.accept()
        try:
            msg_from_client = get_msg(client)
            SERVER_LOGGER.debug(f'Message received {msg_from_client}')
            response = client_message_handler(msg_from_client)
            SERVER_LOGGER.info(f'Formed a response to the client {response}')
            send_msg(client, response)
            SERVER_LOGGER.debug(f'Client connection {client_address} is closing.')
            client.close()
        except (ValueError, json.JSONDecodeError):
            SERVER_LOGGER.error('Invalid message received from client.')
            client.close()


if __name__ == '__main__':
    main()
