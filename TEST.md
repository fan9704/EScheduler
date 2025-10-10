# EScheduler Test Document

---

## Environments

- Python 3.12
- uv
- Pytest
- Pytest-asyncio
- Pytest-cov

### Install Dev Package for Testing

```shell
uv add --dev pytest
uv sync # Sync with all packages
uv sync --no-dev # Sync with no dev packages
```

### Check Testing Fixtures

```shell
uv run pytest --fixtures  
```

---

## Unit Test

```shell
uv run pytest -v
```

---

## E2E Test

```shell
uv run pytest -v
```