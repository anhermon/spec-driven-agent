# Contributing Guide

Thank you for considering contributing to the Spec-Driven Agent Workflow!

## Development Environment

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dev dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pre-commit install
   ```

3. Run tests to ensure everything is working:

   ```bash
   pytest -q
   ```

## Pull Request Checklist

- [ ] Follows project coding standards (`black`, `isort`, `flake8`, `mypy`).
- [ ] New functionality is covered by unit/integration tests.
- [ ] Documentation is updated where applicable.
- [ ] CI pipeline passes.

## Commit Message Format

We follow the Conventional Commits specification, e.g.

```
feat(agents): add new summarizer agent
```

## Code of Conduct

This project adopts the [Contributor Covenant](https://www.contributor-covenant.org/). Please be respectful and considerate in all interactions.