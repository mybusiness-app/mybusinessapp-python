"""
ReadAPIClient for managing read-only API agents.
"""

import logging
from pathlib import Path
import json
from typing import Dict, List, Optional

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import OpenApiTool, OpenApiAnonymousAuthDetails
from semantic_kernel.agents import AzureAIAgent

from custom_agents.base_client import BaseClient
from custom_agents.read_api.constants import (
    ADDRESS_API_DESC, ADDRESS_API_INSTRUCTIONS,
    BOOKING_API_DESC, BOOKING_API_INSTRUCTIONS,
    CUSTOMER_API_DESC, CUSTOMER_API_INSTRUCTIONS,
    DOCUMENT_API_DESC, DOCUMENT_API_INSTRUCTIONS,
    EMPLOYEE_API_DESC, EMPLOYEE_API_INSTRUCTIONS,
    PET_API_DESC, PET_API_INSTRUCTIONS,
    TEAM_API_DESC, TEAM_API_INSTRUCTIONS,
    TENANT_API_DESC, TENANT_API_INSTRUCTIONS
)

# Configure logging
logger = logging.getLogger(__name__)

class ReadAPIClient(BaseClient):
    def __init__(self, client: AIProjectClient):
        """
        Initialize the Read API Client with the Azure AI Project Client to create and manage agents.

        Args:
            client (AIProjectClient): The client for the AI Project.
        """
        logger.debug("Initializing ReadAPIClient")
        self.client = client
        self.agent = None
        self.openapi_dir = Path("openapi/mypetparlorapp")
        
    def _load_openapi_spec(self, api_name: str) -> dict:
        """
        Load OpenAPI specification from JSON file.
        
        Args:
            api_name: Name of the API (e.g., 'booking', 'customer')
            
        Returns:
            Dictionary containing the OpenAPI specification
        """
        spec_path = self.openapi_dir / api_name / "swagger.json"
        if not spec_path.exists():
            raise FileNotFoundError(f"OpenAPI spec not found at {spec_path}")
            
        with open(spec_path, "r") as f:
            return json.load(f)
            
    def _create_api_tool(self, api_name: str, description: str) -> OpenApiTool:
        """
        Create an OpenAPI tool for the specified API.
        
        Args:
            api_name: Name of the API (e.g., 'booking', 'customer')
            description: Detailed description of the API functionality
            
        Returns:
            Configured OpenApiTool instance
        """
        spec = self._load_openapi_spec(api_name)
        auth = OpenApiAnonymousAuthDetails()
        
        return OpenApiTool(
            name=f"{api_name}_api",
            spec=spec,
            description=description,
            auth=auth
        )
        
    async def _create_address_api_agent(self) -> AzureAIAgent:
        """Create the address API specialized agent."""
        logger.debug("Creating address API agent")
        address_api = self._create_api_tool("address", ADDRESS_API_DESC)
        address_api_definition = await self.create_agent(
            client=self.client,
            name="address_read_api",
            description="Address API (read-only)",
            instructions=ADDRESS_API_INSTRUCTIONS,
            tools=address_api.definitions
        )
        return AzureAIAgent(
            client=self.client,
            definition=address_api_definition
        )
        
    async def _create_booking_api_agent(self, scheduling_plugin) -> AzureAIAgent:
        """
        Create the booking API specialized agent.
        
        Args:
            scheduling_plugin: Plugin for scheduling functionality
        """
        logger.debug("Creating booking API agent")
        booking_api = self._create_api_tool("booking", BOOKING_API_DESC)
        booking_api_definition = await self.create_agent(
            client=self.client,
            name="booking_read_api",
            description="Booking API (read-only)",
            instructions=BOOKING_API_INSTRUCTIONS,
            tools=booking_api.definitions
        )
        return AzureAIAgent(
            client=self.client,
            definition=booking_api_definition,
            plugins=[scheduling_plugin] if scheduling_plugin else None
        )
        
    async def _create_customer_api_agent(self, importer_plugin) -> AzureAIAgent:
        """
        Create the customer API specialized agent.
        
        Args:
            importer_plugin: Plugin for importing functionality
        """
        logger.debug("Creating customer API agent")
        customer_api = self._create_api_tool("customer", CUSTOMER_API_DESC)
        customer_api_definition = await self.create_agent(
            client=self.client,
            name="customer_read_api",
            description="Customer API (read-only)",
            instructions=CUSTOMER_API_INSTRUCTIONS,
            tools=customer_api.definitions
        )
        return AzureAIAgent(
            client=self.client,
            definition=customer_api_definition,
            plugins=[importer_plugin] if importer_plugin else None
        )
        
    async def _create_document_api_agent(self) -> AzureAIAgent:
        """Create the document API specialized agent."""
        logger.debug("Creating document API agent")
        document_api = self._create_api_tool("document", DOCUMENT_API_DESC)
        document_api_definition = await self.create_agent(
            client=self.client,
            name="document_read_api",
            description="Document API (read-only)",
            instructions=DOCUMENT_API_INSTRUCTIONS,
            tools=document_api.definitions
        )
        return AzureAIAgent(
            client=self.client,
            definition=document_api_definition
        )
        
    async def _create_employee_api_agent(self) -> AzureAIAgent:
        """Create the employee API specialized agent."""
        logger.debug("Creating employee API agent")
        employee_api = self._create_api_tool("employee", EMPLOYEE_API_DESC)
        employee_api_definition = await self.create_agent(
            client=self.client,
            name="employee_read_api",
            description="Employee API (read-only)",
            instructions=EMPLOYEE_API_INSTRUCTIONS,
            tools=employee_api.definitions
        )
        return AzureAIAgent(
            client=self.client,
            definition=employee_api_definition
        )
        
    async def _create_pet_api_agent(self) -> AzureAIAgent:
        """Create the pet API specialized agent."""
        logger.debug("Creating pet API agent")
        pet_api = self._create_api_tool("pet", PET_API_DESC)
        pet_api_definition = await self.create_agent(
            client=self.client,
            name="pet_read_api",
            description="Pet API (read-only)",
            instructions=PET_API_INSTRUCTIONS,
            tools=pet_api.definitions
        )
        return AzureAIAgent(
            client=self.client,
            definition=pet_api_definition
        )
        
    async def _create_team_api_agent(self) -> AzureAIAgent:
        """Create the team API specialized agent."""
        logger.debug("Creating team API agent")
        team_api = self._create_api_tool("team", TEAM_API_DESC)
        team_api_definition = await self.create_agent(
            client=self.client,
            name="team_read_api",
            description="Team API (read-only)",
            instructions=TEAM_API_INSTRUCTIONS,
            tools=team_api.definitions
        )
        return AzureAIAgent(
            client=self.client,
            definition=team_api_definition
        )
        
    async def _create_tenant_api_agent(self) -> AzureAIAgent:
        """Create the tenant API specialized agent."""
        logger.debug("Creating tenant API agent")
        tenant_api = self._create_api_tool("tenants", TENANT_API_DESC)
        tenant_api_definition = await self.create_agent(
            client=self.client,
            name="tenant_read_api",
            description="Tenant API (read-only)",
            instructions=TENANT_API_INSTRUCTIONS,
            tools=tenant_api.definitions
        )
        return AzureAIAgent(
            client=self.client,
            definition=tenant_api_definition
        )
        
    async def initialize(self, scheduling_plugin=None, importer_plugin=None) -> Dict[str, AzureAIAgent]:
        """
        Initializes all read API agents.
        
        Args:
            scheduling_plugin: Optional plugin for scheduling functionality
            importer_plugin: Optional plugin for importing functionality
            
        Returns:
            Dictionary mapping agent names to their instances
        """
        logger.debug("Initializing all read API agents")
        
        # Create all specialized API agents
        address_agent = await self._create_address_api_agent()
        booking_agent = await self._create_booking_api_agent(scheduling_plugin)
        customer_agent = await self._create_customer_api_agent(importer_plugin)
        document_agent = await self._create_document_api_agent()
        employee_agent = await self._create_employee_api_agent()
        pet_agent = await self._create_pet_api_agent()
        team_agent = await self._create_team_api_agent()
        tenant_agent = await self._create_tenant_api_agent()
        
        # Return all agents in a dictionary for easy access
        agents = {
            "address": address_agent,
            "booking": booking_agent,
            "customer": customer_agent,
            "document": document_agent,
            "employee": employee_agent,
            "pet": pet_agent,
            "team": team_agent,
            "tenant": tenant_agent
        }
        
        logger.debug("ReadAPIClient initialized successfully")
        return agents 