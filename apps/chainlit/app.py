"""
MyPetParlor AI Assistant - Chainlit frontend for Azure AI Agents
---
This application provides a chat interface for interacting with specialized Azure AI agents
that help users manage their MyPetParlor App portal through various APIs.

Author: [Your Name]
Version: 1.0.0
Date: April 30, 2025
"""

import os
import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
from pathlib import Path

# Third-party imports
import chainlit as cl
from azure.ai.projects.models import (
    CodeInterpreterTool, 
    OpenApiTool, 
    OpenApiAnonymousAuthDetails
)
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.functions import kernel_function
from pydantic import BaseModel, Field, validator
from azure.identity import DefaultAzureCredential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
OPENAPI_DIR = Path("openapi/mypetparlorapp")
AGENT_MODEL = os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")

# Environment validation
if not AGENT_MODEL:
    raise EnvironmentError("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME environment variable is not set")

# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------

class Booking(BaseModel):
    """Data model representing a pet care booking."""
    id: str
    date: str
    address: str
    weather: Optional[str] = None
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    
    @validator('date')
    def validate_date_format(cls, v):
        """Ensure date is in YYYY-MM-DD format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

class Schedule(BaseModel):
    """Data model representing a daily schedule with multiple bookings."""
    total_distance: Optional[float] = Field(None, description="Total distance in kilometers")
    total_duration: Optional[float] = Field(None, description="Total duration in minutes")
    bookings: List[Booking] = Field(default_factory=list, description="List of bookings in the schedule")

class AuthSettings(BaseModel):
    """Data model for API authentication settings."""
    queryParameters: Dict[str, str] = Field(default_factory=dict)
    headerParameters: Dict[str, str] = Field(default_factory=dict)

# -----------------------------------------------------------------------------
# Plugin Classes
# -----------------------------------------------------------------------------

class SchedulingPlugin:
    """Plugin for creating and optimizing schedules for pet care providers."""
    
    @kernel_function(name="create_schedule", description="Creates and optimizes schedules for pet care visits")
    def create_schedule(self, request: str) -> str:
        """
        Creates an optimized schedule based on the request.
        
        Args:
            request: A string containing schedule requirements
            
        Returns:
            JSON string representation of the optimized schedule
        """
        # TODO: Replace with actual scheduling optimization logic
        # This is just a placeholder implementation
        schedule = Schedule(
            total_distance=15.5,
            total_duration=120,
            bookings=[
                Booking(
                    id="booking1",
                    date="2024-03-20",
                    address="123 Main St",
                    weather="Sunny",
                    arrival_time="09:00",
                    departure_time="10:00"
                ),
                Booking(
                    id="booking2",
                    date="2024-03-20",
                    address="456 Oak Ave",
                    weather="Cloudy",
                    arrival_time="11:00",
                    departure_time="12:30"
                )
            ]
        )
        return schedule.model_dump_json()

class ImporterPlugin:
    """Plugin for importing and processing files like customer lists or booking data."""
    
    @kernel_function(name="import_file", description="Imports and processes files for MyPetParlor App")
    async def import_file(self, file_path: str, file_type: str) -> str:
        """
        Imports and processes a file.
        
        Args:
            file_path: Path to the file
            file_type: Type of the file (csv, excel, etc.)
            
        Returns:
            Status message about the processing result
        """
        # TODO: Replace with actual file processing logic
        # This is just a placeholder implementation
        logger.info(f"Processing file: {file_path} of type {file_type}")
        return f"Successfully processed {file_path} of type {file_type}"

# -----------------------------------------------------------------------------
# API Tool Factory Functions
# -----------------------------------------------------------------------------

def load_openapi_spec(api_name: str) -> dict:
    """
    Load OpenAPI specification from JSON file.
    
    Args:
        api_name: Name of the API (e.g., 'booking', 'customer')
        
    Returns:
        Dictionary containing the OpenAPI specification
    """
    spec_path = OPENAPI_DIR / api_name / "swagger.json"
    if not spec_path.exists():
        raise FileNotFoundError(f"OpenAPI spec not found at {spec_path}")
        
    with open(spec_path, "r") as f:
        return json.load(f)

def create_api_tool(api_name: str, description: str) -> OpenApiTool:
    """
    Create an OpenAPI tool for the specified API.
    
    Args:
        api_name: Name of the API (e.g., 'booking', 'customer')
        description: Detailed description of the API functionality
        
    Returns:
        Configured OpenApiTool instance
    """
    spec = load_openapi_spec(api_name)
    auth = OpenApiAnonymousAuthDetails()
    
    return OpenApiTool(
        name=f"{api_name}_api",
        spec=spec,
        description=description,
        auth=auth
    )

# -----------------------------------------------------------------------------
# Agent Factory Functions 
# -----------------------------------------------------------------------------

async def create_agent(client: Any, name: str, description: str, 
                      instructions: str, tools: Optional[List] = None) -> Any:
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
    # Enhance instructions with better response guidance
    enhanced_instructions = f"""
    {instructions}
    
    IMPORTANT RESPONSE GUIDELINES:
    1. Always provide complete, self-contained responses that directly address the user's query
    2. Use clear structure with headings and sections for complex information
    3. When analyzing data, include specific findings, patterns, and business implications
    4. Always synthesize information rather than just listing facts
    5. Never respond with just a question without providing substantive information
    6. Avoid echoing back the user's question without adding value
    """
    
    agent_args = {
        "model": AGENT_MODEL,
        "name": name,
        "description": description,
        "instructions": enhanced_instructions
    }
    
    if tools:
        agent_args["tools"] = tools
        
    return await client.agents.create_agent(**agent_args)

# -----------------------------------------------------------------------------
# API Description Constants
# -----------------------------------------------------------------------------

BOOKING_API_DESC = """Expert on MyPetParlor App Booking API (OpenAPI 3.1).
Manages booking resources that belong to customers and teams.
Note that all monetary values are stored in cents (integers). For example, 1000 cents = 10.00 ZAR.

