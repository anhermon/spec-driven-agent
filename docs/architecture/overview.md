# Architecture Overview

```mermaid
graph TD
    UI[User Interfaces]
    CLI[CLI]
    IDE[IDE Integrations]
    API[REST API]
    Orch[Workflow Orchestrator]
    Ctx[Context Engine]
    Agents[AI Agents]
    DB[(PostgreSQL)]
    Redis[(Redis)]

    UI --> Orch
    CLI --> Orch
    IDE --> Orch
    API --> Orch
    Orch --> Ctx
    Orch --> Agents
    Ctx --> DB
    Agents --> Redis
```

> **Figure:** High-level component diagram.

The system is divided into three primary layers:

1. **Interface Layer** – Web UI, CLI, IDE plugins & REST API.
2. **Orchestration Layer** – Coordinates workflows, tasks and events.
3. **Agent Layer** – Specialized AI agents executing domain-specific responsibilities.

See the repository’s `memory-bank/systemPatterns.md` for deeper insights into design patterns.