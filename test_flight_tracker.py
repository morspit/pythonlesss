import unittest
from unittest.mock import patch, MagicMock
from flight_tracker import FlightTracker

class TestFlightTracker(unittest.TestCase):

    @patch('flight_tracker.requests.get')
    def test_fetch_flight_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><tr class="flight-row"><td class="flight-number">AA123</td><td class="status">On Time</td></tr></body></html>'
        mock_get.return_value = mock_response

        tracker = FlightTracker()
        html = tracker.fetch_flight_data('http://fakeurl.com')
        self.assertIn('AA123', html)
        self.assertIn('On Time', html)

    def test_extract_delay(self):
        tracker = FlightTracker()
        self.assertEqual(tracker.extract_delay("Delayed 15 minutes"), 15)
        self.assertEqual(tracker.extract_delay("On Time"), 0)

    @patch('flight_tracker.BeautifulSoup')
    def test_parse_flight_data(self, mock_bs):
        mock_bs.return_value.find_all.return_value = [
            MagicMock(find=lambda x, _: 'AA123' if x == 'td' else 'On Time')
        ]

        tracker = FlightTracker()
        flights = tracker.parse_flight_data('<html></html>', 'Example Airport')
        self.assertEqual(len(flights), 1)
        self.assertEqual(flights[0], ('AA123', 'On Time', 'Example Airport', 0))

    @patch('flight_tracker.sqlite3.connect')
    def test_save_to_database(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        tracker = FlightTracker()
        flights = [('AA123', 'On Time', 'Example Airport', 0)]
        tracker.save_to_database(flights)
        mock_conn.__enter__().execute.assert_called_once()

    @patch('pandas.read_sql_query')
    def test_export_to_csv(self, mock_read_sql):
        mock_df = MagicMock()
        mock_read_sql.return_value = mock_df
        mock_df.to_csv = MagicMock()

        tracker = FlightTracker()
        tracker.export_to_csv('Example Airport', 'output.csv')
        mock_df.to_csv.assert_called_once_with('output.csv', index=False)

if __name__ == '__main__':
    unittest.main()