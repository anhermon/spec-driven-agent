"""
Main FastAPI application for the spec-driven agent workflow system.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from . import __version__
from .cli import app as cli_app

# Create FastAPI application
app = FastAPI(
    title="Spec-Driven Agent Workflow",
    description="A comprehensive spec-driven development workflow that combines the best practices from BMAD-METHOD, Context Engineering, and Spec-Driven Development, enhanced with A2A (Agent-to-Agent) communication protocols.",
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