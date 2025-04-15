"""
Chainlit frontend for MyPetParlor AI Agents.
"""
import chainlit as cl
from chainlit.types import AskFileResponse
import httpx
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@cl.on_chat_start
async def start():
    """Initialize chat session."""
    logger.info("Starting new chat session")
    
    backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
    logger.info(f"Using backend URL: {backend_url}")
    cl.user_session.set("backend_url", backend_url)
    
    # Get available agents from backend
    logger.info("Fetching available agents from backend")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{backend_url}/agents")
            response.raise_for_status()
            agents = response.json()["agents"]
            logger.info(f"Available agents: {agents}")
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}", exc_info=True)
        await cl.Message(content="❌ Error: Could not fetch available agents. Using default agent.").send()
        agents = ["azure_smart_scheduling"]
    
    # Let user select agent type
    logger.info("Prompting user to select agent type")
    try:
        agent_type = await cl.AskActionMessage(
            content="Please select an agent to help you:",
            actions=[
                cl.Action(name="azure", value="azure_smart_scheduling", label="Azure Smart Scheduling", payload={"type": "azure"})
            ]
        ).send()
        
        if not agent_type:
            # If no agent was selected, use default
            logger.info("No agent selected, using default")
            cl.user_session.set("agent_type", "azure_smart_scheduling")
            await cl.Message(
                content="You're now chatting with the Azure Smart Scheduling agent. How can I help you?"
            ).send()
        else:
            selected_type = agent_type.get("value", "azure_smart_scheduling")
            selected_label = agent_type.get("label", "Azure Smart Scheduling")
            logger.info(f"User selected agent: {selected_type} ({selected_label})")
            cl.user_session.set("agent_type", selected_type)
            await cl.Message(
                content=f"You're now chatting with the {selected_label} agent. How can I help you?"
            ).send()
    except Exception as e:
        logger.error(f"Error during agent selection: {str(e)}", exc_info=True)
        await cl.Message(content="❌ Error during agent selection. Please try again.").send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    logger.info("Processing new message")
    logger.debug(f"Message content: {message.content}")
    
    try:
        # Send request to backend with agent type
        backend_url = cl.user_session.get('backend_url')
        agent_type = cl.user_session.get("agent_type")
        logger.info(f"Sending request to backend ({backend_url}) with agent type: {agent_type}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_url}/chat",
                json={
                    "message": message.content,
                    "agent_type": agent_type
                }
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Backend response: {result}")

        # Handle different response types
        if result.get("status") == "failed":
            error_msg = result.get('error', 'Unknown error occurred')
            logger.error(f"Backend returned error: {error_msg}")
            await cl.Message(
                content=f"❌ Error: {error_msg}",
            ).send()
            return

        if "schedule" in result:
            logger.info("Processing schedule response")
            # Create schedule display
            schedule = result["schedule"]
            elements = []
            
            # Add route optimization metrics if available
            if "total_distance" in schedule:
                logger.info(f"Route metrics - Distance: {schedule['total_distance']}km, Duration: {schedule['total_duration']}min")
                elements.append(
                    cl.Text(name="metrics", content=f"""
                    📊 Route Metrics:
                    🚗 Total Distance: {schedule['total_distance']} km
                    ⏱️ Total Duration: {schedule['total_duration']} minutes
                    """)
                )
            
            # Add bookings
            logger.info(f"Processing {len(schedule['bookings'])} bookings")
            for booking in schedule["bookings"]:
                logger.debug(f"Processing booking: {booking}")
                elements.append(
                    cl.Text(name=booking["id"], content=f"""
                    📅 Date: {booking['date']}
                    📍 Location: {booking['address']}
                    🌤️ Weather: {booking.get('weather', 'N/A')}
                    🕒 Arrival: {booking.get('arrival_time', 'N/A')}
                    🕕 Departure: {booking.get('departure_time', 'N/A')}
                    """)
                )
            
            await cl.Message(
                content="Here's your optimized schedule:",
                elements=elements
            ).send()
            logger.info("Successfully sent schedule response")
        else:
            # Regular message response
            logger.info("Sending regular message response")
            await cl.Message(
                content=result.get("response", "No response from agent"),
                status=result.get("status", "completed")
            ).send()

    except httpx.HTTPError as e:
        logger.error(f"HTTP error communicating with backend: {str(e)}", exc_info=True)
        await cl.Message(
            content=f"❌ Connection Error: Could not reach the backend server. Please try again later.\nDetails: {str(e)}",
        ).send()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        await cl.Message(
            content=f"❌ Error: {str(e)}",
        ).send()