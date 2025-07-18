"""
LLM integration for the spec-driven agent workflow system.
"""

import os
import asyncio
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMIntegrationError(Exception):
    """Exception raised for LLM integration errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class LLMIntegration:
    """LLM integration using LiteLLM proxy."""

    def __init__(self):
        self.base_url = os.environ.get("LITELLM_PROXY_URL", "http://10.250.0.17:4000/")
        self.api_key = os.environ.get("LITELLM_API_KEY", "")

        if "LITELLM_API_KEY" not in os.environ or not self.api_key:
            raise LLMIntegrationError(
                "LITELLM_API_KEY not found in environment variables"
            )

        # Ensure base URL ends with slash
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to the LLM provider."""
        try:
            response = await self.client.get("health")
            # Support both sync and async mocks
            await _maybe_await(response.raise_for_status())
            data = await _maybe_await(response.json())
            return {
                "status": "connected",
                "provider": "LiteLLM Proxy",
                "base_url": self.base_url,
                "response": data,
            }
        except httpx.HTTPStatusError as e:
            raise LLMIntegrationError(
                f"HTTP error testing connection: {e.response.status_code}",
                e.response.status_code,
            )
        except httpx.RequestError as e:
            raise LLMIntegrationError(f"Connection error: {str(e)}")

    async def generate_text(
        self,
        prompt: str,
        model: str = "gpt-4",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate text using the LLM."""
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = await self.client.post("v1/chat/completions", json=payload)
            await _maybe_await(response.raise_for_status())
            result = await _maybe_await(response.json())

            return {
                "text": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {}),
                "model": result.get("model", model),
                "finish_reason": result["choices"][0].get("finish_reason"),
            }
        except httpx.HTTPStatusError as e:
            raise LLMIntegrationError(
                f"HTTP error generating text: {e.response.status_code}",
                e.response.status_code,
            )
        except httpx.RequestError as e:
            raise LLMIntegrationError(f"Request error generating text: {str(e)}")

    async def analyze_requirements(self, requirements_text: str) -> Dict[str, Any]:
        """Analyze requirements using LLM."""
        system_message = (
            "You are an expert requirements analyst. Analyze the provided "
            "requirements and extract:\n"
            "1. Functional requirements\n"
            "2. Non-functional requirements\n"
            "3. Technical constraints\n"
            "4. Stakeholder needs\n"
            "5. Potential risks or ambiguities\n\n"
            "Provide your analysis in a structured JSON format."
        )

        prompt = f"Please analyze the following requirements:\n\n{requirements_text}"

        result = await self.generate_text(
            prompt=prompt,
            system_message=system_message,
            model="gpt-4",
            max_tokens=2000,
            temperature=0.3,
        )

        return {
            "analysis": result["text"],
            "usage": result["usage"],
            "model": result["model"],
        }

    async def generate_api_spec(self, requirements_analysis: str) -> Dict[str, Any]:
        """Generate API specification using LLM."""
        system_message = (
            "You are an expert API designer. Based on the requirements analysis, "
            "generate a comprehensive OpenAPI 3.0 specification including:\n"
            "1. API endpoints with proper HTTP methods\n"
            "2. Request/response schemas\n"
            "3. Authentication mechanisms\n"
            "4. Error handling\n"
            "5. Documentation\n\n"
            "Provide the specification in valid JSON format."
        )

        prompt = (
            f"Based on this requirements analysis, generate an OpenAPI 3.0 "
            f"specification:\n\n{requirements_analysis}"
        )

        result = await self.generate_text(
            prompt=prompt,
            system_message=system_message,
            model="gpt-4",
            max_tokens=3000,
            temperature=0.2,
        )

        return {
            "api_spec": result["text"],
            "usage": result["usage"],
            "model": result["model"],
        }

    async def validate_consistency(
        self, context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate consistency of context data using LLM."""
        system_message = (
            "You are an expert system architect. Analyze the provided context "
            "data for consistency issues including:\n"
            "1. Contradictions in requirements\n"
            "2. Missing dependencies\n"
            "3. Inconsistent naming conventions\n"
            "4. Architectural conflicts\n"
            "5. Security concerns\n\n"
            "Provide a detailed analysis with specific recommendations."
        )

        prompt = (
            f"Please analyze this context data for consistency issues:\n\n"
            f"{context_data}"
        )

        result = await self.generate_text(
            prompt=prompt,
            system_message=system_message,
            model="gpt-4",
            max_tokens=2000,
            temperature=0.3,
        )

        return {
            "consistency_analysis": result["text"],
            "usage": result["usage"],
            "model": result["model"],
        }

    async def generate_task_plan(
        self, task_description: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a detailed task execution plan using LLM."""
        system_message = (
            "You are an expert project manager. Based on the task description "
            "and context, create a detailed execution plan including:\n"
            "1. Task breakdown into subtasks\n"
            "2. Dependencies and prerequisites\n"
            "3. Estimated effort for each subtask\n"
            "4. Required resources and skills\n"
            "5. Risk assessment and mitigation strategies\n"
            "6. Success criteria\n\n"
            "Provide the plan in a structured format."
        )

        prompt = (
            f"Task: {task_description}\n\nContext: {context}\n\n"
            "Please create a detailed execution plan."
        )

        result = await self.generate_text(
            prompt=prompt,
            system_message=system_message,
            model="gpt-4",
            max_tokens=2500,
            temperature=0.4,
        )

        return {
            "task_plan": result["text"],
            "usage": result["usage"],
            "model": result["model"],
        }

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Global LLM integration instance
_llm_integration: Optional[LLMIntegration] = None


async def get_llm_integration() -> LLMIntegration:
    """Get the global LLM integration instance."""
    global _llm_integration
    if _llm_integration is None:
        _llm_integration = LLMIntegration()
    return _llm_integration


async def close_llm_integration():
    """Close the global LLM integration instance."""
    global _llm_integration
    if _llm_integration is not None:
        if hasattr(_llm_integration, "close"):
            await _llm_integration.close()
        _llm_integration = None


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


async def _maybe_await(value):  # type: ignore
    """Await the value if it's awaitable (supports AsyncMock in tests)."""
    if asyncio.iscoroutine(value):
        return await value
    return value
