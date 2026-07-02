"""
LLM client for LockIn AI.

Unified client for OpenAI, Anthropic, and Google LLMs with function calling support.
"""

from typing import List, Dict, Any, Callable
import json
from app.config import settings


class LLMClient:
    """Unified LLM client with function calling support."""
    
    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider (openai, anthropic, google)
            model: Model name
            api_key: API key
        """
        self.provider = provider or settings.llm_provider
        self.model = model or settings.default_model
        self.api_key = api_key or settings.api_key
        
        if not self.api_key:
            raise ValueError(f"No API key found for provider: {self.provider}")
        
        self._client = self._initialize_client()
    
    def _initialize_client(self) -> Any:
        """Initialize the appropriate LLM client based on provider."""
        if self.provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=self.api_key)
        
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            return Anthropic(api_key=self.api_key)
        
        elif self.provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            return genai
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Send a chat request with optional function calling.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool/function definitions
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Response dict with 'content', 'tool_calls', and 'usage'
        """
        if self.provider == "openai":
            return self._chat_openai(messages, tools, temperature, max_tokens)
        elif self.provider == "anthropic":
            return self._chat_anthropic(messages, tools, temperature, max_tokens)
        elif self.provider == "google":
            return self._chat_google(messages, tools, temperature, max_tokens)
    
    def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] | None,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """OpenAI chat completion."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if tools:
            kwargs["tools"] = [{"type": "function", "function": tool} for tool in tools]
            kwargs["tool_choice"] = "auto"
        
        response = self._client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        
        result = {
            "content": message.content,
            "tool_calls": [],
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }
        }
        
        if message.tool_calls:
            for tool_call in message.tool_calls:
                result["tool_calls"].append({
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                })
        
        return result
    
    def _chat_anthropic(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] | None,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Anthropic chat completion."""
        # Extract system message
        system = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_messages.append(msg)
        
        kwargs = {
            "model": self.model,
            "messages": user_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if system:
            kwargs["system"] = system
        
        if tools:
            kwargs["tools"] = tools
        
        response = self._client.messages.create(**kwargs)
        
        result = {
            "content": None,
            "tool_calls": [],
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        }
        
        for block in response.content:
            if block.type == "text":
                result["content"] = block.text
            elif block.type == "tool_use":
                result["tool_calls"].append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": block.input
                })
        
        return result
    
    def _chat_google(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] | None,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Google Gemini chat completion."""
        model = self._client.GenerativeModel(self.model)
        
        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_messages.append({
                "role": role,
                "parts": [msg["content"]]
            })
        
        # Note: Gemini function calling format is different
        # For simplicity, we'll use basic chat without tools for now
        # Full implementation would require converting tool schemas
        
        chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
        response = chat.send_message(
            gemini_messages[-1]["parts"][0],
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
        )
        
        return {
            "content": response.text,
            "tool_calls": [],
            "usage": {
                "input_tokens": 0,  # Gemini doesn't provide token counts easily
                "output_tokens": 0,
            }
        }


# Global client instance
def get_llm_client() -> LLMClient:
    """Get configured LLM client instance."""
    return LLMClient()
