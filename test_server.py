import unittest
from server import message_handler


class TestMessageHandler(unittest.TestCase):
    def setUp(self):
        self.message_200 = {
            "action": "presence",
            "time": 1650802194,
            "type": "status",
            "user": {
                "account_name": "test_account",
                "status": "Я здесь!"
            }
        }

        self.message_404 = {
            "action": "presence",
            "time": 1650802194,
            "type": "status",
            "user": {
                "account_name": "unknown_account",
                "status": "Я здесь!"
            }
        }

        self.message_400 = {
            "action": "sanction",
            "time": "Time For Lunch, Munch Munch",
            "type": "bad_request",
            "user": {}
        }

    def testresponse200(self):
        result = message_handler(self.message_200)
        self.assertEqual(result["response"], "200")

    def testresponse404(self):
        result = message_handler(self.message_404)
        self.assertEqual(result["response"], "404")

    def testresponse400(self):
        result = message_handler(self.message_400)
        self.assertEqual(result["response"], "400")


if __name__ == '__main__':
    unittest.main()
