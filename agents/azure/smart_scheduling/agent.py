"""
Smart Scheduling Agent implementation using Azure AI Projects SDK with Google Route Optimization.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import os
import logging
logging.basicConfig(level=logging.DEBUG)
from google.cloud import optimization_v1
from google.cloud.optimization_v1 import (
    FleetRoutingClient,
    OptimizeToursRequest,
    Shipment,
    Vehicle,
    Location,
)
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential
from mypetparlorapp.agents import user_functions

from ...base import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmartSchedulingAgent(BaseAgent):
    def __init__(self, project_connection_string: str):
        """Initialize the Smart Scheduling Agent.
        
        Args:
            project_connection_string: Azure AI Project connection string
        """
        self.project_connection_string = project_connection_string
        self.project_client = None
        self.fleet_routing_client = None
        self.agent = None
        
        self.system_message = """You are a smart scheduling agent that optimizes routes for MyPetParlor App.
You have the capability to combine reservations with day and date schedules, find optimal travel times between bookings,
and choose dates and times with a weather forecast that is optimal for pet grooming if the date range is within 5 days.
Each booking includes an address that should be used to find optimal travel times between bookings,
prioritizing bookings that are nearby each other to reduce total travel time and fuel costs.
You use Google's Route Optimization API to calculate the most efficient routes between multiple locations."""

    async def initialize(self) -> None:
        """Initialize the agent with necessary configurations."""
        try:
            # Initialize Azure credentials
            credential = DefaultAzureCredential()
            logger.info("Initialized Azure credentials")
            
            # Initialize Azure AI Project client
            self.project_client = AIProjectClient.from_connection_string(
                conn_str=self.project_connection_string,
                credential=credential,
            )
            logger.info("Initialized Azure AI Project client")
            
            # Initialize Google Fleet Routing client
            self.fleet_routing_client = FleetRoutingClient()
            logger.info("Initialized Google Fleet Routing client")
            
            # Create and initialize the agent
            await self.create()
            logger.info("Successfully created and initialized the agent")
            
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to initialize agent: {str(e)}")

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process a message using the agent."""
        return await self.process_request({"message": message})

    async def _optimize_route(self, bookings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize route using Google Route Optimization API."""
        try:
            # Convert bookings to shipments
            shipments = []
            for idx, booking in enumerate(bookings):
                shipments.append(
                    Shipment(
                        pickup=Location(
                            latitude=booking['latitude'],
                            longitude=booking['longitude']
                        ),
                        delivery=Location(
                            latitude=booking['latitude'],
                            longitude=booking['longitude']
                        ),
                        demand_unit_quantities={'time': booking['duration_minutes']},
                        time_windows=[{
                            'start_time': booking['start_time'],
                            'end_time': booking['end_time']
                        }],
                        penalty_cost=1000  # High penalty for missing appointments
                    )
                )

            # Define vehicles (pet groomers)
            vehicles = [
                Vehicle(
                    start_location=Location(
                        # Company headquarters location
                        latitude=float(os.getenv('HQ_LATITUDE')),
                        longitude=float(os.getenv('HQ_LONGITUDE'))
                    ),
                    end_location=Location(
                        latitude=float(os.getenv('HQ_LATITUDE')),
                        longitude=float(os.getenv('HQ_LONGITUDE'))
                    ),
                    capacity_constraints={'time': 480}  # 8-hour workday
                )
            ]

            # Create optimization request
            request = OptimizeToursRequest(
                parent=f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}",
                shipments=shipments,
                vehicles=vehicles,
                optimization_objectives={
                    'minimize_tour_duration': True,
                    'minimize_vehicle_count': True
                }
            )

            # Get optimized routes
            response = self.fleet_routing_client.optimize_tours(request)

            # Process response into a more usable format
            optimized_routes = []
            for tour in response.tours:
                route = {
                    'vehicle_id': tour.vehicle_id,
                    'stops': []
                }
                for stop in tour.stops:
                    route['stops'].append({
                        'location': {
                            'latitude': stop.location.latitude,
                            'longitude': stop.location.longitude
                        },
                        'arrival_time': stop.arrival_time,
                        'departure_time': stop.departure_time,
                        'booking_id': stop.shipment_id
                    })
                optimized_routes.append(route)

            return {
                'status': 'success',
                'routes': optimized_routes,
                'total_distance': response.metrics.total_distance,
                'total_duration': response.metrics.total_duration
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def create(self) -> None:
        """Create and initialize the agent with necessary tools."""
        
        # Create the agent
        self.agent = self.project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="smart-scheduling-agent",
            instructions=self.system_message,
        )

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a scheduling request."""
        try:
            # Create a new thread for this request
            thread = self.project_client.agents.create_thread()
            
            # Add user message to thread
            self.project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=str(request)
            )
            
            # Run the agent
            run = self.project_client.agents.create_and_process_run(
                thread_id=thread.id,
                agent_id=self.agent.id
            )
            
            if run.status == "failed":
                # Check if you got "Rate limit is exceeded.", then you want to get more quota
                return {
                    "error": run.last_error,
                    "status": run.status.value
                }
            
            # Get the agent's response
            messages = self.project_client.agents.list_messages(
                thread_id=thread.id,
                order="asc"
            )

            # Get the last message from the sender
            last_msg = messages.get_last_text_message_by_role("assistant")

            # Delete the agent once done
            # self.project_client.agents.delete_agent(self.agent.id)

            if last_msg is None:
                return {
                    "error": "No response from agent",
                    "status": run.status.value
                }

            # Return the last message from the agent
            return {
                "response": last_msg.text.value,
                "status": run.status.value,
                "agent_id": self.agent.id,
                "thread_id": thread.id,
                "run_id": run.id
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }

    async def evaluate(self) -> Dict[str, Any]:
        """Evaluate agent performance."""
        return {
            "metrics": {
                "route_optimization": "Measures reduction in travel time",
                "weather_consideration": "Tracks bookings rescheduled due to weather",
                "booking_clustering": "Analyzes how well nearby bookings are grouped"
            }
        }