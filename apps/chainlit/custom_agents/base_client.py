from typing import Any, Coroutine, List, Optional
from azure.ai.projects import AIProjectClient
from semantic_kernel.agents import Agent
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

class BaseClient:
    """
    Base class for creating and managing clients with Azure AI Agents.
    """
    
    # Get the model deployment name from environment variables
    AGENT_MODEL = os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")
    
    @staticmethod
    async def create_agent(client: AIProjectClient, name: str, description: str, 
                     instructions: str, tools: Optional[List] = None) -> Coroutine[Any, Any, Agent]:
        """
        Create an Azure AI Agent with the specified parameters.
        
        Args:
            client: AzureAIAgent client
            name: Name of the agent
            description: Short description of the agent's purpose
            instructions: Detailed instructions for the agent
            tools: Optional list of tool definitions
            
        Returns:
            Agent definition object
        """
        if not BaseClient.AGENT_MODEL:
            raise EnvironmentError("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME environment variable is not set")
        
        agent_args = {
            "model": BaseClient.AGENT_MODEL,
            "name": name,
            "description": description,
            "instructions": instructions
        }
        
        if tools:
            agent_args["tools"] = tools
            
        logger.debug(f"Creating agent: {name}")
        return await client.agents.create_agent(**agent_args)
