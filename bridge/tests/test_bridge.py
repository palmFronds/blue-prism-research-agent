"""
Tests for the Blue Prism OpenAI Bridge API.

Run with: pytest tests/test_bridge.py -v
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set a dummy API key for testing
os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing"

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Health endpoint should return JSON."""
        response = client.get("/health")
        data = response.get_json()
        assert data is not None
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_includes_version(self, client):
        """Health endpoint should include version."""
        response = client.get("/health")
        data = response.get_json()
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_health_includes_openai_configured(self, client):
        """Health endpoint should indicate if OpenAI is configured."""
        response = client.get("/health")
        data = response.get_json()
        assert "openai_configured" in data
        assert isinstance(data["openai_configured"], bool)


class TestAnalyzeEndpoint:
    """Tests for the /analyze endpoint."""

    def test_analyze_requires_json(self, client):
        """Analyze endpoint should reject non-JSON requests."""
        response = client.post("/analyze", data="not json")
        assert response.status_code == 400
        data = response.get_json()
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_analyze_requires_query_or_sources(self, client):
        """Analyze endpoint should require query or sources."""
        response = client.post(
            "/analyze",
            json={"request_id": "test-001"},
            content_type="application/json"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["error_code"] == "VALIDATION_ERROR"

    @patch("app.client.responses.create")
    def test_analyze_success(self, mock_create, client):
        """Analyze endpoint should return analysis on success."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.output_text = "This is the AI analysis."
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 100
        mock_create.return_value = mock_response

        response = client.post(
            "/analyze",
            json={
                "request_id": "test-001",
                "query": "What is AI?",
                "sources": "AI is artificial intelligence."
            },
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["request_id"] == "test-001"
        assert data["analysis"] == "This is the AI analysis."
        assert "tokens_used" in data
        assert "processing_time_ms" in data

    @patch("app.client.responses.create")
    def test_analyze_with_query_only(self, mock_create, client):
        """Analyze should work with just a query."""
        mock_response = MagicMock()
        mock_response.output_text = "Analysis result."
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 50
        mock_create.return_value = mock_response

        response = client.post(
            "/analyze",
            json={
                "request_id": "test-002",
                "query": "Explain machine learning"
            },
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    @patch("app.client.responses.create")
    def test_analyze_with_sources_only(self, mock_create, client):
        """Analyze should work with just sources."""
        mock_response = MagicMock()
        mock_response.output_text = "Analysis of sources."
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 75
        mock_create.return_value = mock_response

        response = client.post(
            "/analyze",
            json={
                "request_id": "test-003",
                "sources": "Some research content to analyze."
            },
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    @patch("app.client.responses.create")
    def test_analyze_auto_request_id(self, mock_create, client):
        """Analyze should auto-generate request_id if not provided."""
        mock_response = MagicMock()
        mock_response.output_text = "Analysis."
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 10
        mock_create.return_value = mock_response

        response = client.post(
            "/analyze",
            json={"query": "Test query"},
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["request_id"].startswith("auto-")


class TestErrorHandling:
    """Tests for error handling."""

    @patch("app.client.responses.create")
    def test_rate_limit_error(self, mock_create, client):
        """Should return recoverable error on rate limit."""
        from openai import RateLimitError

        mock_create.side_effect = RateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(status_code=429),
            body={}
        )

        response = client.post(
            "/analyze",
            json={"request_id": "test-rate", "query": "Test"},
            content_type="application/json"
        )

        assert response.status_code == 429
        data = response.get_json()
        assert data["success"] is False
        assert data["error_code"] == "RATE_LIMIT"
        assert data["recoverable"] is True

    @patch("app.client.responses.create")
    def test_auth_error(self, mock_create, client):
        """Should return non-recoverable error on auth failure."""
        from openai import AuthenticationError

        mock_create.side_effect = AuthenticationError(
            message="Invalid API key",
            response=MagicMock(status_code=401),
            body={}
        )

        response = client.post(
            "/analyze",
            json={"request_id": "test-auth", "query": "Test"},
            content_type="application/json"
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
        assert data["error_code"] == "AUTH_ERROR"
        assert data["recoverable"] is False

    @patch("app.client.responses.create")
    def test_timeout_error(self, mock_create, client):
        """Should return recoverable error on timeout."""
        from openai import APITimeoutError

        mock_create.side_effect = APITimeoutError(request=MagicMock())

        response = client.post(
            "/analyze",
            json={"request_id": "test-timeout", "query": "Test"},
            content_type="application/json"
        )

        assert response.status_code == 504
        data = response.get_json()
        assert data["success"] is False
        assert data["error_code"] == "TIMEOUT"
        assert data["recoverable"] is True


class TestChatEndpoint:
    """Tests for the /chat endpoint."""

    def test_chat_requires_messages(self, client):
        """Chat endpoint should require messages array."""
        response = client.post(
            "/chat",
            json={"request_id": "test-chat"},
            content_type="application/json"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["error_code"] == "VALIDATION_ERROR"

    @patch("app.client.chat.completions.create")
    def test_chat_success(self, mock_create, client):
        """Chat endpoint should return content on success."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello from OpenAI!"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 25
        mock_create.return_value = mock_response

        response = client.post(
            "/chat",
            json={
                "request_id": "test-chat-001",
                "messages": [
                    {"role": "user", "content": "Hello!"}
                ]
            },
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["content"] == "Hello from OpenAI!"
        assert data["finish_reason"] == "stop"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
