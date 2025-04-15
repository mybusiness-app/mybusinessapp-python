"""
Backend API for MyPetParlor application.
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import logging
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel

from mypetparlorapp.agents.factory import AgentFactory
from mypetparlorapp.agents.base import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="MyPetParlor Backend API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get MCP server URL from environment
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8002")

# Initialize agent factory
agent_factory = AgentFactory()

class ChatMessage(BaseModel):
    message: str
    agent_type: Optional[str] = "azure_smart_scheduling"  # Default to Azure agent

async def get_agent(agent_type: str) -> BaseAgent:
    """Dependency to get agent instance."""
    logger.info(f"Getting agent instance for type: {agent_type}")
    try:
        agent = await agent_factory.get_agent(agent_type)
        if not agent:
            logger.error(f"Agent type '{agent_type}' not supported")
            raise HTTPException(status_code=400, detail=f"Agent type '{agent_type}' not supported")
        logger.info(f"Successfully created agent instance for type: {agent_type}")
        return agent
    except Exception as e:
        logger.error(f"Error creating agent instance: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@app.post("/chat")
async def chat(message: ChatMessage):
    """Handle chat messages using the specified agent."""
    logger.info(f"Processing chat message for agent type: {message.agent_type}")
    logger.debug(f"Message content: {message.message}")
    
    try:
        # Get agent instance
        agent = await get_agent(message.agent_type)
        
        # Process message
        response = await agent.process_message(message.message)
        logger.info("Successfully processed chat message")
        logger.debug(f"Agent response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def list_agents():
    """List available agent types."""
    logger.info("Listing available agent types")
    agents = agent_factory.get_available_agents()
    logger.info(f"Found {len(agents)} available agent types: {agents}")
    return {"agents": agents}

@app.get("/api/bookings")
async def get_bookings(start_date: str, end_date: str):
    """Fetch bookings from MCP server."""
    logger.info(f"Fetching bookings from {start_date} to {end_date}")
    
    async with httpx.AsyncClient() as client:
        try:
            logger.debug(f"Making request to MCP server: {MCP_SERVER_URL}/bookings")
            response = await client.get(
                f"{MCP_SERVER_URL}/bookings",
                params={"start_date": start_date, "end_date": end_date}
            )
            response.raise_for_status()
            bookings = response.json()
            logger.info(f"Successfully fetched {len(bookings)} bookings")
            logger.debug(f"Bookings data: {bookings}")
            return bookings
        except httpx.HTTPError as e:
            logger.error(f"Error fetching bookings from MCP server: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bookings")
async def create_booking(booking: dict):
    """Create a new booking via MCP server."""
    logger.info("Creating new booking")
    logger.debug(f"Booking details: {booking}")
    
    async with httpx.AsyncClient() as client:
        try:
            logger.debug(f"Making request to MCP server: {MCP_SERVER_URL}/bookings")
            response = await client.post(
                f"{MCP_SERVER_URL}/bookings",
                json=booking
            )
            response.raise_for_status()
            result = response.json()
            logger.info("Successfully created booking")
            logger.debug(f"Created booking: {result}")
            return result
        except httpx.HTTPError as e:
            logger.error(f"Error creating booking: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request and response details."""
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Client Host: {request.client.host}")
    logger.info(f"Headers: {request.headers}")
    
    try:
        # Get response
        response = await call_next(request)
        
        # Log response details
        process_time = (time.time() - start_time) * 1000
        logger.info(f"Response: Status {response.status_code}")
        logger.info(f"Process Time: {process_time:.2f}ms")
        
        return response
    except Exception as e:
        # Log any unhandled exceptions
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 