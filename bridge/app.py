"""
Blue Prism → OpenAI Bridge API

A minimal Flask API that handles all OpenAI SDK complexity,
allowing Blue Prism to make simple HTTP requests.

Usage:
    python app.py              # Development mode
    waitress-serve app:app     # Production mode
"""

import os
import time
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from functools import wraps

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError, APITimeoutError, AuthenticationError

# Load configuration
load_dotenv("config.env")

# Initialize Flask app
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 52428800))

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID"),
    timeout=float(os.getenv("REQUEST_TIMEOUT", 120))
)

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "bridge.log"),
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(getattr(logging, LOG_LEVEL))

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
logging.getLogger().addHandler(console_handler)

logger = logging.getLogger(__name__)


def get_timestamp():
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_error_response(request_id, error_code, message, recoverable=False, details=None, http_status=500):
    """Create a standardized error response."""
    response = {
        "request_id": request_id,
        "success": False,
        "error_code": error_code,
        "error_message": message,
        "recoverable": recoverable,
        "timestamp": get_timestamp()
    }
    if details:
        response["details"] = details
    return jsonify(response), http_status


def validate_request(f):
    """Decorator to validate incoming requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return create_error_response(
                request_id="unknown",
                error_code="VALIDATION_ERROR",
                message="Request must be JSON",
                http_status=400
            )
        return f(*args, **kwargs)
    return decorated_function


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for Blue Prism connectivity tests."""
    api_key_configured = bool(os.getenv("OPENAI_API_KEY"))

    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "openai_configured": api_key_configured,
        "timestamp": get_timestamp()
    })


@app.route("/analyze", methods=["POST"])
@validate_request
def analyze():
    """
    Main endpoint for research analysis.

    Request JSON:
    {
        "request_id": "bp-12345",
        "query": "Research topic",
        "sources": "Concatenated source content",
        "model": "gpt-5-nano",  (optional, defaults to gpt-5-nano)
        "max_tokens": 4096      (optional)
    }

    Response JSON (success):
    {
        "request_id": "bp-12345",
        "success": true,
        "analysis": "AI-generated analysis...",
        "tokens_used": 5000,
        "processing_time_ms": 3500
    }
    """
    start_time = time.time()
    data = request.get_json()

    # Extract fields
    request_id = data.get("request_id", f"auto-{int(time.time())}")
    query = data.get("query", "")
    sources = data.get("sources", "")
    model = data.get("model", "gpt-5-nano")
    max_tokens = data.get("max_tokens", 4096)

    # Validate required fields
    if not query and not sources:
        logger.warning(f"Request {request_id}: Missing query and sources")
        return create_error_response(
            request_id=request_id,
            error_code="VALIDATION_ERROR",
            message="At least one of 'query' or 'sources' is required",
            http_status=400
        )

    # Build the input prompt
    input_text = ""
    if query:
        input_text += f"Research Query: {query}\n\n"
    if sources:
        input_text += f"Source Content:\n{sources}\n\n"
    input_text += "Please analyze the above content and provide a comprehensive research summary."

    content_length = len(input_text)
    logger.info(f"Request {request_id}: model={model}, content_length={content_length}")

    try:
        # Call OpenAI Responses API
        response = client.responses.create(
            model=model,
            input=input_text,
            max_output_tokens=max_tokens
        )

        analysis = response.output_text
        tokens_used = getattr(response.usage, "total_tokens", 0) if hasattr(response, "usage") else 0

        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(f"Request {request_id}: completed, tokens={tokens_used}, time_ms={processing_time_ms}")

        return jsonify({
            "request_id": request_id,
            "success": True,
            "analysis": analysis,
            "tokens_used": tokens_used,
            "processing_time_ms": processing_time_ms,
            "timestamp": get_timestamp()
        })

    except AuthenticationError as e:
        logger.error(f"Request {request_id}: Authentication failed - {e}")
        return create_error_response(
            request_id=request_id,
            error_code="AUTH_ERROR",
            message="Invalid OpenAI API key",
            recoverable=False,
            http_status=401
        )

    except RateLimitError as e:
        retry_after = getattr(e, "retry_after", 60)
        logger.warning(f"Request {request_id}: Rate limited, retry after {retry_after}s")
        return create_error_response(
            request_id=request_id,
            error_code="RATE_LIMIT",
            message=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            recoverable=True,
            details={"retry_after_seconds": retry_after},
            http_status=429
        )

    except APITimeoutError as e:
        logger.error(f"Request {request_id}: Timeout - {e}")
        return create_error_response(
            request_id=request_id,
            error_code="TIMEOUT",
            message="Request timed out. Try again with a shorter input.",
            recoverable=True,
            http_status=504
        )

    except APIError as e:
        error_message = str(e)

        # Check for context length errors
        if "context_length" in error_message.lower() or "maximum" in error_message.lower():
            logger.error(f"Request {request_id}: Context length exceeded - {e}")
            return create_error_response(
                request_id=request_id,
                error_code="CONTEXT_LENGTH",
                message="Content too large for model. Please reduce the source content size.",
                recoverable=False,
                http_status=400
            )

        # Generic API error
        logger.error(f"Request {request_id}: API error - {e}")
        return create_error_response(
            request_id=request_id,
            error_code="SERVER_ERROR",
            message=f"OpenAI API error: {error_message}",
            recoverable=True,
            http_status=502
        )

    except Exception as e:
        logger.exception(f"Request {request_id}: Unexpected error - {e}")
        return create_error_response(
            request_id=request_id,
            error_code="BRIDGE_ERROR",
            message=f"Internal bridge error: {str(e)}",
            recoverable=False,
            http_status=500
        )


