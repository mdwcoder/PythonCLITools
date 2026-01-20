from .util import run_command

def run_uvicorn(venv_python, entrypoint, host, port, logger, dry_run=False):
    """
    Runs uvicorn using the venv python.
    """
    # We install uvicorn if missing? Or assume it's in venv?
    # Usually part of deps. If not, it will fail.
    
    logger.step(f"Running Uvicorn: {entrypoint} on {host}:{port}")
    
    cmd = [
        venv_python, "-m", "uvicorn", 
        entrypoint, 
        "--host", host, 
        "--port", str(port)
    ]
    
    # This is a blocking call usually
    run_command(cmd, logger, dry_run=dry_run, check=False)

def run_script(venv_python, script_path, logger, dry_run=False):
    """
    Runs a python script using venv python.
    """
    logger.step(f"Running script: {script_path}")
    cmd = [venv_python, script_path]
    run_command(cmd, logger, dry_run=dry_run, check=False)

def run_generic_command(venv_python, command_str, logger, dry_run=False):
    """
    Runs a generic command string.
    """
    logger.step(f"Running command: {command_str}")
    # We might need to split command_str or run with shell=True if complex.
    # But user asked to use venv environment.
    # We can try to prepend venv/bin to PATH in env?
    # Or replace 'python' with venv_python?
    
    import os
    import shlex
    
    env = os.environ.copy()
    # Add venv bin to path
    venv_bin = os.path.dirname(venv_python)
    env["PATH"] = f"{venv_bin}{os.pathsep}{env.get('PATH', '')}"
    
    # If standard execution
    args = shlex.split(command_str)
    
    # Execute
    run_command(args, logger, dry_run=dry_run, env=env, check=False)

def run_pytest(venv_python, pytest_args, logger, dry_run=False):
    """
    Runs pytest using the venv python.
    """
    logger.step("Runner: PYTEST")
    logger.info(f"Python: {venv_python}")
    
    cmd = [venv_python, "-m", "pytest"] + pytest_args
    
    # Log the args clearly
    if pytest_args:
        logger.info(f"Pytest Args: {' '.join(pytest_args)}")
    else:
        logger.info("Pytest Args: (none)")
        
    run_command(cmd, logger, dry_run=dry_run, check=False)
