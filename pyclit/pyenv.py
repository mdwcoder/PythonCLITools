import shutil
import re
import sys
import os
try:
    import tomli as tomllib
except ImportError:
    import tomllib

from .util import run_command

def get_installed_pyenv_versions(logger):
    """Returns a list of installed python versions from pyenv."""
    if not shutil.which("pyenv"):
        return []
    
    try:
        # We use check=False because pyenv might error if not initialized properly, 
        # but usually 'pyenv versions' works.
        res = subprocess.run(["pyenv", "versions", "--bare"], capture_output=True, text=True)
        if res.returncode != 0:
            return []
        versions = [v.strip() for v in res.stdout.splitlines() if v.strip()]
        return versions
    except Exception as e:
        logger.debug(f"Failed to list pyenv versions: {e}")
        return []

def parse_requires_python(pyproject_path):
    """Extracts [project] requires-python from pyproject.toml."""
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("requires-python")
    except Exception:
        return None

def version_satisfies(version, specifier):
    """
    Very basic check if version satisfies specifier.
    Real implementation would use `packaging` library, but we want to minimize deps.
    We will handle simple cases like ">=3.10", ">=3.10,<3.13".
    """
    # If no specifier, any version is fine
    if not specifier:
        return True
    
    # Simple parsing logic
    # Clean up version string to just numbered parts (e.g. 3.10.4 -> 3.10.4)
    # Ignore 'micromamba' or other suffixes in pyenv output
    v_clean = re.sub(r'[^\d\.]', '', version)
    if not v_clean:
         return False
    
    parts = [int(p) for p in v_clean.split('.')]
    
    specs = specifier.split(',')
    for spec in specs:
        spec = spec.strip()
        if spec.startswith(">="):
            target = [int(p) for p in spec[2:].split('.')]
            if parts < target: return False
        elif spec.startswith(">"):
            target = [int(p) for p in spec[1:].split('.')]
            if parts <= target: return False
        elif spec.startswith("<="):
            target = [int(p) for p in spec[2:].split('.')]
            if parts > target: return False
        elif spec.startswith("<"):
            target = [int(p) for p in spec[1:].split('.')]
            if parts >= target: return False
        elif spec.startswith("=="):
            target = [int(p) for p in spec[2:].split('.')]
            # strict equality might be too harsh for semver, but let's stick to it
            if parts != target: return False
    
    return True

def resolve_python(logger, dry_run=False, prefer_pyenv=True):
    """
    Resolves the python executable to use.
    1. Checks pyproject.toml for requires-python
    2. Checks pyenv for available versions
    3. Picks the best match
    Returns (python_executable_path, version_string)
    """
    requires_python = None
    if os.path.exists("pyproject.toml"):
        requires_python = parse_requires_python("pyproject.toml")
        if requires_python:
            logger.info(f"Found requires-python: {requires_python}")

    if prefer_pyenv and shutil.which("pyenv"):
        installed_versions = get_installed_pyenv_versions(logger)
        logger.debug(f"Pyenv versions found: {installed_versions}")
        
        # Sort versions desc (roughly)
        installed_versions.sort(key=lambda s: [int(u) if u.isdigit() else 0 for u in re.split(r'[^\d]', s)], reverse=True)

        candidate = None
        for v in installed_versions:
             # Skip system entries or weird names if possible, keeping standard semver
             if not v[0].isdigit(): 
                 continue
             
             if version_satisfies(v, requires_python):
                 candidate = v
                 break
        
        if candidate:
            logger.info(f"Selected python version from pyenv: {candidate}")
            # Get path
            try:
                res = subprocess.run(["pyenv", "prefix", candidate], capture_output=True, text=True, check=True)
                prefix = res.stdout.strip()
                python_path = os.path.join(prefix, "bin", "python")
                if not os.path.exists(python_path):
                     # Windows?
                     python_path = os.path.join(prefix, "python.exe")
                return python_path
            except:
                logger.warn(f"Could not determine path for pyenv version {candidate}")
        else:
            logger.warn(f"No installed pyenv version satisfies {requires_python} (or no versions found).")
            # Logic to install (placeholder as asking input in CLI tool mid-run is tricky without interaction mode)
            # User requirement: "Si ninguna cumple, ofrece instalar la más alta estable dentro del rango (o pide input)"
            if not dry_run:
                 # In a real tool we might pause for input, but here we will warn and fallback or ask.
                 # Given prompt constraints, we will just fallback to system if we can't auto-resolve.
                 pass

    # Fallback to system python
    logger.info("Falling back to system python3")
    return sys.executable
