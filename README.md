# Spec-Driven Agent Workflow

A comprehensive spec-driven development workflow that combines the best practices from BMAD-METHOD, Context Engineering, and Spec-Driven Development, enhanced with A2A (Agent-to-Agent) communication protocols.

## 🚀 Overview

This system implements an intelligent agent-based workflow where specialized AI agents collaborate to build software from requirements to deployment, following a spec-driven approach that ensures consistency and quality throughout the development process.

### Key Features

- **🤖 Intelligent Agents**: 8 specialized agents (Analyst, PM, Architect, Scrum Master, Developer, QA, UX Expert, Product Owner)
- **🧠 Rich Context**: Persistent context management with symbolic mechanisms
- **📋 Spec-Driven**: Design-first approach with API specifications as the source of truth
- **🔗 A2A Communication**: Standardized agent-to-agent communication using A2A SDK
- **👤 User Control**: Full visibility and control over the development process
- **💻 IDE Integration**: Seamless integration with development environments

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Interface Layer                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Web UI    │ │   CLI       │ │   IDE       │ │   API       │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ Workflow    │ │ Context     │ │ Task        │ │ Event       │ │
│  │ Manager     │ │ Manager     │ │ Scheduler   │ │ Bus         │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Layer                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ Analyst     │ │ PM          │ │ Architect   │ │ Scrum Master│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ Developer   │ │ QA          │ │ UX Expert   │ │ Product     │ │
│  │             │ │             │ │             │ │ Owner       │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    Communication Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ A2A         │ │ Context     │ │ Memory      │ │ Artifact    │ │
│  │ SDK         │ │ Engine      │ │ Store       │ │ Manager     │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ Database    │ │ File        │ │ AI/LLM      │ │ Monitoring  │ │
│  │             │ │ System      │ │ Services    │ │ & Logging   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

- **🐍 Python 3.9+**: Core orchestration and AI agent logic
- **🚀 FastAPI**: High-performance web framework for APIs
- **🤖 A2A SDK**: Agent-to-agent communication protocol
- **🔍 Pydantic AI**: AI-powered data validation and processing
- **🗄️ PostgreSQL**: Reliable database for project data
- **🧠 ChromaDB**: Vector database for semantic search
- **⚡ Redis**: Caching and session management

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 13 or higher
- Redis 6 or higher

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd spec-driven-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   uvicorn spec_driven_agent.main:app --reload
   ```

## 🚀 Quick Start

### Using the CLI

```bash
# Start a new project
agent spec create --name "Task Management App" --description "A web app for team task management"

# Generate requirements
agent spec generate --from requirements.md

# Design architecture
agent architect design --api-spec

# Implement features
agent developer implement --story user-auth

# Run tests
agent qa test --module auth
```

### Using the Web Interface

1. Open your browser to `http://localhost:8000`
2. Create a new project
3. Watch as agents collaborate to build your application
4. Review and approve each phase of development

## 🔄 Workflow Phases

### Phase 1: Discovery & Planning
- **Analyst Agent**: Conducts stakeholder interviews and market research
- **PM Agent**: Creates comprehensive Product Requirements Document (PRD)
- **User**: Reviews and approves requirements

### Phase 2: Architecture & Design
- **Architect Agent**: Analyzes requirements and proposes system design
- **User**: Provides technical constraints and preferences
- **Output**: Detailed architecture document and API specifications

### Phase 3: Development
- **Scrum Master Agent**: Breaks down work into manageable stories
- **Developer Agent**: Implements features with continuous feedback
- **User**: Reviews progress and provides guidance

### Phase 4: Testing & Deployment
- **QA Agent**: Runs comprehensive tests and validation
- **UX Expert Agent**: Ensures user experience quality
- **Product Owner Agent**: Validates against original requirements

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=spec_driven_agent

# Run specific test file
pytest tests/test_workflow.py
```

## 🛠️ Development

### Code Quality

```bash
# Format code
black spec_driven_agent/

# Sort imports
isort spec_driven_agent/

# Type checking
mypy spec_driven_agent/

# Linting
flake8 spec_driven_agent/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [Agent Development Guide](docs/agents.md)
- [API Reference](docs/api.md)
- [IDE Integration Guide](docs/ide-integration.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

## 🗺️ Roadmap

- [ ] Phase 1: Core Engine (Weeks 1-2)
  - [ ] Spec-Driven Context Engine
  - [ ] Workflow Orchestrator
  - [ ] CLI Interface
- [ ] Phase 2: Agent Implementation (Weeks 3-4)
  - [ ] Analyst Agent
  - [ ] Architect Agent
  - [ ] Developer Agent
- [ ] Phase 3: User Interface (Weeks 5-6)
  - [ ] Web Dashboard
  - [ ] Real-time Progress Tracking
- [ ] Phase 4: Advanced Integration (Weeks 7-8)
  - [ ] LSP Integration
  - [ ] Performance Optimization
