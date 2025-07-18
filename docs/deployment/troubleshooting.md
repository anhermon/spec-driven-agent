# Troubleshooting

Below are common issues you might encounter and steps to resolve them.

## Unable to Start Uvicorn

**Symptoms**: `Address already in use` or app exits immediately.

**Fix**: Another process is using port 8000.

```bash
lsof -i :8000  # identify process
kill -9 <pid>
```

---

## Database Connection Errors

**Symptoms**: `psycopg2.OperationalError` during startup.

**Fixes**:
1. Verify `DATABASE_URL` in `.env` is correct.
2. Check PostgreSQL is running and accessible.
3. Ensure the user has correct privileges.

---

## 404 on `/docs`

**Symptoms**: Swagger UI not found.

**Fix**: Confirm you are on `http://<host>:<port>/docs` and that the FastAPI `app` is being served (not a sub-application).

---

## Out-of-Memory (OOM) in Docker

Add limits or increase Docker memory allocation. Example docker-compose excerpt:

```yaml
services:
  api:
    mem_limit: 1g
```

---

If your issue isn’t listed, please open a ticket on GitHub and include logs plus steps to reproduce.