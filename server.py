import socket
import sys
import json
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, RESPONDEFAULT_IP_ADDRESSE
from common.utils import get_mess, send_mess


def clients_massage_handler(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'New_User':
        return {RESPONSE: 200}
    return {
        RESPONDEFAULT_IP_ADDRESSE: 400,
        ERROR: 'Wrong Request'
    }


def main():
    try:
        if '-p' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            port = DEFAULT_PORT
        if port < 1024 or port > 65535:
            raise ValueError
    except IndexError:
        print('After the -\'p\' parameter, you must specify the port number.')
        sys.exit(1)
    except ValueError:
        print(
            'Only a number in the range from 1024 to 65535 can be specified as a port.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            address = sys.argv[sys.argv.index('-a') + 1]
        else:
            address = ''

    except IndexError:
        print(
            'After the \'a\' - you must specify the address that the server will listen to.')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((address, port))

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            mess_from_client = get_mess(client)
            print(mess_from_client)
            response = clients_massage_handler(mess_from_client)
            send_mess(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Invalid message received from client.')
            client.close()


if __name__ == '__main__':
    main()

