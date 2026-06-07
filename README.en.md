[Español](README.es.md) | [English](README.en.md)

---

# PythonCLITools (`pyclit`)

> Automate your Python project lifecycle: scaffolding, dependencies, virtual environments, execution, and deployment preparation.

- **Automated setup**: Detects `pyproject.toml` or `requirements.txt` and manages `.venv` automatically.
- **Smart Execution**: Runs servers (Uvicorn), scripts, and tests inside the environment without activation headaches.
- **Project Hygiene**: Built-in formatters, pre-commit hooks, and deep cleaning tools.
- **Production Ready**: Generates Dockerfiles, Lockfiles, and audits security.

## What You Get

| Feature | Command |
| :--- | :--- |
| **Initialize Project** | `pyclit --template <type>` |
| **Setup Environment** | `pyclit -v` |
| **Run Server** | `pyclit --run UVICORN` |
| **Run Tests** | `pyclit --run PYTEST` |
| **Run Scripts (Proxy)** | `pyclit --runp main.py` |
| **Format Code** | `pyclit --style` |
| **Install Hooks** | `pyclit --hooks` |
| **Clean Artifacts** | `pyclit --clean` |
| **Dockerize** | `pyclit --dockerize` |
| **Audit Health** | `pyclit --health` |

## Quick Start

```bash
# 1. Create a new FastAPI project
pyclit --template fastapi

# 2. Setup venv and install dependencies
pyclit -v -toml

# 3. Format verify code style
pyclit --style

# 4. Run tests
pyclit --run PYTEST

# 5. Start the server with Ngrok tunnel
pyclit --run UVICORN -ngrok
```

## Installation

### Recommended (pipx)
Isolate the tool from your system python:
```bash
pipx install .
```

### Developer
```bash
pip install -e .
```

**Verify:**
```bash
pyclit --help
```

*Note on Windows*: The tool automatically handles `Scripts/python.exe` vs `bin/python` differences.

## Core Concepts

**Project Detection**
`pyclit` scans for `pyproject.toml` (Type: TOML) or `requirements.txt` (Type: REQ) to determine how to install dependencies (supporting Poetry, uv, and pip).

**Virtual Environments**
By default, `pyclit` operates on a `.venv` directory in your project root. It invokes the python executable inside `.venv` directly, so you never need to run `source .venv/bin/activate`.

**Python Resolution**
Flag `-version` attempts to resolve the best Python version using `pyenv` and `[project] requires-python` metadata.

**Non-Destructive**
Most operations check before overwriting. Use `--dry-run` to preview actions.

## User Manual

### Preparation & Setup
- `-v`: Ensure `.venv` exists.
- `-req`: Force install from `requirements.txt`.
- `-toml`: Force install from `pyproject.toml` (tries Poetry -> uv -> pip).
- `-version`: Resolve generic Python version via pyenv.

### Execution
- `--run UVICORN`: Starts Uvicorn. Auto-detects `app = FastAPI()`.
  - usage: `pyclit --run UVICORN -ip 0.0.0.0 -port 8080`
- `--run PYTEST`: Runs pytest in venv.
  - usage: `pyclit --run PYTEST -- -v -k mytest` (pass args after `--`)
- `--run <script.py>`: Runs a python script using venv python.
- `--run "<command>"`: Runs a shell command string with venv in PATH.
- `--runp <target>`: **Proxy Run**. Runs a command/script without checking install state. ideal for quick tasks like `pyclit --runp pip list`.
- `-ngrok`: Exposes UVICORN port via ngrok (requires `ngrok` in PATH).

### Code Quality
- `--style` / `--format`: Runs formatters. Prefers `ruff` if available, falls back to `black` + `isort`.
- `--hooks`: Installs `pre-commit` hooks for the repo.

### Cleanup
- `--clean` / `--nuke`: Removes `__pycache__`, `.pytest_cache`, `dist`, `build`, etc.
- `--rebuild-venv`: When paired with `--clean`, deletes and recreates `.venv`.

### Scaffolding
- `--template <type>`: Generates project structure. Types: `fastapi`, `data`, `cli`.
- `pyclit` auto-generates a robust `.gitignore` when templating.

### Deployment & Audit
- `--dockerize`: Creates an optimized `Dockerfile`.
- `--lock`: Generates `requirements.lock` using `pip-tools` (hash-checking) or `pip freeze`.
- `--health`: Checks for Python version mismatches and known vulnerabilities (via `pip-audit` or `safety`).

## Recipes

### 1. Legacy Project (requirements.txt)
Initialize environment and install dependencies:
```bash
pyclit -v -req
pyclit --run main.py
```

### 2. Modern FastAPI with Poetry/Uv
Detects TOML, installs, and runs server:
```bash
pyclit -v -toml --run UVICORN
```

### 3. Run Tests Quickly
Run all tests with verbose output:
```bash
pyclit --run PYTEST -- -v
```

### 4. Full Cleanup & Reset
Nuclear option to clean caches and reinstall environment:
```bash
pyclit --clean --rebuild-venv --yes
```

### 5. Production Prep
Generate lockfile and Dockerfile:
```bash
pyclit -v --lock
pyclit --dockerize
```

## Troubleshooting

- **`pyenv` not found**: Ensure `pyenv` is in your PATH if using `-version`.
- **Ngrok error**: You need `ngrok` installed and authenticated.
- **Entrypoint not detected**: `pyclit` looks for `app = FastAPI()` in common paths. If not found, use `--run "uvicorn my.app:app ..."`.
- **Permissions**: On Windows, ensure you are not locking files in `.venv` when running `--clean`.

## Philosophy

`pyclit` is a **wrapper**, not a replacement. It delegates to best-in-class tools (`pip`, `uv`, `ruff`, `docker`) rather than reinventing them. It prioritizes "working by default" over complex configuration.

## Contributing

```bash
# Run internal tests
python -m unittest discover tests
```