Key capabilities:
- Get/search bookings with filtering by customer, employee, state, date, team
- Create single or recurring bookings with customer details and services
- View booking details including customer info, pet details, status
- Update booking information and reschedule appointments
- Change transportation modes and apply vouchers/discounts
- Manage booking messages, notes, and service orders
- Handle accounting system integration
- Delete bookings individually or in batches
"""

CUSTOMER_API_DESC = """Expert on MyPetParlor App Customer API (OpenAPI 3.1).
Manages customer resources belonging to tenants with team associations.

Key capabilities:
- Get/search customers with pagination and team filtering
- Create customers with contact info, profiles, team associations
- Send email invitations during customer creation
- View customer details by ID or UID
- Update customer information and profile settings
- Manage payment flags, profile images, and accounting links
- Add/remove team associations
- Delete customer records
- Support Gravatar integration
- Handle multi-team customer relationships
"""

DOCUMENT_API_DESC = """Expert on MyPetParlor App Document API (OpenAPI 3.1).
Manages legal documents for tenants, profiles, or teams.

Document types: refund_policy, terms
Reference types: organisation, profile, team

Key capabilities:
- Get documents with type/reference filtering
- Create documents with content and references
- Retrieve documents by ID or reference
- Update document content and metadata
- Generate refund policies and terms based on business details
- Delete documents
- Support pagination for multiple documents
- Manage document relationships across entities
"""

TEAM_API_DESC = """Expert on MyPetParlor App Team API (OpenAPI 3.1).
Manages team resources belonging to tenants.

Key capabilities:
- Get/search teams with pagination and filtering
- Create teams with coat types, payment, scheduling configurations
- Set default team properties
- View team details by ID
- Update team properties while preserving configuration
- Delete team records
- Support Gravatar integration
- Configure payment precedence and booking schedules
- Manage team types (e.g., mobile teams with timeblock scheduling)
"""

TENANT_API_DESC = """Expert on MyPetParlor App Tenant API (OpenAPI 3.1).
Manages tenant resources (parent of all other resources).

Key capabilities:
- Get tenants with pagination and filtering
- Create tenants with payment, scheduling, application settings
- View tenant details by ID or unique identifier
- Update tenant properties and configurations
- Delete tenant records
- Disable specific payment methods
- Link cloud resources (Azure, Google Cloud)
- Configure coat requirements and booking advance time
- Manage third-party integrations like Xero
"""

SETUP_GUIDE_INSTRUCTIONS = """You are an expert in guiding new and existing users of the MyPetParlor App portal.

Follow this structured approach to help users set up their portal:

1. User Setup Guide:
   - Create user account and login
   - Set user email and password
   - Configure user preferences

