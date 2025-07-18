"""
Main FastAPI application for the spec-driven agent workflow system.
"""

from typing import Any, Dict
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import __version__
from .agents import AgentManager, AnalystAgent, ProductManagerAgent
from .core.llm_integration import LLMIntegrationError, get_llm_integration
from .models.task import Task, TaskStatus

# Create FastAPI application
app = FastAPI(
    title="Spec-Driven Agent Workflow",
    description=(
        "A comprehensive spec-driven development workflow that combines the "
        "best practices from BMAD-METHOD, Context Engineering, and "
        "Spec-Driven Development, enhanced with A2A (Agent-to-Agent) "
        "communication protocols."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent manager
agent_manager = AgentManager()

# Initialize some test agents
analyst_agent = AnalystAgent()
pm_agent = ProductManagerAgent()

# Register agents
agent_manager.register_agent(analyst_agent)
agent_manager.register_agent(pm_agent)


@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "name": "Spec-Driven Agent Workflow",
        "version": __version__,
        "description": "A comprehensive spec-driven development workflow system",
        "status": "active",
        "docs": "/docs",
        "cli": "Use 'agent --help' for CLI commands",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": "2024-01-01T00:00:00Z",  # This would be dynamic
    }


@app.get("/api/v1/agents")
async def list_agents():
    """List all registered agents."""
    return {
        "agents": agent_manager.list_agents(),
        "total": len(agent_manager.agents),
    }


@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details."""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    status = await agent.get_status()
    return status


@app.post("/api/v1/agents/{agent_id}/ping")
async def ping_agent(agent_id: str):
    """Ping an agent to check if it's alive."""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return await agent.ping()


@app.post("/api/v1/agents/{agent_id}/tasks")
async def assign_task(agent_id: str, task_data: Dict[str, Any]):
    """Assign a task to an agent."""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Create task from request data
    task = Task(
        name=task_data.get("title", "Generic Task"),  # Required by StatusModel
        status=TaskStatus.PENDING,  # Required by StatusModel
        task_id=task_data.get("task_id", f"task-{agent_id}-001"),
        task_type=task_data.get("task_type", "generic"),
        task_name=task_data.get("title", "Generic Task"),  # Map title to task_name
        description=task_data.get("description", "A generic task"),
        priority=task_data.get("priority", "medium"),
        assigned_agent_id=uuid4(),  # Generate a UUID for the agent
        dependencies=task_data.get("dependencies", []),
        workflow_id=uuid4(),  # Generate a UUID for the workflow
        phase="test-phase",  # Required field
    )

    # Process the task
    result = await agent_manager.assign_task(agent_id, task)

    return {
        "task_id": task.task_id,
        "agent_id": agent_id,
        "result": {
            "success": result.success,
            "message": result.message,
            "error_message": result.error_message,
            "artifacts": [
                {
                    "artifact_id": artifact.artifact_id,
                    "name": artifact.name,
                    "artifact_type": artifact.artifact_type.value,
                }
                for artifact in result.artifacts
            ]
            if result.artifacts
            else [],
        },
    }


@app.get("/api/v1/system/status")
async def get_system_status():
    """Get overall system status."""
    return await agent_manager.get_system_status()


@app.get("/api/v1/projects")
async def list_projects():
    """List all projects."""
    # This would integrate with the actual project management
    return {
        "projects": [],
        "total": 0,
    }


@app.post("/api/v1/projects")
async def create_project(project_data: dict):
    """Create a new project."""
    # This would integrate with the actual project creation
    return {
        "project_id": "new-project-id",
        "status": "created",
    }


@app.get("/api/v1/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details."""
    # This would integrate with the actual project retrieval
    return {
        "project_id": project_id,
        "name": "Sample Project",
        "status": "active",
    }


@app.get("/api/v1/projects/{project_id}/workflow")
async def get_workflow(project_id: str):
    """Get workflow status for a project."""
    # This would integrate with the actual workflow management
    return {
        "project_id": project_id,
        "workflow_status": "active",
        "current_phase": "development",
    }


@app.post("/api/v1/projects/{project_id}/workflow/transition")
async def transition_workflow(project_id: str, phase: str):
    """Transition workflow to a new phase."""
    # This would integrate with the actual workflow orchestration
    return {
        "project_id": project_id,
        "new_phase": phase,
        "status": "transitioned",
    }


# LLM Integration Endpoints
@app.get("/api/v1/llm/health")
async def llm_health_check():
    """Check LLM integration health."""
    try:
        llm = await get_llm_integration()
        result = await llm.test_connection()
        return {
            "status": "healthy",
            "llm_integration": result,
        }
    except LLMIntegrationError as e:
        raise HTTPException(
            status_code=503, detail=f"LLM integration error: {e.message}"
        )


@app.post("/api/v1/llm/analyze-requirements")
async def analyze_requirements(requirements_data: Dict[str, Any]):
    """Analyze requirements using LLM."""
    try:
        llm = await get_llm_integration()
        requirements_text = requirements_data.get("requirements", "")

        if not requirements_text:
            raise HTTPException(status_code=400, detail="Requirements text is required")

        result = await llm.analyze_requirements(requirements_text)
        return {
            "status": "success",
            "analysis": result["analysis"],
            "usage": result["usage"],
            "model": result["model"],
        }
    except LLMIntegrationError as e:
        raise HTTPException(status_code=503, detail=f"LLM analysis error: {e.message}")


@app.post("/api/v1/llm/generate-api-spec")
async def generate_api_spec(requirements_data: Dict[str, Any]):
    """Generate API specification using LLM."""
    try:
        llm = await get_llm_integration()
        requirements_analysis = requirements_data.get("requirements_analysis", "")

        if not requirements_analysis:
            raise HTTPException(
                status_code=400, detail="Requirements analysis is required"
            )

        result = await llm.generate_api_spec(requirements_analysis)
        return {
            "status": "success",
            "api_spec": result["api_spec"],
            "usage": result["usage"],
            "model": result["model"],
        }
    except LLMIntegrationError as e:
        raise HTTPException(
            status_code=503, detail=f"LLM generation error: {e.message}"
        )


@app.post("/api/v1/llm/validate-consistency")
async def validate_consistency(context_data: Dict[str, Any]):
    """Validate consistency using LLM."""
    try:
        llm = await get_llm_integration()

        if not context_data:
            raise HTTPException(status_code=400, detail="Context data is required")

        result = await llm.validate_consistency(context_data)
        return {
            "status": "success",
            "consistency_analysis": result["consistency_analysis"],
            "usage": result["usage"],
            "model": result["model"],
        }
    except LLMIntegrationError as e:
        raise HTTPException(
            status_code=503, detail=f"LLM validation error: {e.message}"
        )


@app.post("/api/v1/llm/generate-task-plan")
async def generate_task_plan(task_data: Dict[str, Any]):
    """Generate task execution plan using LLM."""
    try:
        llm = await get_llm_integration()
        task_description = task_data.get("task_description", "")
        context = task_data.get("context", {})

        if not task_description:
            raise HTTPException(status_code=400, detail="Task description is required")

        result = await llm.generate_task_plan(task_description, context)
        return {
            "status": "success",
            "task_plan": result["task_plan"],
            "usage": result["usage"],
            "model": result["model"],
        }
    except LLMIntegrationError as e:
        raise HTTPException(status_code=503, detail=f"LLM planning error: {e.message}")


@app.post("/api/v1/llm/generate-text")
async def generate_text(text_request: Dict[str, Any]):
    """Generate text using LLM."""
    try:
        llm = await get_llm_integration()
        prompt = text_request.get("prompt", "")
        model = text_request.get("model", "gpt-4")
        max_tokens = text_request.get("max_tokens", 1000)
        temperature = text_request.get("temperature", 0.7)
        system_message = text_request.get("system_message")

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        result = await llm.generate_text(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_message=system_message,
        )
        return {
            "status": "success",
            "text": result["text"],
            "usage": result["usage"],
            "model": result["model"],
            "finish_reason": result["finish_reason"],
        }
    except LLMIntegrationError as e:
        raise HTTPException(
            status_code=503, detail=f"LLM generation error: {e.message}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )


def main():
    """Main entry point for the application."""
    uvicorn.run(
        "spec_driven_agent.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
