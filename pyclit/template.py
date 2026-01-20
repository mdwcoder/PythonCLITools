import os
from .util import write_file_safe

def generate_gitignore(logger, dry_run=False):
    """
    Generates a robust .gitignore
    """
    content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Testing
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/
.tox/
.nox/

# Tools
.ruff_cache/
.pre-commit-config.yaml.save

# IDEs
.idea/
.vscode/
*.swp
*.swo
"""
    write_file_safe(".gitignore", content, logger, dry_run=dry_run)

def create_template(kind, logger, dry_run=False):
    """
    Creates project structure.
    """
    if kind == "fastapi":
        # Dirs
        dirs = ["app", "app/routers"]
        for d in dirs:
            logger.step(f"Creating dir {d}/")
            if not dry_run:
                os.makedirs(d, exist_ok=True)
        
        # Files
        main_py = """from fastapi import FastAPI
from .routers import items

app = FastAPI()

app.include_router(items.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
"""
        items_py = """from fastapi import APIRouter

router = APIRouter(prefix="/items")

@router.get("/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
"""
        write_file_safe("app/main.py", main_py, logger, dry_run)
        write_file_safe("app/routers/items.py", items_py, logger, dry_run)
        write_file_safe("app/routers/__init__.py", "", logger, dry_run)
        
        # Deps
        logger.step("Adding dependnecies: fastapi, uvicorn")
        if not dry_run:
            with open("requirements.txt", "a") as f:
                f.write("\nfastapi\nuvicorn\n")
    
    elif kind == "cli":
        os.makedirs("src", exist_ok=True)
        
        main_py = """import typer

app = typer.Typer()

@app.command()
def hello(name: str):
    print(f"Hello {name}")

if __name__ == "__main__":
    app()
"""
        write_file_safe("src/main.py", main_py, logger, dry_run)
        
        logger.step("Adding dependencies: typer")
        if not dry_run:
             with open("requirements.txt", "a") as f:
                f.write("\ntyper\n")

    elif kind == "data":
        for d in ["notebooks", "data", "scripts"]:
             os.makedirs(d, exist_ok=True)
        
        logger.step("Adding dependencies: pandas, numpy")
        if not dry_run:
             with open("requirements.txt", "a") as f:
                f.write("\npandas\nnumpy\n")
    
    else:
        logger.error(f"Unknown template: {kind}")
