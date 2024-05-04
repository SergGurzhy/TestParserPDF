import unittest
from helpers.helpers import determine_value_type


class TestDateDetect(unittest.TestCase):

    def test_1(self):
        self.assertEqual({'type': 'date', 'pattern': '%d.%m.%Y'}, determine_value_type('25.12.2023'))

    def test_2(self):
        self.assertEqual({'type': 'number', 'pattern': r"^\d+$"}, determine_value_type('111'))

    def test_3(self):
        self.assertEqual({'type': 'string', 'pattern': r'^[A-Z0-9]+$'}, determine_value_type('P101'))

    def test_4(self):
        self.assertEqual({'type': 'string', 'pattern': r'^[a-z0-9]+$'}, determine_value_type('kj101ol'))

    def test_5(self):
        self.assertEqual({'type': 'string', 'pattern': r'^[a-zA-Z0-9]+$'}, determine_value_type('PM101ol'))

    def test_6(self):
        self.assertEqual({'type': 'string', 'pattern': ''}, determine_value_type('PM1-01ol'))

    def test_7(self):
        self.assertEqual({'type': 'string', 'pattern': r'^[A-Z ]+$'}, determine_value_type('SERVICES LLC'))


if __name__ == '__main__':
    unittest.main()
