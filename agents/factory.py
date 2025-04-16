"""
Agent factory for creating and managing MyPetParlor agents.
"""
from typing import Dict, Optional
from .base import BaseAgent
from .azure.smart_scheduling.agent import SmartSchedulingAgent
from .azure.smart_importer.agent import SmartImporterAgent
import os

class AgentFactory:
    """Factory for creating and managing agents."""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        
    async def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Get or create an agent of the specified type."""
        if agent_type in self._agents:
            return self._agents[agent_type]
            
        agent = await self._create_agent(agent_type)
        if agent:
            self._agents[agent_type] = agent
            await agent.initialize()
        return agent
    
    async def _create_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Create a new agent instance."""
        if agent_type == "smart_scheduling":
            project_connection_string = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
            if not project_connection_string:
                raise ValueError("AZURE_AI_PROJECT_CONNECTION_STRING environment variable not set")
            return SmartSchedulingAgent(project_connection_string)
        elif agent_type == "smart_importer":
            project_connection_string = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
            if not project_connection_string:
                raise ValueError("AZURE_AI_PROJECT_CONNECTION_STRING environment variable not set")
            return SmartImporterAgent(project_connection_string)
            
        return None
        
    def get_available_agents(self) -> list[str]:
        """Get list of available agent types."""
        return ["smart_scheduling", "smart_importer"]