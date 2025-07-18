# Quick-Start Tutorial

This guide walks you through standing up the Spec-Driven Agent Workflow locally in **five minutes**.

---

## 1. Clone the Repository

```bash
git clone https://github.com/your-org/spec-driven-agent.git
cd spec-driven-agent
```

## 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the Application

```bash
uvicorn spec_driven_agent.main:app --reload
```

You should see output similar to:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## 5. Explore the API

Open <http://127.0.0.1:8000/docs> to launch the interactive Swagger UI.

Try the `/health` endpoint (if defined) or list available routes.

## 6. Next Steps

* Read the [Architecture Overview](../architecture/overview.md) to understand system components.
* Generate the OpenAPI schema: `python docs/generate_openapi.py`.
* Continue to the [Installation Guide](../deployment/installation.md) for production-ready setup.