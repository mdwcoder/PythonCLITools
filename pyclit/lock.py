from .util import run_command, is_tool

def lock_dependencies(venv_python, logger, dry_run=False):
    """
    Locks dependencies.
    """
    if is_tool("pip-compile"):
        logger.step("Using pip-compile to generate requirements.lock...")
        run_command(["pip-compile", "--generate-hashes", "--output-file", "requirements.lock", "requirements.txt"], logger, dry_run=dry_run)
    else:
        logger.step("pip-tools not found. Falling back to pip freeze...")
        cmd = [venv_python, "-m", "pip", "freeze"]
        if not dry_run:
            res = run_command(cmd, logger, capture_output=True)
            with open("requirements.lock", "w") as f:
                f.write(res.stdout)
            logger.success("requirements.lock generated via pip freeze.")
