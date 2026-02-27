from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents in the framework"""
    
    def __init__(self, agent_id: str, name: str, description: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.config = config
        self.memory = []  # Short-term memory for conversation context
        self.logs = []  # Agent activity logs
        self.provider = config.get("llm_config", {}).get("provider", "google")
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output"""
        pass
    
    def log(self, message: str, level: str = "INFO"):
        """Log agent activity"""
        log_entry = {
            "agent": self.name,
            "provider": self.provider,
            "message": message,
            "level": level,
            "timestamp": self._get_timestamp()
        }
        self.logs.append(log_entry)
        logger.log(getattr(logging, level), f"{self.name} ({self.provider}): {message}")
    
    def get_memory_context(self, limit: int = 10) -> List[Dict]:
        """Get recent memory for context"""
        return self.memory[-limit:] if self.memory else []
    
    def update_memory(self, entry: Dict[str, Any]):
        """Update agent memory"""
        self.memory.append({
            **entry,
            "timestamp": self._get_timestamp()
        })
        
    def clear_memory(self):
        """Clear agent memory"""
        self.memory = []
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "provider": self.provider,
            "config": self.config
        }