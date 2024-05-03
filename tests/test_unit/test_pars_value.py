import unittest
from data_finder import get_key_value


class ParseValue(unittest.TestCase):

    def test_1(self):
        string = "DESCRIPTION: PART"
        expected = ('DESCRIPTION', "PART", ':')
        self.assertEqual(expected, get_key_value(string))

    def test_2(self):
        string = "DESCRIPTION PART"
        expected = ('DESCRIPTION PART', "", '')
        self.assertEqual(expected, get_key_value(string))

    def test_3(self):
        string = "DESCRIPTION: PART: 123"
        expected = ('DESCRIPTION', "PART: 123", ':')
        self.assertEqual(expected, get_key_value(string))

    def test_4(self):
        string = "GRIFFON AVIATION SERVICES LLC"
        expected = ('GRIFFON AVIATION SERVICES LLC', "", '')
        self.assertEqual(expected, get_key_value(string))


if __name__ == '__main__':
    unittest.main()
