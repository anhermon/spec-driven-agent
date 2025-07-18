"""
Tests for LLM integration functionality.
"""

from unittest.mock import AsyncMock, patch

import pytest

from spec_driven_agent.core.llm_integration import (
    LLMIntegration,
    LLMIntegrationError,
    close_llm_integration,
    get_llm_integration,
)


class TestLLMIntegration:
    """Test LLM integration functionality."""

    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables."""
        with patch.dict(
            "os.environ",
            {
                "LITELLM_PROXY_URL": "http://test-server:4000/",
                "LITELLM_API_KEY": "test-api-key",
            },
        ):
            yield

    @pytest.fixture
    def llm_integration(self, mock_env_vars):
        """Create LLM integration instance."""
        return LLMIntegration()

    @pytest.mark.asyncio
    async def test_llm_integration_initialization(self, mock_env_vars):
        """Test LLM integration initialization."""
        llm = LLMIntegration()
        assert llm.base_url == "http://test-server:4000/"
        assert llm.api_key == "test-api-key"

    @pytest.mark.asyncio
    async def test_llm_integration_missing_api_key(self):
        """Test LLM integration with missing API key."""
        with patch.dict(
            "os.environ", {"LITELLM_PROXY_URL": "http://test-server:4000/"}
        ):
            with pytest.raises(LLMIntegrationError, match="LITELLM_API_KEY not found"):
                LLMIntegration()

    @pytest.mark.asyncio
    async def test_test_connection_success(self, llm_integration):
        """Test successful connection test."""
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status": "ok"}

        with patch.object(llm_integration.client, "get", return_value=mock_response):
            result = await llm_integration.test_connection()

            assert result["status"] == "connected"
            assert result["provider"] == "LiteLLM Proxy"
            assert result["base_url"] == "http://test-server:4000/"

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, llm_integration):
        """Test connection test failure."""
        import httpx

        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=None, response=mock_response
        )

        with patch.object(llm_integration.client, "get", return_value=mock_response):
            with pytest.raises(
                LLMIntegrationError, match="HTTP error testing connection"
            ):
                await llm_integration.test_connection()

    @pytest.mark.asyncio
    async def test_generate_text_success(self, llm_integration):
        """Test successful text generation."""
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Generated text"}, "finish_reason": "stop"}
            ],
            "usage": {"total_tokens": 100},
            "model": "gpt-4",
        }

        with patch.object(llm_integration.client, "post", return_value=mock_response):
            result = await llm_integration.generate_text("Test prompt")

            assert result["text"] == "Generated text"
            assert result["usage"]["total_tokens"] == 100
            assert result["model"] == "gpt-4"

    @pytest.mark.asyncio
    async def test_analyze_requirements(self, llm_integration):
        """Test requirements analysis."""
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Requirements analysis"}}],
            "usage": {"total_tokens": 200},
            "model": "gpt-4",
        }

        with patch.object(llm_integration.client, "post", return_value=mock_response):
            result = await llm_integration.analyze_requirements("Test requirements")

            assert result["analysis"] == "Requirements analysis"
            assert result["usage"]["total_tokens"] == 200
            assert result["model"] == "gpt-4"

    @pytest.mark.asyncio
    async def test_generate_api_spec(self, llm_integration):
        """Test API specification generation."""
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "OpenAPI spec"}}],
            "usage": {"total_tokens": 300},
            "model": "gpt-4",
        }

        with patch.object(llm_integration.client, "post", return_value=mock_response):
            result = await llm_integration.generate_api_spec("Requirements analysis")

            assert result["api_spec"] == "OpenAPI spec"
            assert result["usage"]["total_tokens"] == 300
            assert result["model"] == "gpt-4"

    @pytest.mark.asyncio
    async def test_validate_consistency(self, llm_integration):
        """Test consistency validation."""
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Consistency analysis"}}],
            "usage": {"total_tokens": 150},
            "model": "gpt-4",
        }

        with patch.object(llm_integration.client, "post", return_value=mock_response):
            result = await llm_integration.validate_consistency({"test": "data"})

            assert result["consistency_analysis"] == "Consistency analysis"
            assert result["usage"]["total_tokens"] == 150
            assert result["model"] == "gpt-4"

    @pytest.mark.asyncio
    async def test_generate_task_plan(self, llm_integration):
        """Test task plan generation."""
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Task plan"}}],
            "usage": {"total_tokens": 250},
            "model": "gpt-4",
        }

        with patch.object(llm_integration.client, "post", return_value=mock_response):
            result = await llm_integration.generate_task_plan(
                "Test task", {"context": "data"}
            )

            assert result["task_plan"] == "Task plan"
            assert result["usage"]["total_tokens"] == 250
            assert result["model"] == "gpt-4"

    @pytest.mark.asyncio
    async def test_close_client(self, llm_integration):
        """Test client closure."""
        with patch.object(llm_integration.client, "aclose") as mock_close:
            await llm_integration.close()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_env_vars):
        """Test async context manager."""
        with patch(
            "spec_driven_agent.core.llm_integration.httpx.AsyncClient"
        ) as mock_client:
            mock_client.return_value.aclose = AsyncMock()

            async with LLMIntegration() as llm:
                assert isinstance(llm, LLMIntegration)

            mock_client.return_value.aclose.assert_called_once()


class TestLLMIntegrationGlobal:
    """Test global LLM integration functions."""

    @pytest.mark.asyncio
    async def test_get_llm_integration_singleton(self, mock_env_vars):
        """Test that get_llm_integration returns a singleton."""
        with patch(
            "spec_driven_agent.core.llm_integration.LLMIntegration"
        ) as mock_llm_class:
            mock_llm_class.return_value = "mock_llm_instance"

            # First call should create instance
            result1 = await get_llm_integration()
            assert result1 == "mock_llm_instance"
            mock_llm_class.assert_called_once()

            # Second call should return same instance
            result2 = await get_llm_integration()
            assert result2 == "mock_llm_instance"
            # Should not create another instance
            assert mock_llm_class.call_count == 1

    @pytest.mark.asyncio
    async def test_close_llm_integration(self, mock_env_vars):
        """Test closing global LLM integration."""
        with patch(
            "spec_driven_agent.core.llm_integration.LLMIntegration"
        ) as mock_llm_class:
            mock_instance = AsyncMock()
            mock_llm_class.return_value = mock_instance

            # Get instance
            await get_llm_integration()

            # Close it
            await close_llm_integration()

            # Verify close was called
            mock_instance.close.assert_called_once()
