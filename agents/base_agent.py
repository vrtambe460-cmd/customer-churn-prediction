"""Base Agent class for all ML agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Abstract base class for all agents in the churn prediction system."""

    def __init__(self, name: str):
        self.name = name
        self.is_initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the agent with required resources."""
        pass

    @abstractmethod
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task."""
        pass

    def log(self, message: str) -> None:
        """Log agent messages."""
        print(f"[{self.name}] {message}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
