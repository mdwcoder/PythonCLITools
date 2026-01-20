import unittest
from unittest.mock import MagicMock, patch
from pyclit.run import run_pytest

class TestPytestRunner(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()

    @patch('pyclit.run.run_command')
    def test_run_pytest_basic(self, mock_run):
        run_pytest("python_venv", [], self.logger)
        
        # Check command
        args, kwargs = mock_run.call_args
        cmd = args[0]
        
        self.assertEqual(cmd, ["python_venv", "-m", "pytest"])
        
    @patch('pyclit.run.run_command')
    def test_run_pytest_args(self, mock_run):
        run_pytest("python_venv", ["-v", "-k", "foo"], self.logger)
        
        args, kwargs = mock_run.call_args
        cmd = args[0]
        
        self.assertEqual(cmd, ["python_venv", "-m", "pytest", "-v", "-k", "foo"])
        
if __name__ == '__main__':
    unittest.main()
