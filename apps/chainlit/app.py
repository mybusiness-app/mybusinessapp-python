"""
MyPetParlor AI Assistant - Chainlit frontend for Azure AI Agents
---
This application provides a chat interface for interacting with specialized Azure AI agents
that help users manage their MyPetParlor App portal through various APIs.

Author: MyBusiness App (Pty) Ltd
"""

import os
import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import asyncio

# Third-party imports
import chainlit as cl
from azure.ai.projects import AIProjectClient
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.functions import kernel_function
from pydantic import BaseModel, Field, validator
from azure.identity import DefaultAzureCredential

# Initialize Azure credentials
credential = DefaultAzureCredential()

# Create Azure AI Agent client
client = AzureAIAgent.create_client(credential=credential)

# Configure logging
logger = logging.getLogger(__name__)

from custom_agents.setup_guide import SetupGuideClient
from custom_agents.read_api import ReadAPIClient
from custom_agents.triage import TriageClient
from telemetry.appinsights import AzureMonitor

# Enable Azure Monitor tracing
async def init_application_insights():
    connection_string = await client.telemetry.get_connection_string()
    if not connection_string:
        print("Application Insights was not enabled for this project.")
        print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
        exit()
    azureMonitor = AzureMonitor(connection_string=connection_string)
    azureMonitor.set_up_logging()
    azureMonitor.set_up_tracing()
    azureMonitor.set_up_metrics()

# Run the initialization
asyncio.run(init_application_insights())

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
            content="👋 Welcome to MyPetParlor AI Assistant! How can I help you today?",
        ).send()
        
        # Initialize specialized clients
        logger.info("Initializing specialized clients")
        setup_guide_client = SetupGuideClient(client=client)
        read_api_client = ReadAPIClient(client=client)
        triage_client = TriageClient(client=client)
        
        # Create plugins
        scheduling_plugin = SchedulingPlugin()
        importer_plugin = ImporterPlugin()
        
        # Initialize agents from clients
        logger.info("Initializing agents from clients")
        setup_guide_agent = await setup_guide_client.initialize()
        api_agents = await read_api_client.initialize(
            scheduling_plugin=scheduling_plugin,
            importer_plugin=importer_plugin
        )
        
        # Initialize triage agent with all plugins
        triage_agent = await triage_client.initialize(
            setup_guide_agent=setup_guide_agent,
            api_agents=api_agents
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
        
        # Add user message to thread
        logger.info("Sending message to agents for processing")
        thread_response = await triage_agent.get_response(
            thread=thread,
            messages=[system_message]
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
        logger.error(f"Error processing the message: {str(e)}", exc_info=True)
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
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    system_message = f"""
    <user_message>
    {user_content}
    </user_message>
    
    <current_date_time>
    {current_date_time}.
    </current_date_time>
 
    <api_authentication>
    You MUST share and use these authentication parameters through instruction overrides:
    {auth_settings}
    </api_authentication>
    """
    logger.info(f"System message: {system_message}")
    return system_message

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