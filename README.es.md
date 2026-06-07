[Español](README.es.md) | [English](README.en.md)

---

# PythonCLITools (`pyclit`)

Automatiza el ciclo de vida de proyectos Python: scaffolding, dependencias, entornos virtuales, ejecucion y preparacion para despliegue.

## Que ofrece

| Funcion | Comando |
| :--- | :--- |
| Inicializar proyecto | `pyclit --template <type>` |
| Preparar entorno | `pyclit -v` |
| Ejecutar servidor | `pyclit --run UVICORN` |
| Ejecutar tests | `pyclit --run PYTEST` |
| Ejecutar scripts | `pyclit --runp main.py` |
| Formatear codigo | `pyclit --style` |
| Instalar hooks | `pyclit --hooks` |
| Limpiar artefactos | `pyclit --clean` |
| Generar Dockerfile | `pyclit --dockerize` |
| Auditar salud | `pyclit --health` |

## Inicio rapido

```bash
pyclit --template fastapi
pyclit -v -toml
pyclit --style
pyclit --run PYTEST
pyclit --run UVICORN -ngrok
```

## Instalacion

### Recomendado con pipx

```bash
pipx install .
```

### Desarrollo

```bash
pip install -e .
pyclit --help
```

## Conceptos clave

- Detecta `pyproject.toml` o `requirements.txt`.
- Gestiona `.venv` sin necesidad de activar el entorno.
- Resuelve versiones de Python con `pyenv` cuando procede.
- Usa operaciones no destructivas y ofrece `--dry-run`.

## Uso recomendado

Usa `pyclit` para estandarizar tareas repetidas en proyectos Python y reducir friccion al alternar entre repositorios.
