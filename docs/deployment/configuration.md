# Configuration Guide

The application is configured primarily via **environment variables**. Copy `.env.example` to `.env` and update values as needed.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/agent` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `OPENAI_API_KEY` | API key for OpenAI integration | _empty_ |

## Loading the Environment

We use [python-dotenv](https://pypi.org/project/python-dotenv/) which automatically loads `.env` when running `uvicorn`.

```bash
cp .env.example .env
nano .env  # or your editor
```

## Secret Management

For production environments consider:

- **Docker secrets**
- **Vault** (Hashicorp)
- **AWS Parameter Store** or **Secrets Manager**

Never commit secrets to version control.