2. Organization Setup Guide:
   - Create organization profile
   - Set organization name
   - Configure organization settings
   - Set organization address
   - Setup organization operating hours
   - Configure organization service area

3. Profile Setup Guide:
   - Create staff profile
   - Set staff name
   - Configure staff role
   - Set staff email
   - Set staff phone number
   - Configure staff schedule
   - Set staff service area

4. Team Setup Guide:
   - Create team profile
   - Set team name
   - Configure team settings
   - Set team service area
   - Configure team schedule
   - Set team operating hours
   - Configure team members

5. Customer Setup Guide (Optional):
   - Create customer profiles
   - Set customer names
   - Configure customer preferences
   - Set customer addresses
   - Configure customer pets
   - Set customer contact info
   - Configure customer billing
   - Set customer notes

6. Booking Setup Guide (Optional):
   - Configure booking settings
   - Set booking durations
   - Configure booking types
   - Set booking prices
   - Configure booking notifications
   - Set booking restrictions
   - Configure booking cancellation policy
   - Set booking reminders

Important Guidelines:
- Guides 1-4 (User, Organization, Profile, Team) are REQUIRED and must be completed in order
- Guides 5-6 (Customer, Booking) are OPTIONAL but recommended for full functionality
- Use the MyPetParlorAppOpenAPIAgent to verify setup status and configuration
- Guide users through each section systematically, ensuring all required fields are completed
- Provide clear explanations and examples for each setup step
- Verify completion of each guide before moving to the next
- Help troubleshoot any issues that arise during setup"""

TRIAGE_INSTRUCTIONS = f"""You are the main coordinator for the MyPetParlor AI Assistant. Your role is to properly route and synthesize information from specialized agents.

When evaluating user requests, follow this process:

1. IDENTIFY THE REQUEST TYPE - Carefully analyze what the user is asking for:
   - For setup/guide questions → Use SetupGuideAgent
   - For customer-related queries → Use CustomerAPIAgent
   - For document-related queries → Use DocumentAPIAgent
   - For team-related queries → Use TeamAPIAgent
   - For tenant-related queries → Use TenantAPIAgent
   - For booking-related queries → Use BookingAPIAgent
   - For general questions, respond directly

2. AGENT CONSULTATION PROCESS:
   - Call the appropriate specialized agent(s) with a clear, specific question
   - Wait for the complete response from each specialized agent
   - If the response is insufficient, ask follow-up questions to the same agent

3. SYNTHESIS AND RESPONSE:
   - CRITICALLY IMPORTANT: Do NOT simply repeat or forward what the specialized agent said
   - Do NOT respond with just a question or acknowledgment
   - Always synthesize the information from specialized agents into a complete, coherent answer
   - Always provide a substantive response that directly addresses the user's query
   - Structure your response logically with clear sections if appropriate
   - Include relevant data, insights, and recommendations when applicable

For data analysis requests specifically:
- When users request trend analysis or data insights, always provide a substantive analysis
- Include observations about patterns, anomalies, and potential causation
- Present quantitative information clearly and interpret what it means for the business

Remember: Your value is in providing complete, synthesized answers that integrate specialized knowledge. Never return just the user's question or a simple acknowledgment. If you do not have any information to provide, just say so."""

# -----------------------------------------------------------------------------
# ChainLit Event Handlers
# -----------------------------------------------------------------------------

