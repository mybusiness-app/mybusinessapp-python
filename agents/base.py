"""
Base agent interface for MyPetParlor agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """Base class for all agents."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent with necessary configurations."""
        pass
    
    @abstractmethod
    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process a message and return a response."""
        pass
    
    @abstractmethod
    async def evaluate(self) -> Dict[str, Any]:
        """Evaluate agent performance."""
        pass 