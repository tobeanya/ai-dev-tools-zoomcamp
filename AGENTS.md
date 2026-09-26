# AGENTS

This repository is a Python project for the AI Dev Tools Zoomcamp.

## Project purpose
- Keep the environment reproducible using uv.
- Prefer small, focused Python packages and tests.
- Use clear naming and keep code easy to read.

## Workflow
- Use the virtual environment in `.venv` for Python commands.
- Prefer `uv pip install ...` for dependency management.
- Run tests with `pytest` before considering work complete.
- Keep documentation readable and project-specific.

## Commands
```bash
# activate venv
.venv\Scripts\Activate.ps1

# install project in editable mode
uv pip install -e .

# run tests
pytest
```

## Notes
- Keep secrets out of source control.
- Use `.env` files locally if needed.
- Prefer concise, maintainable code over clever shortcuts.
- Dependencies are added in `pyproject.toml`. Do not add one without asking.
