import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Append src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import workkeylogger

class TestWorkKeylogger(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='{"email":"test@example.com", "password":"password123"}')
    @patch('os.path.exists', return_value=True)
    def test_load_credentials(self, mock_exists, mock_file):
        email, password = workkeylogger.load_credentials('config.json')
        self.assertEqual(email, "test@example.com")
        self.assertEqual(password, "password123")

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('os.path.exists', return_value=False)
    def test_load_credentials_file_not_found(self, mock_exists, mock_file):
        email, password = workkeylogger.load_credentials('config.json')
        self.assertIsNone(email)
        self.assertIsNone(password)

    def test_process_key_strike_char(self):
        workkeylogger.content = ""
        mock_key = MagicMock()
        mock_key.char = "a"
        workkeylogger.process_key_strike(mock_key)
        self.assertEqual(workkeylogger.content, "a")

if __name__ == '__main__':
    try:
        unittest.main()
    except Exception as e:
        print(f"Test execution failed: {e}")
        sys.exit(1)
