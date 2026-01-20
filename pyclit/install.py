import os
import shutil
from .util import run_command

def install_deps(mode, venv_python, logger, dry_run=False):
    """
    Installs dependencies based on mode.
    """
    if mode == "req":
        if not os.path.exists("requirements.txt"):
             logger.error("requirements.txt not found.")
             return
        
        logger.step("Installing from requirements.txt...")
        cmd = [venv_python, "-m", "pip", "install", "-r", "requirements.txt"]
        run_command(cmd, logger, dry_run=dry_run)
    
    elif mode == "toml":
        if not os.path.exists("pyproject.toml"):
            logger.error("pyproject.toml not found.")
            return

        # Strategy: poetry -> uv -> pip
        
        # 1. Poetry
        if (os.path.exists("poetry.lock") or "[tool.poetry]" in open("pyproject.toml").read()) and shutil.which("poetry"):
            logger.step("Detected Poetry project. Using 'poetry install'...")
            # Poetry manages its own venvs usually, but we want to use OUR .venv?
            # Poetry respects virtualenvs.create if local, or we can use `poetry install` if active.
            # But the user req says: "usa python del venv directamente" for execution.
            # For installation, `poetry install` works if we are 'inside' the venv or configured to use it.
            # Best way to force poetry to utilize the current venv is often just running it when VIRTUAL_ENV is set,
            # or trusting it finds .venv.
            # Let's set VIRTUAL_ENV env var for safety if we are creating it manually.
            env = os.environ.copy()
            # If we created .venv, we want poetry to use it.
            # Simplest for this script: standard 'pip install .' if poetry fails? 
            # No, user explicitly requested 'poetry install'.
            logger.info("Running poetry install...")
            run_command(["poetry", "install"], logger, dry_run=dry_run, env=env)
        
        # 2. UV
        elif (os.path.exists("uv.lock") or shutil.which("uv")):
             # Note: logic says "si detectas uv.lock o herramienta uv presente".
             # If uv is present but project is pure pip, uv is still a fast pip replacement.
             logger.step("Using uv for installation...")
             # uv sync usually creates .venv. We can point it to ours or let it handle it.
             # User said: "usar 'uv sync'".
             run_command(["uv", "sync"], logger, dry_run=dry_run)
        
        # 3. Fallback Pip
        else:
            logger.step("Fallback: Installing current package with pip...")
            cmd = [venv_python, "-m", "pip", "install", "."]
            run_command(cmd, logger, dry_run=dry_run)
