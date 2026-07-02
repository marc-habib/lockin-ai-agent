"""
Base tool class for LockIn AI.

Defines the interface that all tools must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    def __init__(self):
        """Initialize the tool."""
        self.name = self._get_name()
        self.description = self._get_description()
        self.parameters = self._get_parameters()
    
    @abstractmethod
    def _get_name(self) -> str:
        """
        Get the tool name.
        
        Returns:
            Tool name
        """
        pass
    
    @abstractmethod
    def _get_description(self) -> str:
        """
        Get the tool description.
        
        Returns:
            Tool description
        """
        pass
    
    @abstractmethod
    def _get_parameters(self) -> Dict[str, Any]:
        """
        Get the tool parameter schema.
        
        Returns:
            Parameter schema dict
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool.
        
        Args:
            **kwargs: Tool parameters
        
        Returns:
            Tool result as dict
        """
        pass
    
    def to_function_schema(self) -> Dict[str, Any]:
        """
        Convert tool to function calling schema.
        
        Returns:
            Function schema dict for LLM
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
