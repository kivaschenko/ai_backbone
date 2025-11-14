"""
Base Agent Class
Foundation for all specialized AI agents.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all AI agents."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        llm_config: Dict[str, Any],
        memory_limit: int = 10,
    ):
        """
        Initialize base agent.

        Args:
            agent_id: Unique agent identifier
            name: Human-readable agent name
            llm_config: LLM configuration (model, api_key, etc.)
            memory_limit: Maximum number of messages to keep in memory
        """
        self.agent_id = agent_id
        self.name = name
        self.llm_config = llm_config
        self.memory_limit = memory_limit

        self.memory: List[Dict[str, Any]] = []
        self.tools: Dict[str, Any] = {}

    def add_to_memory(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """
        Add a message to agent memory.

        Args:
            role: Message role (system, user, assistant)
            content: Message content
            metadata: Additional metadata
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        self.memory.append(message)

        # Trim memory if exceeds limit
        if len(self.memory) > self.memory_limit:
            self.memory = self.memory[-self.memory_limit :]

    def clear_memory(self):
        """Clear agent memory."""
        self.memory = []
        logger.info(f"Memory cleared for agent: {self.name}")

    def register_tool(self, tool_name: str, tool_func: Any):
        """
        Register a tool for the agent to use.

        Args:
            tool_name: Name of the tool
            tool_func: Tool function or callable
        """
        self.tools[tool_name] = tool_func
        logger.info(f"Tool registered for {self.name}: {tool_name}")

    def call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """
        Call the LLM with a prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            LLM response
        """
        # This is a placeholder. In real implementation, this would call
        # OpenAI, Anthropic, or other LLM APIs
        logger.info(f"Agent {self.name} calling LLM")

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add memory context
        messages.extend(self.memory[-5:])  # Last 5 messages for context

        # Add current prompt
        messages.append({"role": "user", "content": prompt})

        # TODO: Implement actual LLM call
        # response = openai.ChatCompletion.create(
        #     model=self.llm_config["model"],
        #     messages=messages,
        #     temperature=self.llm_config.get("temperature", 0.7)
        # )

        response_text = "LLM Response placeholder"

        # Add to memory
        self.add_to_memory("user", prompt)
        self.add_to_memory("assistant", response_text)

        return response_text

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data. To be implemented by subclasses.

        Args:
            input_data: Input data for the agent

        Returns:
            Processed result
        """
        raise NotImplementedError("Subclasses must implement process()")

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent state to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "memory_size": len(self.memory),
            "tools": list(self.tools.keys()),
        }
