# API Reference

The OpenAPI specification can be generated at any time using the helper script:

```bash
python docs/generate_openapi.py
```

This will write `openapi.json` and `openapi.yaml` in `docs/api/` which can then be viewed with Swagger UI or Redoc.

## Interactive Docs

When the application is running locally you can access interactive docs at:

- Swagger UI: <http://localhost:8000/docs>
- Redoc: <http://localhost:8000/redoc>

## Example Usage

```bash
# List all agents
curl -X GET http://localhost:8000/agents
```