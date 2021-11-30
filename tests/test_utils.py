import json
import unittest

from utils import send_msg, get_msg



class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode('utf-8')
        self.received_message = message_to_send

    def recv(self, max_len):
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode('utf-8')


class TestUtils(unittest.TestCase):
    test_dict_send = {
        'action': 'presence',
        'time': 111111.111111,
        'user': {
            'account_name': 'test_test'
        }
    }
    test_dict_recv_ok = {'response': 200}
    test_dict_recv_err = {
        'response': 400,
        'error': 'Wrong Request'
    }

    def test_send_msg(self):
        test_socket = TestSocket(self.test_dict_send)

        send_msg(test_socket, self.test_dict_send)

        self.assertEqual(test_socket.encoded_message, test_socket.received_message)

        self.assertRaises(TypeError, send_msg, test_socket)

    def test_get_msg(self):
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)
        self.assertEqual(get_msg(test_sock_ok), self.test_dict_recv_ok)
        self.assertEqual(get_msg(test_sock_err), self.test_dict_recv_err)


if __name__ == '__main__':
    unittest.main()


