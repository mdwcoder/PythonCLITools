import unittest
import os
import shutil
from unittest.mock import MagicMock, patch
from pyclit.template import create_template, generate_gitignore
from pyclit.dockerize import generate_dockerfile
from pyclit.clean import clean_project

class TestMVPFeatures(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()
        self.test_dir = "test_env_mvp"
        os.makedirs(self.test_dir, exist_ok=True)
        self.cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.test_dir)

    def test_template_fastapi(self):
        create_template("fastapi", self.logger)
        self.assertTrue(os.path.exists("app/main.py"))
        self.assertTrue(os.path.exists("requirements.txt"))
        with open("requirements.txt") as f:
            self.assertIn("fastapi", f.read())

    def test_gitignore_creation(self):
        generate_gitignore(self.logger)
        self.assertTrue(os.path.exists(".gitignore"))
        with open(".gitignore") as f:
            self.assertIn(".venv", f.read())

    def test_dockerfile_smoke(self):
        with open("requirements.txt", "w") as f: f.write("flask")
        generate_dockerfile(self.logger)
        self.assertTrue(os.path.exists("Dockerfile"))
        with open("Dockerfile") as f:
            content = f.read()
            self.assertIn("FROM python", content)
            self.assertIn("pip install", content)

    @patch('pyclit.clean.confirm')
    def test_clean_dry_run(self, mock_confirm):
        mock_confirm.return_value = True
        os.makedirs("__pycache__", exist_ok=True)
        clean_project(self.logger, dry_run=True, rebuild_venv=False)
        # Should still exist because dry run
        self.assertTrue(os.path.exists("__pycache__"))

if __name__ == '__main__':
    unittest.main()