@app.route("/chat", methods=["POST"])
@validate_request
def chat():
    """
    Alternative endpoint using Chat Completions API format.
    Use this if you need more control over the conversation.

    Request JSON:
    {
        "request_id": "bp-12345",
        "model": "gpt-5-nano",
        "messages": [
            {"role": "system", "content": "You are a research assistant."},
            {"role": "user", "content": "Analyze this content..."}
        ],
        "max_tokens": 4096
    }
    """
    start_time = time.time()
    data = request.get_json()

    request_id = data.get("request_id", f"auto-{int(time.time())}")
    model = data.get("model", "gpt-5-nano")
    messages = data.get("messages", [])
    max_tokens = data.get("max_tokens", 4096)

    if not messages:
        return create_error_response(
            request_id=request_id,
            error_code="VALIDATION_ERROR",
            message="'messages' array is required",
            http_status=400
        )

    logger.info(f"Request {request_id}: chat endpoint, model={model}, messages={len(messages)}")

    try:
        # Use Chat Completions API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens
        )

        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        finish_reason = response.choices[0].finish_reason

        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(f"Request {request_id}: completed, tokens={tokens_used}, time_ms={processing_time_ms}")

        return jsonify({
            "request_id": request_id,
            "success": True,
            "content": content,
            "tokens_used": tokens_used,
            "finish_reason": finish_reason,
            "processing_time_ms": processing_time_ms,
            "timestamp": get_timestamp()
        })

    except AuthenticationError as e:
        logger.error(f"Request {request_id}: Authentication failed - {e}")
        return create_error_response(
            request_id=request_id,
            error_code="AUTH_ERROR",
            message="Invalid OpenAI API key",
            recoverable=False,
            http_status=401
        )

    except RateLimitError as e:
        retry_after = getattr(e, "retry_after", 60)
        logger.warning(f"Request {request_id}: Rate limited, retry after {retry_after}s")
        return create_error_response(
            request_id=request_id,
            error_code="RATE_LIMIT",
            message=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            recoverable=True,
            details={"retry_after_seconds": retry_after},
            http_status=429
        )

    except APITimeoutError as e:
        logger.error(f"Request {request_id}: Timeout - {e}")
        return create_error_response(
            request_id=request_id,
            error_code="TIMEOUT",
            message="Request timed out. Try again with a shorter input.",
            recoverable=True,
            http_status=504
        )

    except APIError as e:
        logger.error(f"Request {request_id}: API error - {e}")
        return create_error_response(
            request_id=request_id,
            error_code="SERVER_ERROR",
            message=f"OpenAI API error: {str(e)}",
            recoverable=True,
            http_status=502
        )

    except Exception as e:
        logger.exception(f"Request {request_id}: Unexpected error - {e}")
        return create_error_response(
            request_id=request_id,
            error_code="BRIDGE_ERROR",
            message=f"Internal bridge error: {str(e)}",
            recoverable=False,
            http_status=500
        )


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle requests that exceed MAX_CONTENT_LENGTH."""
    return create_error_response(
        request_id="unknown",
        error_code="PAYLOAD_TOO_LARGE",
        message="Request body exceeds maximum allowed size (50MB)",
        recoverable=False,
        http_status=413
    )


@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler."""
    logger.exception(f"Unhandled exception: {e}")
    return create_error_response(
        request_id="unknown",
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        recoverable=False,
        http_status=500
    )


if __name__ == "__main__":
    host = os.getenv("BRIDGE_HOST", "127.0.0.1")
    port = int(os.getenv("BRIDGE_PORT", 5050))

    logger.info(f"Starting Blue Prism OpenAI Bridge on {host}:{port}")

    # Use Flask's built-in server for development
    # For production, use: waitress-serve --host=127.0.0.1 --port=5050 app:app
    app.run(host=host, port=port, debug=False)
