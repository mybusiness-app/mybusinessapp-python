"""
TriageClient for managing the main triage agent.
"""

import logging
from typing import Dict, List, Optional

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool
from semantic_kernel.agents import AzureAIAgent

from custom_agents.base_client import BaseClient
from custom_agents.triage.constants import TRIAGE_INSTRUCTIONS

# Configure logging
logger = logging.getLogger(__name__)

class TriageClient(BaseClient):
    def __init__(self, client: AIProjectClient):
        """
        Initialize the Triage Client with the Azure AI Project Client to create and manage agents.

        Args:
            client (AIProjectClient): The client for the AI Project.
        """
        logger.debug("Initializing TriageClient")
        self.client = client
        self.agent = None
        
    async def _create_data_analysis_agent(self) -> AzureAIAgent:
        """Create the data analysis specialized agent."""
        logger.debug("Creating data analysis agent")
        code_interpreter = CodeInterpreterTool()
        data_analysis_definition = await self.create_agent(
            client=self.client,
            name="data_analysis",
            description="An expert in analyzing data that MUST be already fetched from its source (e.g. API) in a previous step",
            instructions="""You are an expert in analyzing fetched data.
            You can use the Code Interpreter tool to run queries and advanced analysis on the data.""",
            tools=code_interpreter.definitions
        )
        return AzureAIAgent(
            client=self.client,
            definition=data_analysis_definition
        )
        
    async def _create_triage_agent(self, plugins: List[AzureAIAgent]) -> AzureAIAgent:
        """Create the main triage agent with plugins."""
        logger.debug("Creating main triage agent")
        triage_definition = await self.create_agent(
            client=self.client,
            name="triage",
            description="Main coordinator that routes requests to specialized agents",
            instructions=TRIAGE_INSTRUCTIONS
        )
        return AzureAIAgent(
            client=self.client,
            definition=triage_definition,
            plugins=plugins
        )
        
    async def initialize(self, setup_guide_agent: AzureAIAgent, api_agents: Dict[str, AzureAIAgent]) -> AzureAIAgent:
        """
        Initializes the triage agent with all its plugins.
        
        Args:
            setup_guide_agent: The setup guide agent to use as a plugin
            api_agents: Dictionary of API agents to use as plugins
            
        Returns:
            The initialized triage agent
        """
        logger.debug("Initializing triage agent")
        
        # Create data analysis agent
        data_analysis_agent = await self._create_data_analysis_agent()
        
        # Create the main triage agent with all plugins
        self.agent = await self._create_triage_agent(
            plugins=[
                setup_guide_agent,
                data_analysis_agent,
                *api_agents.values()
            ]
        )
        
        logger.debug("TriageClient initialized successfully")
        return self.agent
