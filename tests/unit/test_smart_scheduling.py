"""
Unit tests for Smart Scheduling Agent.
"""
import pytest
from datetime import datetime, timedelta
from agents.azure.smart_scheduling.agent import SmartSchedulingAgent
from azure.ai.agents import AgentConfiguration

@pytest.fixture
def agent():
    config = AgentConfiguration(
        name="test-agent",
        endpoint="http://localhost:8000",
        key="test-key"
    )
    return SmartSchedulingAgent(config)

@pytest.mark.asyncio
async def test_process_request(agent):
    request = {
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    }
    
    result = await agent.process_request(request)
    assert "optimized_schedule" in result
    assert "bookings" in result["optimized_schedule"]
    assert "route" in result["optimized_schedule"]

@pytest.mark.asyncio
async def test_evaluate(agent):
    result = await agent.evaluate()
    assert "metrics" in result
    assert "route_optimization" in result["metrics"]
    assert "weather_consideration" in result["metrics"]
    assert "booking_clustering" in result["metrics"]