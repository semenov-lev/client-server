import unittest
from common.utils import encode_message, decode_data


class TestEncodeMessage(unittest.TestCase):
    def setUp(self):
        self.message = {
            "key1": "value",
            "ключ2": 123,
            "key3": {
                "key1": "значение",
                "люч2": 123,
            }
        }

    def test_bytes(self):
        result = encode_message(self.message)
        self.assertEqual(type(result), bytes)


class TestDecodeData(unittest.TestCase):
    def setUp(self):
        self.data = b'{"key1": "value",' \
                    b' "\\u043a\\u043b\\u044e\\u04472": 123,' \
                    b' "key3": {"key1": "\\u0437\\u043d\\u0430\\u0447\\u0435\\u043d\\u0438\\u0435",' \
                    b' "\\u043b\\u044e\\u04472": 123}}'

    def test_python_dict(self):
        result = decode_data(self.data)
        self.assertEqual(type(result), dict)

    def test_attribute_error(self):
        result = decode_data('йцукен')
        self.assertEqual(result,  {})

    def test_value_error(self):
        result = decode_data(b"{('a', 'b'): 'string'}")
        self.assertEqual(result,  {})


if __name__ == '__main__':
    unittest.main()
