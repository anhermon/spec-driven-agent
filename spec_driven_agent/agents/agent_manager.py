"""
Agent manager for coordinating and managing agents in the system.
"""

from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent, SimpleTaskResult
from ..models.agent import AgentRole
from ..models.task import Task


class AgentManager:
    """Manages all agents in the system."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the manager."""
        self.agents[agent.agent_id] = agent
        
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
        
    def get_agents_by_role(self, role: AgentRole) -> List[BaseAgent]:
        """Get all agents with a specific role."""
        return [agent for agent in self.agents.values() if agent.role == role]
        
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents."""
        return [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "role": agent.role,  # AgentRole is already a string
                "status": agent.status.value
            }
            for agent in self.agents.values()
        ]
        
    async def assign_task(self, agent_id: str, task: Task) -> SimpleTaskResult:
        """Assign a task to a specific agent."""
        agent = self.get_agent(agent_id)
        if not agent:
            return SimpleTaskResult(
                task_id=task.task_id,
                success=False,
                error_message=f"Agent {agent_id} not found",
                artifacts=[]
            )
        
        return await agent.process_task(task)
        
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        agent_statuses = []
        for agent in self.agents.values():
            status = await agent.get_status()
            agent_statuses.append(status)
            
        return {
            "total_agents": len(self.agents),
            "agents": agent_statuses,
            "system_status": "healthy"
        } 