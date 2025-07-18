# Quickstart Example Project

This example demonstrates a minimal end-to-end flow using the Spec-Driven Agent Workflow.

1. **Start the API**

   ```bash
   uvicorn spec_driven_agent.main:app --reload
   ```

2. **Create a New Project via API**

   ```bash
   curl -X POST -H "Content-Type: application/json" \
        -d '{"name": "Todo App", "description": "Track todos"}' \
        http://localhost:8000/projects
   ```

3. **Generate OpenAPI spec**

   ```bash
   python docs/generate_openapi.py
   open docs/api/openapi.html
   ```

Refer to the [Quick-Start Tutorial](../../docs/tutorials/quickstart.md) for detailed steps.