@cl.on_chat_start
async def start():
    """
    Initialize chat session with Azure AI Agent when a user starts a new chat.
    This sets up all necessary agents and tools.
    """
    logger.info("Starting new chat session")
    
    try:
        # Send a welcome message to the user
        await cl.Message(
            content="👋 Welcome to MyPetParlor Assistant! How can I help you today?",
        ).send()

        # Initialize Azure credentials
        credential = DefaultAzureCredential()
        
        # Create Azure AI Agent client
        client = AzureAIAgent.create_client(credential=credential)
        
        # Create common tools
        code_interpreter = CodeInterpreterTool()
        
        # Create API tools with proper descriptions
        booking_api = create_api_tool("booking", BOOKING_API_DESC)
        customer_api = create_api_tool("customer", CUSTOMER_API_DESC)
        document_api = create_api_tool("document", DOCUMENT_API_DESC)
        team_api = create_api_tool("team", TEAM_API_DESC)
        tenant_api = create_api_tool("tenants", TENANT_API_DESC)
        
        # Create specialized agent definitions
        logger.info("Creating specialized agent definitions")
        
        # Setup guide agent - helps users navigate the setup process
        setup_guide_definition = await create_agent(
            client=client,
            name="setup_guide",
            description="A setup guide specialist that helps users set up their MyPetParlor App portal",
            instructions=SETUP_GUIDE_INSTRUCTIONS
        )
        
        # API-specific agents - each specializes in one API domain
        booking_api_definition = await create_agent(
            client=client,
            name="booking_api",
            description="An expert in the MyPetParlor App Booking API",
            instructions="You are a data expert with access to the MyPetParlor App Booking API and the Code Interpreter tool for data analysis.",
            tools=booking_api.definitions + code_interpreter.definitions
        )
        
        customer_api_definition = await create_agent(
            client=client,
            name="customer_api",
            description="An expert in the MyPetParlor App Customer API",
            instructions="You are a data expert with access to the MyPetParlor App Customer API and the Code Interpreter tool for data analysis.",
            tools=customer_api.definitions + code_interpreter.definitions
        )
        
        document_api_definition = await create_agent(
            client=client,
            name="document_api",
            description="An expert in the MyPetParlor App Document API",
            instructions="You are a data expert with access to the MyPetParlor App Document API and the Code Interpreter tool for data analysis.",
            tools=document_api.definitions + code_interpreter.definitions
        )
        
        team_api_definition = await create_agent(
            client=client,
            name="team_api",
            description="An expert in the MyPetParlor App Team API",
            instructions="You are a data expert with access to the MyPetParlor App Team API and the Code Interpreter tool for data analysis.",
            tools=team_api.definitions + code_interpreter.definitions
        )
        
        tenant_api_definition = await create_agent(
            client=client,
            name="tenant_api",
            description="An expert in the MyPetParlor App Tenant API",
            instructions="You are a data expert with access to the MyPetParlor App Tenant API and the Code Interpreter tool for data analysis.",
            tools=tenant_api.definitions + code_interpreter.definitions
        )

        data_analysis_definition = await create_agent(
            client=client,
            name="data_analysis",
            description="An expert in analyzing data",
            instructions="You are an expert in analyzing data who can use the Code Interpreter tool to run queries and analysis on the data.",
            tools=code_interpreter.definitions
        )
        
        # Triage agent - orchestrates between specialized agents
        triage_definition = await create_agent(
            client=client,
            name="triage",
            description="Main coordinator that routes requests to specialized agents",
            instructions=TRIAGE_INSTRUCTIONS
        )
        
        # Create agent instances with their plugins
        logger.info("Initializing agent instances")
        
        # Create plugins
        scheduling_plugin = SchedulingPlugin()
        importer_plugin = ImporterPlugin()

        setup_guide_agent = AzureAIAgent(
            client=client,
            definition=setup_guide_definition
        )

        data_analysis_agent = AzureAIAgent(
            client=client,
            definition=data_analysis_definition
        )
        
        booking_api_agent = AzureAIAgent(
            client=client, 
            definition=booking_api_definition,
            plugins=[scheduling_plugin, data_analysis_agent]
        )
        
        customer_api_agent = AzureAIAgent(
            client=client,
            definition=customer_api_definition,
            plugins=[importer_plugin, data_analysis_agent]
        )
        
        document_api_agent = AzureAIAgent(
            client=client,
            definition=document_api_definition,
            plugins=[data_analysis_agent]
        )
        
        team_api_agent = AzureAIAgent(
            client=client,
            definition=team_api_definition,
            plugins=[data_analysis_agent]
        )
        
        tenant_api_agent = AzureAIAgent(
            client=client,
            definition=tenant_api_definition,
            plugins=[data_analysis_agent]
        )
        
        # Main triage agent with all specialized agents as plugins
        triage_agent = AzureAIAgent(
            client=client,
            definition=triage_definition,
            plugins=[
                setup_guide_agent, 
                customer_api_agent, 
                document_api_agent, 
                team_api_agent, 
                tenant_api_agent, 
                booking_api_agent
            ]
        )
        
        # Create a new thread for the chat session
        thread = AzureAIAgentThread(client=client)
        
        # Add Chainlit filter to capture function calls as Steps
        sk_filter = cl.SemanticKernelFilter(kernel=triage_agent.kernel)
        
        # Run a copilot function call to obtain the authentication object
        logger.info("Retrieving authentication settings")
        fn = cl.CopilotFunction(name="get_copilot_auth_settings", args={})
        auth_settings = await fn.acall()
        
        # Store session variables - including client for proper cleanup
        cl.user_session.set("auth_settings", auth_settings)
        cl.user_session.set("client", client)
        cl.user_session.set("triage_agent", triage_agent)
        cl.user_session.set("thread", thread)
        
    except Exception as e:
        logger.error(f"Error initializing chat session: {str(e)}", exc_info=True)
        await cl.Message(
            content="❌ Error initializing the assistant. Please try refreshing the page or contact support.",
        ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming messages using Azure AI Agent.
    
    Args:
        message: The message received from the user
    """
    logger.info(f"Processing new message: {message.id}")
    
    try:
        # Retrieve session variables
        triage_agent: AzureAIAgent = cl.user_session.get("triage_agent")
        thread: AzureAIAgentThread = cl.user_session.get("thread")
        auth_settings: dict = cl.user_session.get("auth_settings")
        
        if not all([triage_agent, thread, auth_settings]):
            raise ValueError("Session data is missing. Please restart the chat.")
        
        # Create a thinking message to indicate processing
        thinking_msg = cl.Message(content="🧠 Analyzing your request...", author="System")
        await thinking_msg.send()
        
        # Create a structured system message with authentication details
        system_message = create_system_message(message.content, auth_settings)
        
        # Create a response orchestration message to ensure proper synthesis
        orchestration_message = system_message + """
        <response_requirements>
        1. IMPORTANT: You MUST synthesize a complete response that directly answers the user's question.
        2. Do NOT simply ask a question back to the user or acknowledge their request without providing information.
        3. If analyzing data or trends, provide substantive insights with observations about patterns and business implications.
        4. Structure your response in a clear, logical manner with appropriate sections.
        5. Include specific data points when relevant to support your analysis.
        </response_requirements>
        """
        
        # Add user message to thread
        logger.info("Sending message to agents for processing")
        thread_response = await triage_agent.get_response(
            thread=thread,
            messages=[orchestration_message]
        )
        
        # Delete the thinking message
        await thinking_msg.remove()
        
        # Check if we got a valid response
        if not thread_response or not thread_response.content:
            logger.warning("Empty response received from agent")
            await cl.Message(
                content="I couldn't generate a proper response. Could you please rephrase your question?",
            ).send()
            return
            
        # Create a Chainlit message for the response stream
        answer = cl.Message(content="")
        
        # Stream the response (with additional check to avoid echoing the question)
        async for content in triage_agent.invoke_stream(thread=thread):
            if content.content:
                content_text = content.content.content if hasattr(content.content, 'content') else content.content
                
                # Skip if the content matches the user's question too closely
                if is_echo_of_question(content_text, message.content):
                    logger.warning("Detected echo of user question, skipping")
                    continue
                    
                # Try to parse as schedule data
                try:
                    schedule_data = parse_schedule_data(content_text)
                    if schedule_data:
                        await send_schedule_message(schedule_data)
                        continue
                except Exception as e:
                    logger.debug(f"Not schedule data, streaming regular content: {str(e)}")
                
                # Regular content, stream token by token
                await answer.stream_token(content_text)
        
        # Send the final message if not already sent and not empty
        if answer.content and not is_echo_of_question(answer.content, message.content):
            await answer.send()
        else:
            # Fallback if we somehow got an empty or echo response
            await cl.Message(
                content="I processed your request but couldn't generate a proper response. Please try a more specific question about bookings, customers, teams, or setup guides.",
            ).send()
            
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        await cl.Message(
            content=f"❌ Error: {str(e)}. Please try again or contact support if the issue persists.",
        ).send()

@cl.on_chat_end
async def end():
    """
    Clean up resources when chat ends to prevent memory leaks and ensure proper resource disposal.
    """
    logger.info("Ending chat session and cleaning up resources")
    try:
        # Get the client from the session
        client = cl.user_session.get("client")
        if client:
            # Close the client properly to release resources
            await client.close()
            logger.info("Azure AI Agent client closed successfully")
    except Exception as e:
        logger.error(f"Error closing client during chat end: {str(e)}", exc_info=True)

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def create_system_message(user_content: str, auth_settings: dict) -> str:
    """
    Create a structured system message with user content and authentication details.
    
    Args:
        user_content: The message from the user
        auth_settings: Authentication settings for API access
        
    Returns:
        Formatted system message string
    """
    # Extract query parameters
    query_params = auth_settings.get('queryParameters', {})
    firebase_token = query_params.get('firebaseIdToken', '')
    
    # Extract header parameters
    header_params = auth_settings.get('headerParameters', {})
    app_id = header_params.get('x-mba-application-id', '')
    app_type = header_params.get('x-mba-application-type', '')
    deploy_location = header_params.get('x-mba-deployment-location', '')
    subscription_key = header_params.get('ocp-apim-subscription-key', '')

    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"""
    <user_message>
    {user_content}
    </user_message>
    
    <current_date_time>
    The current date and time is {current_date_time}. Use this information to provide accurate time-related responses.
    </current_date_time>

    <api_authentication>
    When using OpenAPI tools or other agents used to access the MyPetParlor App APIs, 
    you MUST share and use these authentication parameters through instruction overrides:
    
    Query Parameters:
    - firebaseIdToken: {firebase_token}
    
    Header Parameters:
    - x-mba-application-id: {app_id}
    - x-mba-application-type: {app_type}
    - x-mba-deployment-location: {deploy_location}
    - ocp-apim-subscription-key: {subscription_key}
    </api_authentication>
    """

def is_echo_of_question(response: str, question: str) -> bool:
    """
    Check if the response is just echoing the user's question.
    
    Args:
        response: The response text to check
        question: The original question from the user
        
    Returns:
        True if the response appears to be an echo of the question, False otherwise
    """
    # Strip punctuation and whitespace for comparison
    import re
    
    def normalize_text(text):
        # Convert to lowercase, remove extra whitespace and punctuation
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    norm_response = normalize_text(response)
    norm_question = normalize_text(question)
    
    # Check if the response is just the question or starts with it
    if norm_response == norm_question:
        return True
    
    # Check if response is mostly just the question with some minor additions
    if norm_response.startswith(norm_question) and len(norm_response) < len(norm_question) + 20:
        return True
        
    # Check if response is just asking a clarifying question without providing information
    clarification_patterns = [
        r"^can you (clarify|explain|elaborate|specify|provide more details)",
        r"^(what|which|how|when|where|why) (exactly|specifically|precisely)",
        r"^(do you want|are you looking for|would you like)",
        r"^(could you|can you) (please |)?(clarify|explain|elaborate)"
    ]
    
    for pattern in clarification_patterns:
        if re.match(pattern, norm_response):
            return True
    
    return False

def parse_schedule_data(content: Any) -> Optional[Schedule]:
    """
    Try to parse content as Schedule data.
    
    Args:
        content: Content to parse
        
    Returns:
        Schedule object if parsing succeeds, None otherwise
    """
    try:
        # Handle different content formats from agents
        content_str = content
        if hasattr(content, 'content'):
            content_str = content.content
            
        schedule_data = Schedule.model_validate_json(content_str)
        return schedule_data
    except Exception:
        return None

async def send_schedule_message(schedule_data: Schedule) -> None:
    """
    Send a formatted message with schedule data.
    
    Args:
        schedule_data: Schedule data to display
    """
    elements = []
    
    # Add metrics if available
    if schedule_data.total_distance is not None:
        elements.append(
            cl.Text(name="metrics", content=f"""
            📊 Route Metrics:
            🚗 Total Distance: {schedule_data.total_distance} km
            ⏱️ Total Duration: {schedule_data.total_duration} minutes
            """)
        )
    
    # Add each booking as a separate element
    for booking in schedule_data.bookings:
        elements.append(
            cl.Text(name=booking.id, content=f"""
            📅 Date: {booking.date}
            📍 Location: {booking.address}
            🌤️ Weather: {booking.weather or 'N/A'}
            🕒 Arrival: {booking.arrival_time or 'N/A'}
            🕕 Departure: {booking.departure_time or 'N/A'}
            """)
        )
    
    # Send as a rich message with elements
    await cl.Message(
        content="Here's your optimized schedule:",
        elements=elements
    ).send()

# -----------------------------------------------------------------------------
# Main entry point (for direct execution)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    logger.warning("This file should be run via Chainlit, not directly")