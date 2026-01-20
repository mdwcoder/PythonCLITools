import shutil
import subprocess
import sys
import shlex
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

# Custom theme for clarity
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "green",
    "step": "bold blue"
})

console = Console(theme=custom_theme)

class Logger:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def info(self, msg):
        console.print(f"[info]INFO:[/info] {msg}")

    def warn(self, msg):
        console.print(f"[warning]WARN:[/warning] {msg}")

    def error(self, msg):
        console.print(f"[error]ERROR:[/error] {msg}")

    def step(self, msg):
        console.print(f"[step]STEP:[/step] {msg}")
    
    def debug(self, msg):
        if self.verbose:
            console.print(f"[dim]DEBUG: {msg}[/dim]")

    def success(self, msg):
        console.print(f"[success]SUCCESS:[/success] {msg}")

def run_command(cmd, logger, dry_run=False, cwd=None, env=None, check=True, capture_output=False):
    """
    Executes a shell command.
    """
    cmd_str = " ".join(shlex.quote(str(part)) for part in cmd)
    if cwd:
         logger.info(f"Directory: {cwd}")
    
    if dry_run:
        logger.info(f"[DRY-RUN] Executing: {cmd_str}")
        return None

    logger.debug(f"Executing: {cmd_str}")
    
    try:
        # If capture_output is True, we return the CompletedProcess object to inspect stdout/stderr
        # If False, we let it print to stdout/stderr naturally (good for long running processes like uvicorn)
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            env=env, 
            check=check,
            # We only capture if explicitly requested (e.g. to parse output)
            text=True if capture_output else False, 
            capture_output=capture_output
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with return code {e.returncode}")
        logger.error(f"Command: {cmd_str}")
        if capture_output:
            logger.error(f"Stderr: {e.stderr}")
        raise e
    except FileNotFoundError:
        logger.error(f"Executable not found for command: {cmd[0]}")
        raise

def is_tool(name):
    """Check whether `name` is on PATH."""
    return shutil.which(name) is not None

def confirm(question, yes_flag=False, default=True):
    """
    Ask for confirmation.
    If yes_flag is True, returns True.
    If not TTY, returns default.
    Otherwise functionality asks user.
    """
    if yes_flag:
        return True
    
    if not sys.stdin.isatty():
        return default
    
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    prompt = " [Y/n] " if default else " [y/N] "
    
    while True:
        console.print(f"[bold yellow]{question}{prompt}[/bold yellow]", end="")
        choice = input().lower()
        if choice == "":
            return default
        if choice in valid:
            return valid[choice]
        console.print("Please respond with 'yes' or 'no' (or 'y'/'n').")

def write_file_safe(path, content, logger, dry_run=False, overwrite=False):
    """
    Writes content to path safely.
    """
    import os
    if os.path.exists(path) and not overwrite:
        logger.warn(f"File {path} already exists. Skipping.")
        return False
    
    logger.step(f"Writing file: {path}")
    if dry_run:
        return True
        
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.success(f"Created {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write {path}: {e}")
        return False
