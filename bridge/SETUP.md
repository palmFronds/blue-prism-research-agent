# Blue Prism OpenAI Bridge - Setup Guide

A minimal Flask API that handles all OpenAI SDK complexity, allowing Blue Prism to make simple HTTP requests.

## Quick Start (5 minutes)

### 1. Prerequisites
- Python 3.11+ installed ([download](https://www.python.org/downloads/))
- OpenAI API key

### 2. Setup

```batch
cd bridge

:: Create virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

:: Configure API key
copy config.env.template config.env
:: Edit config.env and add your OPENAI_API_KEY
```

### 3. Start the Bridge

```batch
start.bat
```

The server starts on `http://127.0.0.1:5050`

### 4. Test It

```batch
curl http://localhost:5050/health
```

---

## API Endpoints

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "openai_configured": true,
  "timestamp": "2026-01-14T10:30:00Z"
}
```

### Analyze (Main Endpoint)
```
POST /analyze
Content-Type: application/json
```

**Request:**
```json
{
  "request_id": "bp-12345",
  "query": "Research topic",
  "sources": "Concatenated source content (up to 200KB+)",
  "model": "gpt-5-nano",
  "max_tokens": 4096
}
```

**Success Response:**
```json
{
  "request_id": "bp-12345",
  "success": true,
  "analysis": "AI-generated analysis...",
  "tokens_used": 5000,
  "processing_time_ms": 3500,
  "timestamp": "2026-01-14T10:30:08Z"
}
```

**Error Response:**
```json
{
  "request_id": "bp-12345",
  "success": false,
  "error_code": "RATE_LIMIT",
  "error_message": "Rate limit exceeded. Retry after 60 seconds.",
  "recoverable": true,
  "details": {"retry_after_seconds": 60},
  "timestamp": "2026-01-14T10:30:01Z"
}
```

### Chat (Alternative Endpoint)
```
POST /chat
Content-Type: application/json
```

For more control using the Chat Completions API format.

---

## Blue Prism Integration

### C# Code Stage Example

```csharp
using System.Net;
using System.Text;
using System.Web.Script.Serialization;

// Build request
var request = new {
    request_id = Guid.NewGuid().ToString(),
    query = Query,           // Input: Query text
    sources = Sources,       // Input: Source content
    model = "gpt-5-nano",
    max_tokens = 4096
};

var serializer = new JavaScriptSerializer();
serializer.MaxJsonLength = int.MaxValue;
string jsonRequest = serializer.Serialize(request);

// Make HTTP request
using (WebClient client = new WebClient())
{
    client.Headers[HttpRequestHeader.ContentType] = "application/json";
    client.Encoding = Encoding.UTF8;

    try
    {
        string jsonResponse = client.UploadString(
            "http://localhost:5050/analyze",
            "POST",
            jsonRequest
        );

        dynamic response = serializer.DeserializeObject(jsonResponse);

        if (response["success"] == true)
        {
            Analysis = response["analysis"];   // Output: Analysis text
            Success = true;
        }
        else
        {
            ErrorCode = response["error_code"];
            ErrorMessage = response["error_message"];
            Recoverable = response["recoverable"];
            Success = false;
        }
    }
    catch (WebException ex)
    {
        // Handle HTTP errors
        using (var reader = new StreamReader(ex.Response.GetResponseStream()))
        {
            string errorJson = reader.ReadToEnd();
            dynamic error = serializer.DeserializeObject(errorJson);
            ErrorCode = error["error_code"];
            ErrorMessage = error["error_message"];
            Recoverable = error["recoverable"];
            Success = false;
        }
    }
}
```

### Error Handling in Blue Prism

```
1. Call /analyze endpoint
2. Check "success" field:
   - true: Use "analysis" field
   - false: Check "recoverable" field
3. If recoverable == true AND retry_count < 3:
   - Wait (use details.retry_after_seconds if available)
   - Retry request
4. If recoverable == false OR retry_count >= 3:
   - Log error to audit
   - Move to Dead Letter Queue
   - Raise exception
```

---

## Error Codes

| Code | HTTP | Meaning | Recoverable |
|------|------|---------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request format | No |
| `AUTH_ERROR` | 401 | Invalid API key | No |
| `CONTEXT_LENGTH` | 400 | Content too large | No |
| `RATE_LIMIT` | 429 | Too many requests | Yes |
| `TIMEOUT` | 504 | Request timed out | Yes |
| `SERVER_ERROR` | 502 | OpenAI service error | Yes |
| `BRIDGE_ERROR` | 500 | Internal bridge error | No |

---

## Running as Windows Service

### Option 1: NSSM (Recommended)

1. Download [NSSM](https://nssm.cc/download)
2. Install service:
```batch
nssm install BluePrismBridge "C:\path\to\python.exe"
nssm set BluePrismBridge AppDirectory "C:\path\to\bridge"
nssm set BluePrismBridge AppParameters "-m waitress --host=127.0.0.1 --port=5050 app:app"
nssm set BluePrismBridge Start SERVICE_AUTO_START
nssm start BluePrismBridge
```

### Option 2: Task Scheduler

1. Create scheduled task to run `start.bat prod` at system startup
2. Configure to run whether user is logged on or not

---

## Logging

Logs are written to `logs/bridge.log` with rotation (5 files, 10MB each).

**Log format:**
```
2026-01-14 10:30:00 [INFO] Request bp-12345: model=gpt-5-nano, content_length=215000
2026-01-14 10:30:08 [INFO] Request bp-12345: completed, tokens=46500, time_ms=8500
```

---

## Testing

### Run Unit Tests
```batch
venv\Scripts\activate
pip install pytest
pytest tests/test_bridge.py -v
```

### Manual Testing
```batch
:: Health check
curl http://localhost:5050/health

:: Simple analysis
curl -X POST http://localhost:5050/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"request_id\":\"test-001\",\"query\":\"What is AI?\",\"sources\":\"AI stands for artificial intelligence.\"}"
```

---

## Troubleshooting

### "config.env not found"
Copy `config.env.template` to `config.env` and add your OpenAI API key.

### "Connection refused"
Make sure the bridge is running (`start.bat`).

### "AUTH_ERROR"
Check that your OpenAI API key in `config.env` is correct.

### "CONTEXT_LENGTH"
Your source content is too large for the model. Try truncating to under 100KB.

### "TIMEOUT"
The request took too long. Try:
- Reducing content size
- Using `gpt-5-nano` (fastest model)
- Increasing `REQUEST_TIMEOUT` in `config.env`
