import os
import sys
from .util import run_command, confirm, is_tool, write_file_safe

def get_style_command(logger):
    """
    Determines the style command to use.
    If ruff is installed/available, prefer it.
    Else black + isort.
    """
    # Check if tools exist in current venv or PATH?
    # We should look in venv first theoretically, but is_tool looks in PATH.
    # The caller manages venv PATH injection usually.
    
    has_ruff = is_tool("ruff")
    has_black = is_tool("black")
    has_isort = is_tool("isort")
    
    if has_ruff:
        return "ruff"
    if has_black:
        return "black"
    return None

def ensure_style_config(logger, dry_run=False, yes_flag=False):
    """
    Checks for style config. If missing, offers to create it.
    """
    # Check for pyproject.toml sections or config files
    has_config = False
    
    common_configs = [
        "pyproject.toml", "ruff.toml", ".ruff.toml", 
        ".black", "black.toml"
    ]
    
    # We check if these files exist AND have relevant sections?
    # Simplest check: if project has configuration file.
    # But pyproject.toml almost always exists now.
    # Check content of pyproject.toml for [tool.ruff] or [tool.black]
    
    if os.path.exists("pyproject.toml"):
        try:
            with open("pyproject.toml", "r") as f:
                content = f.read()
                if "[tool.ruff]" in content or "[tool.black]" in content or "[tool.isort]" in content:
                    has_config = True
        except:
            pass
            
    if not has_config:
        for f in common_configs:
            if f != "pyproject.toml" and os.path.exists(f):
                has_config = True
                break
    
    if has_config:
        logger.info("Style configuration detected.")
        return

    # Offer to create
    msg = "No style config detected. Create recommended configuration (Ruff/Black)?"
    # If no TTY, default is Create (per instructions)
    if confirm(msg, yes_flag=yes_flag, default=True):
        # Create pyproject.toml snippet or append?
        # If pyproject.toml exists, append. Else create.
        
        ruff_config = """
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
ignore = []

[tool.isort]
profile = "black"

[tool.black]
line-length = 88
target-version = ['py310']
"""
        target = "pyproject.toml"
        mode = "a" if os.path.exists(target) else "w"
        
        logger.step(f"Adding style config to {target}...")
        
        if not dry_run:
            try:
                with open(target, mode, encoding="utf-8") as f:
                    if mode == "a": f.write("\n")
                    f.write(ruff_config)
                logger.success("Configuration added.")
            except Exception as e:
                logger.error(f"Failed to write config: {e}")
        else:
            logger.info(f"[DRY-RUN] Would append config to {target}")

def run_style(venv_python, logger, dry_run=False, yes_flag=False):
    """
    Runs formatting tools.
    """
    ensure_style_config(logger, dry_run, yes_flag)
    
    # Determine tools available in VENV or PATH
    # We need to execute inside VENV context ideally.
    # But tools might be global (e.g. pipx).
    # We try to run them via venv_python -m <tool> first?
    # Or just assumes they are in PATH (maybe venv activated or passed).
    
    # Let's try to detect if we can run `ruff` directly.
    # Helper to run tool
    def run_tool(name, args):
        cmd = [name] + args
        try:
            run_command(cmd, logger, dry_run=dry_run, check=False)
        except FileNotFoundError:
            logger.warn(f"{name} not found. Install it with 'pip install {name}' or similar.")

    # Strategy: Ruff first
    # But wait, we should check if they are installed in the venv?
    # If we are using venv_python, we can try `venv_python -m ruff`.
    
    # Let's try running via module first, fallback to CLI command.
    
    # Is Ruff available?
    # We can check by running `venv_python -m ruff --version` silently?
    
    use_ruff = False
    try:
        # Check if ruff is importable/runnable
        subprocess.run([venv_python, "-m", "ruff", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        use_ruff = True
    except:
        # Fallback to system ruff?
        if is_tool("ruff"):
            use_ruff = True
            # But if system ruff, we just call "ruff"
    
    # Logic to run commands
    # If use_ruff: `ruff format .` AND `ruff check --fix .`
    if use_ruff:
        logger.step("Running Ruff format...")
        # Try module way first if possible to use venv version
        cmd_base = [venv_python, "-m", "ruff"]
        try:
            run_command(cmd_base + ["format", "."], logger, dry_run=dry_run, check=False)
            logger.step("Running Ruff check --fix...")
            run_command(cmd_base + ["check", "--fix", "."], logger, dry_run=dry_run, check=False)
            return
        except FileNotFoundError:
            # Fallback to global
            run_command(["ruff", "format", "."], logger, dry_run=dry_run, check=False)
            run_command(["ruff", "check", "--fix", "."], logger, dry_run=dry_run, check=False)
            return

    # Fallback to Black + Isort
    logger.step("Ruff not found. Trying Black + Isort...")
    
    run_command([venv_python, "-m", "black", "."], logger, dry_run=dry_run, check=False)
    run_command([venv_python, "-m", "isort", "."], logger, dry_run=dry_run, check=False)
