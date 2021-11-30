import json
import socket
import sys

from utils import get_msg, send_msg


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
            port = 7772
        if port < 1024 or port > 65535:
            raise ValueError
    except IndexError:
        print('After the -\'p\' parameter, you must specify the port number.')
        sys.exit(1)
    except ValueError:
        print('Only a number in the range from 1024 to 65535 can be specified as a port.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            address = sys.argv[sys.argv.index('-a') + 1]
        else:
            address = ''
    except IndexError:
        print('After the \'a\' - you must specify the address that the server will listen to.')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((address, port))

    transport.listen(5)

    while True:
        client, client_address = transport.accept()
        try:
            msg_from_client = get_msg(client)
            print(msg_from_client)
            response = client_message_handler(msg_from_client)
            send_msg(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Invalid message received from client.')
            client.close()


if __name__ == '__main__':
    main()
