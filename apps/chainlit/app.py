"""
Chainlit frontend for MyPetParlor AI Agents using Azure AI Agent.
"""
import os
import logging
import json
from typing import Optional, List
from datetime import datetime
import chainlit as cl
from azure.ai.projects.models import CodeInterpreterTool, OpenApiTool, OpenApiAnonymousAuthDetails
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.functions import kernel_function
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data models for structured output
class Booking(BaseModel):
    id: str
    date: str
    address: str
    weather: Optional[str]
    arrival_time: Optional[str]
    departure_time: Optional[str]

class Schedule(BaseModel):
    total_distance: Optional[float]
    total_duration: Optional[float]
    bookings: List[Booking]

# Specialized plugins for each agent
class SchedulingPlugin:
    @kernel_function(name="create_schedule", description="Creates and optimizes schedules")
    def create_schedule(self, request: str) -> str:
        """Creates an optimized schedule based on the request."""
        # Placeholder implementation - replace with actual scheduling logic
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
                )
            ]
        )
        return schedule.model_dump_json()

class ImporterPlugin:
    @kernel_function(name="import_file", description="Imports and processes files")
    async def import_file(self, file_path: str, file_type: str) -> str:
        """Imports and processes a file."""
        # Placeholder implementation - replace with actual file processing logic
        return f"Successfully processed {file_path} of type {file_type}"

@cl.on_chat_start
async def start():
    """Initialize chat session with Azure AI Agent."""
    logger.info("Starting new chat session")
    
    # Initialize Azure credentials
    credential = DefaultAzureCredential()
    
    # Create Azure AI Agent client - store the client itself
    client = AzureAIAgent.create_client(credential=credential)

    # Access the spec files for OpenAPI tools
    openapi_spec_file_path = "openapi/mypetparlorapp"
    with open(os.path.join(openapi_spec_file_path, "swagger.json")) as file_one:
        openapi_spec_one = json.loads(file_one.read())

    # Create the tools
    code_interpreter = CodeInterpreterTool()
    auth = OpenApiAnonymousAuthDetails()
    openapi_mypetparlor_api = OpenApiTool(
        name="OpenAPIMyPetParlorAppAPIAgent",
        spec=openapi_spec_one,
        description="<description>",
        auth=auth,
    )
    
    # Create specialized agents
    
    setup_guide_definition = await client.agents.create_agent(
        model=os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME"),
        name="SetupGuideAgent",
        description="A setup guide specialist that helps users go through the necessary guides to get their MyPetParlor App portal setup",
        instructions="""You are an expert in guiding new and existing users of the MyPetParlor App portal.

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
    )
    
    mypetparlorapp_api_definition = await client.agents.create_agent(
        model=os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME"),
        name="MyPetParlorAppOpenAPIAgent",
        description="",
        instructions="""You are expert reader of the MyPetParlor App API.""",
        tools=openapi_mypetparlor_api.definitions + code_interpreter.definitions,
        tool_resources=code_interpreter.resources,
    )
    
    triage_definition = await client.agents.create_agent(
        model=os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME"),
        name="TriageAgent",
        description="Main coordinator that routes requests to specialized agents",
        instructions="""You are the main coordinator. Evaluate user requests and:
        1. For setup & guide related queries, use the SetupGuideAgent
        2. Provide complete answers incorporating information from the specialized agents
        3. For general queries, respond directly"""
    )
    
    # Create agent instances with their plugins
    setup_guide_agent = AzureAIAgent(
        client=client,
        definition=setup_guide_definition
    )
    
    mypetparlorapp_api_agent = AzureAIAgent(
        client=client,
        definition=mypetparlorapp_api_definition
    )
    
    triage_agent = AzureAIAgent(
        client=client,
        definition=triage_definition,
        plugins=[setup_guide_agent, mypetparlorapp_api_agent]
    )
    
    # Create a new thread for the chat session
    thread = AzureAIAgentThread(client=client)
    
    # Add Chainlit filter to capture function calls as Steps
    sk_filter = cl.SemanticKernelFilter(kernel=triage_agent.kernel)
    
    # Store in session - including the client
    cl.user_session.set("client", client)
    cl.user_session.set("triage_agent", triage_agent)
    cl.user_session.set("thread", thread)

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages using Azure AI Agent."""
    logger.info("Processing new message")
    
    try:
        triage_agent: AzureAIAgent = cl.user_session.get("triage_agent")
        thread: AzureAIAgentThread = cl.user_session.get("thread")
        
        # Add user message to thread
        await triage_agent.get_response(
            thread=thread,
            messages=[message.content]
        )
        
        # Create a Chainlit message for the response stream
        answer = cl.Message(content="")
        
        # Stream the response
        async for content in triage_agent.invoke_stream(thread=thread):
            if content.content:
                # Check if response contains schedule data
                try:
                    schedule_data = Schedule.model_validate_json(content.content)
                    elements = []
                    
                    if schedule_data.total_distance is not None:
                        elements.append(
                            cl.Text(name="metrics", content=f"""
                            📊 Route Metrics:
                            🚗 Total Distance: {schedule_data.total_distance} km
                            ⏱️ Total Duration: {schedule_data.total_duration} minutes
                            """)
                        )
                    
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
                    
                    await cl.Message(
                        content="Here's your optimized schedule:",
                        elements=elements
                    ).send()
                except:
                    # Not schedule data, stream the token
                    await answer.stream_token(content.content.content)
        
        # Send the final message if not already sent
        if answer.content:
            await answer.send()

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        await cl.Message(
            content=f"❌ Error: {str(e)}",
        ).send()

@cl.on_chat_end
async def end():
    """Clean up resources when chat ends."""
    logger.info("Ending chat session")
    try:
        # Get the client from the session
        client = cl.user_session.get("client")
        if client:
            # Close the client properly
            await client.close()
    except Exception as e:
        logger.error(f"Error closing client: {str(e)}", exc_info=True)