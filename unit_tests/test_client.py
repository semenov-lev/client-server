import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from client import presence_message
from common import variables


class TestPresenceMessage(unittest.TestCase):
    def setUp(self):
        self.message = presence_message()

    def test_action(self):
        self.assertEqual(self.message["action"], variables.PRESENCE)

    def test_account_name(self):
        self.assertEqual(self.message["user"]["account_name"], variables.ACCOUNT_NAME)


if __name__ == '__main__':
    unittest.main()
