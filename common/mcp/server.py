"""
MCP Server implementation for MyBusiness App API.
"""
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

class MCPServer:
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.app = FastAPI(title="MyBusiness App MCP Server")
        self.setup_routes()

    def setup_routes(self):
        """Setup API routes based on swagger definition."""
        @self.app.get("/bookings")
        async def get_bookings(start_date: str, end_date: str) -> Dict[str, Any]:
            """Get bookings for a date range."""
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/bookings",
                    params={"start_date": start_date, "end_date": end_date},
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail=response.text)
                return response.json()

        @self.app.post("/bookings")
        async def create_booking(booking: Dict[str, Any]) -> Dict[str, Any]:
            """Create a new booking."""
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/bookings",
                    json=booking,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                if response.status_code != 201:
                    raise HTTPException(status_code=response.status_code, detail=response.text)
                return response.json()

    def run(self, host: str = "0.0.0.0", port: int = 8002):
        """Run the MCP server."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)