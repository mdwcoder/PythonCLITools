import unittest
from unittest.mock import MagicMock, patch
from pyclit.run import run_uvicorn

class TestRun(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()
    
    @patch('pyclit.run.run_command')
    def test_run_uvicorn(self, mock_run):
        run_uvicorn("python_venv", "main:app", "0.0.0.0", 8000, self.logger)
        
        args, kwargs = mock_run.call_args
        cmd = args[0]
        
        self.assertEqual(cmd[0], "python_venv")
        self.assertIn("uvicorn", cmd)
        self.assertIn("main:app", cmd)
        self.assertIn("--host", cmd)
        self.assertIn("0.0.0.0", cmd)
        
if __name__ == '__main__':
    unittest.main()
