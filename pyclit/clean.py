import os
import shutil
from .util import run_command, confirm
from .venv import create_venv
from .install import install_deps
from .detect import detect_project_type

def nuke_path(path, logger, dry_run=False):
    if os.path.exists(path):
        logger.step(f"Removing {path}...")
        if not dry_run:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

def clean_project(logger, venv_path=".venv", dry_run=False, rebuild_venv=False, yes_flag=False):
    """
    Cleans caches and artifacts. Optional venv rebuild.
    """
    targets = [
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "dist",
        "build",
    ]
    
    # Recursive walk for __pycache__ and .pyc
    # We'll just walk safely
    if dry_run:
        logger.info("[DRY-RUN] Scanning for targets to clean...")

    files_to_clean = []
    dirs_to_clean = []

    # root level folders
    for t in targets:
        if os.path.exists(t):
            dirs_to_clean.append(t)
            
    # Egg info
    for f in os.listdir("."):
        if f.endswith(".egg-info"):
            dirs_to_clean.append(f)

    # Walk for pyc/pycache
    for root, dirs, files in os.walk("."):
        if ".venv" in root: continue # Skip venv
        
        if "__pycache__" in dirs:
            dirs_to_clean.append(os.path.join(root, "__pycache__"))
        
        for f in files:
            if f.endswith(".pyc"):
                files_to_clean.append(os.path.join(root, f))
    
    # Execute clean
    if not files_to_clean and not dirs_to_clean:
        logger.info("Nothing to clean.")
    else:
        for d in dirs_to_clean:
            nuke_path(d, logger, dry_run)
        for f in files_to_clean:
            nuke_path(f, logger, dry_run)
            
    # Rebuild Venv
    if rebuild_venv:
        # Check confirmation
        # Instruction: "Si --rebuild-venv, pide confirmación si hay TTY salvo que el usuario pase --yes"
        if confirm(f"Are you sure you want to delete and rebuild {venv_path}?", yes_flag, default=False):
            nuke_path(venv_path, logger, dry_run)
            
            if not dry_run:
                # Re-create logic
                # We need base python... detecting logic duplication from main?
                # We'll just use sys.executable for now or assume user handles it. 
                # But to be helpful, let's try to detect.
                # Since we don't have easy access to `resolve_python` arguments here easily without coupling,
                # we will assume `sys.executable` or simple reconstruction.
                # Ideally `cli.py` handles the reconstruction call, but `clean_project` is the handler.
                # Let's import resolution logic.
                from .pyenv import resolve_python
                import sys
                
                # Resolve
                logger.step("Rebuilding venv...")
                base = resolve_python(logger, dry_run=False) # Use defaults
                new_python = create_venv(base, logger, venv_dir=venv_path, dry_run=False)
                
                # Reinstall
                mode = detect_project_type(logger)
                if mode:
                    install_deps(mode, new_python, logger, dry_run=False)
                
                logger.success("Venv rebuilt.")
        else:
            logger.warn("Skipping venv rebuild (cancelled).")
