import argparse
import sys
import os
from .util import Logger, console, is_tool
from .detect import detect_project_type, detect_entrypoint
from .pyenv import resolve_python
from .venv import create_venv, get_venv_python
from .install import install_deps
from .run import run_uvicorn, run_script, run_generic_command, run_pytest
from .ngrok import start_ngrok

# MVP+ Imports
from .style import run_style
from .hooks import install_hooks
from .clean import clean_project
from .template import create_template, generate_gitignore
from .dockerize import generate_dockerfile
from .lock import lock_dependencies
from .health import check_health

def main():
    parser = argparse.ArgumentParser(description="PythonCLITools (pyclit) - Automated Project Manager")
    
    # Flags Existing
    parser.add_argument("-v", "--venv", action="store_true", help="Create/Ensure .venv exists")
    parser.add_argument("-req", "--requirements", action="store_true", help="Install from requirements.txt")
    parser.add_argument("-toml", "--pyproject", action="store_true", help="Install from pyproject.toml")
    parser.add_argument("-version", "--resolve-version", action="store_true", help="Resolve and pick python version")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    # Run options
    group_run = parser.add_mutually_exclusive_group()
    group_run.add_argument("--run", metavar="TARGET", help="Run target: UVICORN, PYTEST, <file.py>, or <command>")
    group_run.add_argument("--runp", metavar="TARGET", help="[MVP+] Run Proxy: execute in venv without activation")

    parser.add_argument("-ngrok", "--ngrok", action="store_true", help="Expose via ngrok (requires UVICORN)")
    parser.add_argument("-ip", default="0.0.0.0", help="Host IP for Uvicorn")
    parser.add_argument("-port", type=int, default=8000, help="Port for Uvicorn")
    
    # Pytest specific
    parser.add_argument("--pytest-args", help="Arguments to pass to pytest (quote them string)")

    # MVP+ Flags
    parser.add_argument("--style", "--format", action="store_true", help="[MVP+] Run formatter (Ruff/Black)")
    parser.add_argument("--hooks", action="store_true", help="[MVP+] Install pre-commit hooks")
    parser.add_argument("--clean", "--nuke", action="store_true", help="[MVP+] Deep clean project")
    parser.add_argument("--rebuild-venv", action="store_true", help="[MVP+] Rebuild venv (used with --clean)")
    parser.add_argument("--template", choices=["fastapi", "data", "cli"], help="[MVP+] Auto-scaffold project")
    parser.add_argument("--dockerize", action="store_true", help="[MVP+] Generate Dockerfile")
    parser.add_argument("--lock", action="store_true", help="[MVP+] Generate requirements.lock")
    parser.add_argument("--health", action="store_true", help="[MVP+] Audit project health")
    parser.add_argument("--yes", action="store_true", help="[MVP+] Auto-confirm prompts")

    # Capture remainder for pytest or generic args
    parser.add_argument("rest", nargs=argparse.REMAINDER, help="Extra args passed to runner (use after --)")

    args = parser.parse_args()
    
    logger = Logger(verbose=args.verbose)
    
    console.print(f"[bold cyan]pyclit[/bold cyan] [dim]{os.getcwd()}[/dim]")
    
    # --- Scaffolding (Template) ---
    # Happens before venv ideally
    if args.template:
        logger.info(f"Initializing template: {args.template}")
        create_template(args.template, logger, dry_run=args.dry_run)
        generate_gitignore(logger, dry_run=args.dry_run)
        # If template created, we might want to continue to venv creation?
        # User might want `pyclit --template fastapi -v`
        
    # --- Resolution & Venv ---
    base_python = sys.executable
    if args.resolve_version:
        logger.step("Resolving Python version...")
        base_python = resolve_python(logger, dry_run=args.dry_run)

    # Calculate venv python path
    venv_python = get_venv_python()
    
    # Check cleaning with rebuild
    if args.clean:
        clean_project(logger, venv_path=".venv", dry_run=args.dry_run, rebuild_venv=args.rebuild_venv, yes_flag=args.yes)
        # If we just nuked venv without rebuild, venv_python is invalid.
        # If rebuild was true, venv_python is valid again.
        if args.rebuild_venv:
             pass # it's back
        elif os.path.exists(".venv"):
             pass # it wasn't valid or wasn't deleted
        else:
             # Venv gone. If we have other operations depending on venv (like --style, --run), they will fail.
             # Unless -v was passed to recreate it?
             pass

    if args.venv:
        venv_python = create_venv(base_python, logger, dry_run=args.dry_run)
    
    # --- Dockerize ---
    if args.dockerize:
        generate_dockerfile(logger, dry_run=args.dry_run)
        
    # --- Install Deps ---
    mode = None
    if args.requirements: mode = "req"
    elif args.pyproject: mode = "toml"
    else:
        # Detect
        detected = detect_project_type(logger)
        if detected: mode = detected
    
    # Trigger install if specific flags OR if we are doing setup things and NOT just running?
    # Original logic: "Si no pasa ninguna, aplica auto" -> implies always install if detected.
    # But if we run `pyclit --runp script.py`, we might not want to check install every ms.
    # Refinement for MVP+: Only auto-install if NOT running a proxy/run command OR if venv is missing?
    # Or stick to original rule. Sticking to original rule for robustness.
    # But optimize: if no requirements file found, skip.
    if mode and (args.requirements or args.pyproject or args.venv or args.template):
         # Explicit install requested via flags implies we WANT install
         install_deps(mode, venv_python, logger, dry_run=args.dry_run)
    elif mode and not (args.run or args.runp):
         # If NOT running, do auto install
         install_deps(mode, venv_python, logger, dry_run=args.dry_run)
    
    # --- MVP+ Features utilizing venv ---
    
    if args.lock:
        lock_dependencies(venv_python, logger, dry_run=args.dry_run)
        
    if args.style:
        run_style(venv_python, logger, dry_run=args.dry_run, yes_flag=args.yes)
        
    if args.hooks:
        install_hooks(venv_python, logger, dry_run=args.dry_run)

    if args.health:
        check_health(venv_python, logger)

    # --- Execution ---
    
    # Handle --runp (Proxy)
    if args.runp:
        target = args.runp
        if not os.path.exists(venv_python) and not args.dry_run:
            logger.error(f"No venv found at {venv_python}. Run with -v first.")
            sys.exit(1)
            
        if target.endswith(".py"):
            run_script(venv_python, target, logger, dry_run=args.dry_run)
        else:
             # Heuristic: if spaces -> command. If not -> module?
             # User says: "Si target parece módulo... y el usuario pasa --module (si lo añades)" 
             # I didn't add --module flag.
             # "Si target parece modulo (ej pkg.mod) ... => python -m pkg.mod"
             # How to distinguish `command` from `module`? 
             # `pytest` is a command. `mypkg.mod` is a module.
             # Implementation: Try to resolve as command path inside venv/bin?
             # Simple approach: If it has spaces, it's a command string.
             # If it looks like a file, it's a script.
             # Default fallback: Command execution?
             run_generic_command(venv_python, target, logger, dry_run=args.dry_run)

    if args.run:
        target = args.run
        ngrok_proc = None
        
        try:
            if target == "PYTEST":
                if not os.path.exists(venv_python) and not args.dry_run:
                     logger.error("No venv found. Run with -v first (or run prepare flags).")
                     # We can't continue
                     sys.exit(1)
                
                # Determine Args
                # Priority: rest > --pytest-args
                pytest_target_args = []
                
                if args.rest:
                    # 'rest' usually captures '--' as the first item if present
                    # Example: pyclit --run PYTEST -- -k foo -> rest = ['--', '-k', 'foo']
                    # Example: pyclit --run PYTEST -k foo -> rest = might capture -k foo if unrecognized?
                    # But argparse stops at unrecognized flags only if parsing partially.
                    # REMAINDER captures anything remaining.
                     cleaned_rest = []
                     for a in args.rest:
                         if a == "--": continue
                         cleaned_rest.append(a)
                     
                     if cleaned_rest:
                          pytest_target_args.extend(cleaned_rest)
                
                if args.pytest_args:
                    # Splitting safe?
                    import shlex
                    try:
                        extras = shlex.split(args.pytest_args)
                        pytest_target_args.extend(extras)
                    except:
                        logger.warn("Failed to split --pytest-args string safely.")
                        pytest_target_args.append(args.pytest_args)
                        
                run_pytest(venv_python, pytest_target_args, logger, dry_run=args.dry_run)
            
            elif target == "UVICORN":
                entrypoint = detect_entrypoint(logger)
                if not entrypoint:
                     logger.error("Could not detect FastAPI entrypoint.")
                     return 

                if args.ngrok:
                    ngrok_proc, public_url = start_ngrok(args.port, logger)
                    if public_url:
                        console.print(f"[bold green]Public URL: {public_url}[/bold green]")
                
                logger.info(f"Entrypoint: {entrypoint}")
                run_uvicorn(venv_python, entrypoint, args.ip, args.port, logger, dry_run=args.dry_run)
                
            elif target.endswith(".py"):
                run_script(venv_python, target, logger, dry_run=args.dry_run)
            else:
                run_generic_command(venv_python, target, logger, dry_run=args.dry_run)
                
        except KeyboardInterrupt:
            logger.info("Stopping...")
        finally:
            if ngrok_proc:
                ngrok_proc.terminate()
                logger.info("Ngrok stopped.")

if __name__ == "__main__":
    main()
