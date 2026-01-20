import sys
import shutil
from .util import run_command, is_tool

def check_health(venv_python, logger):
    """
    Audits the project.
    """
    # 1. Python version mismatch
    sys_ver = sys.version.split()[0]
    
    # Gets venv version
    try:
        res = run_command([venv_python, "--version"], logger, capture_output=True)
        venv_ver = res.stdout.strip().split()[-1]
    except:
        venv_ver = "Unknown"
        
    logger.info(f"System Python: {sys_ver}")
    logger.info(f"Venv Python:   {venv_ver}")
    
    if sys_ver != venv_ver:
        logger.warn("System and Venv python versions differ. This is fine if intended.")
        
    # 2. Audits
    logger.step("Checking vulnerabilities...")
    
    if is_tool("pip-audit"):
        run_command(["pip-audit"], logger, check=False)
    elif is_tool("safety"):
        run_command(["safety", "check"], logger, check=False)
    else:
        logger.warn("No audit tool (pip-audit/safety) found.")
        logger.info("Install one: pip install pip-audit")
