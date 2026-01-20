import os
import re

TYPE_TOML = "toml"
TYPE_REQ = "req"

def detect_project_type(logger, explicit_req=False, explicit_toml=False):
    """
    Detects project type based on files or flags.
    Returns TYPE_TOML, TYPE_REQ, or None.
    """
    has_toml = os.path.exists("pyproject.toml")
    has_req = os.path.exists("requirements.txt")

    if explicit_toml:
        if has_toml: return TYPE_TOML
        logger.warn("Flag -toml passed but pyproject.toml not found.")
        return None # Or error? User said "respeta esas", implies try or fail. 
                    # If file missing, likely fail logic in install step.
                    # returning detected type helps caller decide.
        return TYPE_TOML
    
    if explicit_req:
        if has_req: return TYPE_REQ
        logger.warn("Flag -req passed but requirements.txt not found.")
        return TYPE_REQ

    # Auto detection
    if has_toml:
        return TYPE_TOML
    elif has_req:
        return TYPE_REQ
    
    return None

def detect_entrypoint(logger):
    """
    Heuristics to find FastAPI entrypoint.
    Searches for 'app = FastAPI(' in common files.
    """
    candidate_files = [
        "main.py", "app.py", 
        "src/main.py", "src/app/main.py", 
        "app/main.py"
    ]
    
    pattern = re.compile(r'app\s*=\s*FastAPI\(')

    for fname in candidate_files:
        if os.path.exists(fname):
            try:
                with open(fname, "r", encoding="utf-8") as f:
                    content = f.read()
                    if pattern.search(content):
                        # Convert path to module syntax
                        # e.g. src/main.py -> src.main:app
                        module_path = fname.replace("/", ".").replace("\\", ".").replace(".py", "")
                        logger.info(f"Detected potential entrypoint in {fname}")
                        return f"{module_path}:app"
            except Exception:
                pass
    
    return None
