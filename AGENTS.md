# AGENTS

This repository is a Python project for the AI Dev Tools Zoomcamp.

## Project context

The product being built is the **Weekly Project Feedback SaaS** — see
`_docs/weekly-project-feedback-mvp-scope.md` for the full spec,
`_docs/tech-stack-options.md` for the stack decision, and
`_docs/architecture.md` for the resulting architecture. All project docs
live under `_docs/`.

**Chosen stack:** Django + Django REST Framework, PostgreSQL, Celery +
Redis, django-allauth (Option 1 in the tech stack doc).

**Task tracking:** the build is broken into small, self-contained tasks
in `_docs/tasks.md`, each mirrored as a GitHub issue. Issues #1-30 are
the active v1 backlog; issues labeled `post-v1` are deferred scope, not
dropped scope — see `_docs/tasks.md` §2 for why each was deferred.

## Project structure

- `manage.py` — Django entry point (repo root).
- `ai_dev_tools_zoomcamp/` — the Django project package: `settings.py`,
  `urls.py`, `wsgi.py`, `asgi.py`. Domain apps (tenancy, feedback,
  themes, voting, etc. — see `_docs/architecture.md` §3) get added here
  as their tasks are implemented.
- `tests/` — test suite (pytest + pytest-django, configured in
  `pyproject.toml`).

**Database:** defaults to SQLite with zero setup (`db.sqlite3`, already
gitignored). Set `DATABASE_HOST` (plus `DATABASE_NAME`/`USER`/
`PASSWORD`/`PORT` as needed) to switch to Postgres — the `psycopg`
driver is already installed either way.

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

# install project in editable mode (includes dev dependencies)
uv pip install -e ".[dev]"

# run tests
pytest

# run the dev server
python manage.py runserver

# Django system check
python manage.py check
```

## Notes
- Keep secrets out of source control.
- Use `.env` files locally if needed.
- Prefer concise, maintainable code over clever shortcuts.
- Dependencies are added in `pyproject.toml`. Do not add one without asking.
