import os
import sys
from .util import run_command

def get_venv_python(venv_dir=".venv"):
    """
    Returns the path to the python executable inside the venv.
    Handles Windows/Unix differences.
    """
    if sys.platform == "win32":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python")

def create_venv(base_python, logger, venv_dir=".venv", dry_run=False):
    """
    Creates a virtual environment using the specified base python.
    REUSES existing venv if present, but logs it.
    """
    if os.path.exists(venv_dir):
        logger.info(f"Virtual environment already exists at {venv_dir}. Reusing.")
        return get_venv_python(venv_dir)
    
    logger.step(f"Creating virtual environment at {venv_dir} using {base_python}...")
    
    cmd = [base_python, "-m", "venv", venv_dir]
    run_command(cmd, logger, dry_run=dry_run)
    
    return get_venv_python(venv_dir)
