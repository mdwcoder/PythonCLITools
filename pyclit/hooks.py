import os
import shutil
from .util import run_command, confirm, write_file_safe, is_tool

def install_hooks(venv_python, logger, dry_run=False, style_mode="ruff"):
    """
    Installs and configures pre-commit.
    """
    # 1. Check if pre-commit installed
    # Try running it
    has_precommit = is_tool("pre-commit")
    if not has_precommit:
        # Check venv
        if not dry_run:
            logger.step("pre-commit not found. Installing in venv...")
            run_command([venv_python, "-m", "pip", "install", "pre-commit"], logger, check=False)
            # Recheck? Or just assume it works via `venv_python -m pre_commit`
            has_precommit = True # We effectively have it now
    
    # 2. Config generation
    config_path = ".pre-commit-config.yaml"
    if not os.path.exists(config_path):
        logger.step("Generating .pre-commit-config.yaml...")
        
        # Decide hooks
        # Base
        content = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
"""
        # Formatter
        # If ruff detected or default
        if style_mode == "ruff":
            content += """
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.280
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format
"""
        else:
            # Black + Isort
            content += """
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
"""
        # Pytest?
        # Detect pytest in requirements or toml
        has_pytest = False
        try:
            if os.path.exists("requirements.txt") and "pytest" in open("requirements.txt").read(): has_pytest = True
            if os.path.exists("pyproject.toml") and "pytest" in open("pyproject.toml").read(): has_pytest = True
        except: pass
        
        if has_pytest:
             content += """
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
"""
        write_file_safe(config_path, content, logger, dry_run)
    else:
        logger.info(".pre-commit-config.yaml already exists.")

    # 3. Install hooks
    logger.step("Installing git hooks...")
    # Use venv module if system version absent
    cmd = ["pre-commit", "install"]
    if not is_tool("pre-commit"):
        cmd = [venv_python, "-m", "pre_commit", "install"]
    
    run_command(cmd, logger, dry_run=dry_run, check=False)
    
    # 4. Run all files?
    if confirm("Run pre-commit on all files now?", default=False):
        logger.step("Running pre-commit run --all-files...")
        if not is_tool("pre-commit"):
            cmd = [venv_python, "-m", "pre_commit", "run", "--all-files"]
        else:
             cmd = ["pre-commit", "run", "--all-files"]
        run_command(cmd, logger, dry_run=dry_run, check=False)
