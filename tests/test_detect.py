import os
import unittest
from unittest.mock import MagicMock
from pyclit.detect import detect_project_type, detect_entrypoint, TYPE_TOML, TYPE_REQ

class TestDetect(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()

    def test_detect_none(self):
        # Ensure no files exist
        if os.path.exists("pyproject.toml"): os.remove("pyproject.toml")
        if os.path.exists("requirements.txt"): os.remove("requirements.txt")
        self.assertIsNone(detect_project_type(self.logger))

    def test_detect_req(self):
        with open("requirements.txt", "w") as f: f.write("foo")
        try:
            self.assertEqual(detect_project_type(self.logger), TYPE_REQ)
        finally:
            os.remove("requirements.txt")

    def test_detect_toml(self):
        with open("pyproject.toml", "w") as f: f.write("")
        try:
            self.assertEqual(detect_project_type(self.logger), TYPE_TOML)
        finally:
            os.remove("pyproject.toml")
            
    def test_entrypoint_detection(self):
        os.makedirs("src/app", exist_ok=True)
        fname = "src/app/main.py"
        with open(fname, "w") as f:
            f.write("from fastapi import FastAPI\napp = FastAPI()")
        
        try:
            ep = detect_entrypoint(self.logger)
            self.assertEqual(ep, "src.app.main:app")
        finally:
            os.remove(fname)
            os.rmdir("src/app")
            os.rmdir("src")

if __name__ == '__main__':
    unittest.main()
