import unittest

from data_finder import extract_data, get_project_root


class CompareTickets(unittest.TestCase):
    root = get_project_root()
    etalon = extract_data(f'{root}/test_task.pdf')
    ticket = extract_data(f'{root}/test_task_1.pdf')

    def test_self(self):
        self.assertEqual(self.etalon, self.etalon)

    def test_sheet_size(self):
        self.assertEqual(
            self.etalon.get('meta_data').get('sheet_size'),
            self.ticket.get('meta_data').get('sheet_size')
        )

    def test_all_positions_on_sheet(self):
        etalon_key = set(self.etalon.get('body').keys())
        ticket_key = set(self.ticket.get('body').keys())

        self.assertEqual(len(etalon_key ^ ticket_key), 0)


if __name__ == '__main__':
    unittest.main()
