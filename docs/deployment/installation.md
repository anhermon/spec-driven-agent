# Installation Guide

This document describes how to install the Spec-Driven Agent Workflow in a variety of environments.

## Local Development

1. **Prerequisites**
   - Python 3.9+
   - Git

2. **Clone & Install**

```bash
git clone https://github.com/your-org/spec-driven-agent.git
cd spec-driven-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Start the App**

```bash
uvicorn spec_driven_agent.main:app --reload
```

## Docker

We provide a sample `Dockerfile` (TBD). Until then:

```bash
docker build -t spec-driven-agent .
docker run -p 8000:8000 spec-driven-agent
```

## Production Deployment

For production we recommend:

- **Uvicorn + Gunicorn** behind **NGINX**
- A **PostgreSQL** database
- **Redis** for caching

Example systemd service (excerpt):

```ini
[Unit]
Description=Spec Driven Agent API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/spec-driven-agent
ExecStart=/usr/local/bin/gunicorn -k uvicorn.workers.UvicornWorker -c gunicorn_conf.py spec_driven_agent.main:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```