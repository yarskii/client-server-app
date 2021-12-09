import json
from decorators import log


@log
def get_msg(client):
    encoded_response = client.recv(1024)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode('utf-8')
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


@log
def send_msg(sock, message):
    js_message = json.dumps(message)
    encoded_message = js_message.encode('utf-8')
    sock.send(encoded_message)

