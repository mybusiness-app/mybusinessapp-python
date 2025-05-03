import logging

from azure.ai.projects import AIProjectClient
from semantic_kernel.agents import AzureAIAgent
from custom_agents.base_client import BaseClient
from custom_agents.setup_guide.constants import SETUP_GUIDE_INSTRUCTIONS, USER_SETUP_INSTRUCTIONS

# Configure logging
logger = logging.getLogger(__name__)

class SetupGuideClient(BaseClient):
    def __init__(self, client: AIProjectClient):
        """
        Initialize the Setup Guide Client with the Azure AI Project Client to create and manage agents.

        Args:
            client (AIProjectClient): The client for the AI Project.
        """
        logger.debug("Initializing SetupGuideClient")
        self.client = client
        self.agent = None
        
    async def _create_user_setup_agent(self):
        """Create the user setup specialized agent."""
        logger.debug("Creating user setup agent")
        user_setup_definition = await self.create_agent(
            client=self.client,
            name="user_setup",
            description="A specialist in setting up the user's profile and security",
            instructions=USER_SETUP_INSTRUCTIONS
        )
        return AzureAIAgent(
            client=self.client,
            definition=user_setup_definition
        )
        
    async def _create_setup_guide_agent(self, plugins):
        """Create the main setup guide agent with plugins."""
        logger.debug("Creating main setup guide agent")
        setup_guide_definition = await self.create_agent(
            client=self.client,
            name="setup_guide",
            description="Main coordinator for the MyPetParlor App portal setup process",
            instructions=SETUP_GUIDE_INSTRUCTIONS
        )
        return AzureAIAgent(
            client=self.client,
            definition=setup_guide_definition,
            plugins=plugins
        )
        
    async def initialize(self):
        """Initializes all setup guide agents."""
        logger.debug("Initializing all setup guide agents")
        
        # Create specialized setup agents
        user_setup_agent = await self._create_user_setup_agent()
        
        # Create the main setup guide agent with plugins
        logger.debug("Creating main setup guide agent with plugins")
        self.agent = await self._create_setup_guide_agent(
            plugins=[user_setup_agent]
        )
        
        logger.debug("SetupGuideAgent initialized successfully")
        return self.agent