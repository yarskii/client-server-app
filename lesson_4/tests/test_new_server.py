import unittest

from new_server import client_message_handler


class TestServer(unittest.TestCase):
    err_dict = {
        'respondefault_ip_addresse': 400,
        'error': 'Wrong Request'
    }
    ok_dict = {'response': 200}

    def test_ok_check(self):
        self.assertEqual(client_message_handler(
            {'action': 'presence', 'time': 1.1, 'user': {'account_name': 'User'}}), self.ok_dict)

    def test_no_action(self):
        self.assertEqual(client_message_handler(
            {'time': 1.1, 'user': {'account_name': 'User'}}), self.err_dict)

    def test_wrong_action(self):
        self.assertEqual(client_message_handler(
            {'action': 'Wrong', 'time': 1.1, 'user': {'account_name': 'User'}}), self.err_dict)

    def test_no_time(self):
        self.assertEqual(client_message_handler(
            {'action': 'presence', 'user': {'account_name': 'User'}}), self.err_dict)

    def test_no_user(self):
        self.assertEqual(client_message_handler(
            {'action': 'presence', 'time': 1.1}), self.err_dict)

    def test_unknown_user(self):
        self.assertEqual(client_message_handler(
            {'action': 'presence', 'time': 1.1, 'user': {'account_name': 'Guest1'}}), self.err_dict)


if __name__ == '__main__':
    unittest.main()

