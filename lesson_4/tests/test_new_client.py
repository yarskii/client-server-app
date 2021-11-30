import unittest

from new_client import new_presence, answer


class TestClass(unittest.TestCase):

    def test_new_presence(self):
        test = new_presence()
        test['time'] = 1.1
        self.assertEqual(test, {'action': 'presence', 'time': 1.1, 'user': {'account_name': 'User'}})

    def test_200_ans(self):
        self.assertEqual(answer({'response': 200}), 'Code 200: OK')

    def test_400_ans(self):
        self.assertEqual(answer({'response': 400, "error": 'Wrong Request'}), 'Code 400: Wrong Request')

    def test_no_response(self):
        self.assertRaises(ValueError, answer, {'error': 'Wrong Request'})


if __name__ == '__main__':
    unittest.main()
