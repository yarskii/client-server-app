import json

from lesson_3.common.variables import MAX_PACK_LENGTH, ENCODING


def get_mess(client):
    encoded_response = client.recv(MAX_PACK_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_mess(sock, message):
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)

