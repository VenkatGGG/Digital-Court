"""
core/gemini_client.py - Gemini API Client

A robust wrapper around Google's Gemini API with:
- System instruction support for persona injection
- Exponential backoff retry logic
- Streaming and non-streaming generation
"""

import time
import random
from typing import Optional, Generator

from google import genai
from google.genai import types

from config.settings import get_settings


class GeminiBrainError(Exception):
    """Custom exception for GeminiBrain-related errors."""
    pass


class GeminiBrain:
    """
    A wrapper class for Google Gemini API that supports persona injection
    via system instructions, automatic retries, and structured output.
    """
    
    def __init__(
        self,
        persona_name: str,
        system_instruction: str,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize a GeminiBrain instance.
        
        Args:
            persona_name: Identifier for this brain (used in logging)
            system_instruction: The system prompt defining this agent's persona
            model_name: Optional override for the Gemini model to use
            api_key: Optional API key (defaults to settings)
        """
        settings = get_settings()
        
        self.persona_name = persona_name
        self.system_instruction = system_instruction
        
        # Get API key
        self._api_key = api_key or settings.gemini_api_key
        if not self._api_key:
            raise GeminiBrainError(
                "GEMINI_API_KEY not found. Set it in your .env file."
            )
        
        # Initialize client
        self.client = genai.Client(api_key=self._api_key)
        
        # Model configuration
        self._model_name = model_name or settings.gemini_model
        self._max_retries = settings.max_retries
        self._base_delay = settings.base_retry_delay
        
        # Chat history for multi-turn
        self._chat_history = []
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate delay with jitter for exponential backoff."""
        delay = self._base_delay * (2 ** attempt)
        jitter = random.uniform(0, 0.5 * delay)
        return delay + jitter
    
    def generate(
        self,
        prompt: str,
        use_chat: bool = False,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a response from the Gemini model.
        
        Args:
            prompt: The user prompt/input
            use_chat: If True, maintains conversation context
            temperature: Optional temperature override
        
        Returns:
            The model's text response
        """
        last_exception = None
        
        for attempt in range(self._max_retries):
            try:
                # Build contents
                if use_chat:
                    self._chat_history.append(
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=prompt)]
                        )
                    )
                    contents = self._chat_history
                else:
                    contents = prompt
                
                # Build config
                config = types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                )
                if temperature is not None:
                    config.temperature = temperature
                
                # API call
                response = self.client.models.generate_content(
                    model=self._model_name,
                    contents=contents,
                    config=config
                )
                
                result_text = response.text
                
                # Update chat history
                if use_chat:
                    self._chat_history.append(
                        types.Content(
                            role="model",
                            parts=[types.Part.from_text(text=result_text)]
                        )
                    )
                
                return result_text
                
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                is_retryable = any(term in error_str for term in [
                    "rate limit", "quota", "429", "503", "overloaded", "timeout"
                ])
                
                if is_retryable and attempt < self._max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    print(f"⚠️ [{self.persona_name}] Retry {attempt + 1} after {delay:.1f}s")
                    time.sleep(delay)
                elif not is_retryable:
                    raise GeminiBrainError(f"[{self.persona_name}] Error: {e}") from e
        
        raise GeminiBrainError(
            f"[{self.persona_name}] All retries exhausted. Last error: {last_exception}"
        ) from last_exception
    
    def generate_stream(
        self,
        prompt: str,
        use_chat: bool = False,
        temperature: Optional[float] = None
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response from the Gemini model.
        
        Yields text chunks as they arrive.
        """
        try:
            if use_chat:
                self._chat_history.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    )
                )
                contents = self._chat_history
            else:
                contents = prompt
            
            config = types.GenerateContentConfig(
                system_instruction=self.system_instruction,
            )
            if temperature is not None:
                config.temperature = temperature
            
            full_response = ""
            
            for chunk in self.client.models.generate_content_stream(
                model=self._model_name,
                contents=contents,
                config=config
            ):
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            
            if use_chat and full_response:
                self._chat_history.append(
                    types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=full_response)]
                    )
                )
                
        except Exception as e:
            raise GeminiBrainError(f"[{self.persona_name}] Streaming error: {e}") from e
    
    def reset_chat(self):
        """Clear chat history."""
        self._chat_history = []
    
    def __repr__(self) -> str:
        return f"GeminiBrain(persona='{self.persona_name}', model='{self._model_name}')"
