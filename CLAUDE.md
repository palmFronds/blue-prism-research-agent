# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A deterministic Blue Prism RPA research agent that navigates Chrome, extracts web content, enriches it with LLM APIs (OpenAI/Anthropic/AWS Bedrock), and manages work through AWS SQS queues with auditable workflows.

**Current State**: Project is in documentation/planning phase - no code has been implemented yet.

## Architecture

```
Blue Prism Bot → AWS API Gateway → Lambda Functions → AWS Services (SQS, DynamoDB, S3)
                                        ↓
                              LLM Providers (OpenAI/Anthropic/Bedrock)
```

### Key Components
- **Blue Prism Objects**: ChromeNavigation, ContentExtraction, QueueManagement, ExceptionHandler, AuditLogger
- **API Layer**: Python FastAPI (or Node.js Express) on Lambda
- **Queues**: SQS (research-queue, enrichment-queue, dead-letter-queue)
- **Storage**: DynamoDB (WorkItems, AuditLogs, Configurations), S3 (logs, data, exports)

## Planned Project Structure

```
blue-prism-research-agent/
├── api/                    # FastAPI service (Python 3.11+)
│   ├── src/handlers/       # Lambda handlers
│   ├── src/services/       # Business logic
│   ├── src/models/         # Pydantic models
│   └── tests/
├── llm-service/            # LLM provider abstraction layer
│   ├── src/providers/      # OpenAI, Anthropic, Bedrock implementations
│   └── src/prompts/        # Prompt templates
├── blue-prism/             # Blue Prism objects and processes
│   ├── objects/
│   └── processes/
├── infrastructure/         # Terraform or AWS CDK
│   └── terraform/
└── deployment/             # Docker, Lambda packages
```

## Build & Development Commands

### Python API Setup
```bash
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Local API
```bash
cd api
uvicorn src.main:app --reload
```

### Run Tests
```bash
cd api
pytest tests/                 # All tests
pytest tests/unit/            # Unit tests only
pytest tests/integration/     # Integration tests
```

### Infrastructure Deployment (Terraform)
```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### Infrastructure Deployment (AWS CDK)
```bash
cd infrastructure/cdk
npm install
cdk bootstrap
cdk deploy
```

### Docker Build
```bash
cd api
docker build -t rpa-api:latest .
```

### Lambda Deployment
```bash
cd api
zip -r function.zip src/ requirements.txt
aws lambda create-function --function-name rpa-queue-api --runtime python3.11 --handler src.handlers.queue_handler --zip-file fileb://function.zip
```

## API Endpoints

- `POST /api/queue/item` - Add work item to research queue
- `GET /api/queue/item/{id}` - Get work item status/results
- `POST /api/llm/enrich` - Enrich content with LLM
- `GET /api/status` - Health check
- `POST /api/audit/log` - Log activity

## Technology Stack

- **RPA**: Blue Prism v7+ with Chrome automation
- **API**: Python 3.11+ / FastAPI (or Node.js 18+ / Express)
- **AWS**: API Gateway, Lambda, SQS, DynamoDB, S3, CloudWatch
- **LLM**: OpenAI SDK, Anthropic SDK, boto3 (Bedrock)
- **IaC**: Terraform or AWS CDK

## Key Dependencies

```
fastapi==0.104.1
uvicorn==0.24.0
boto3==1.29.0
pydantic==2.5.0
openai==1.3.0
anthropic==0.7.0
python-dotenv==1.0.0
```

## Environment Variables

Required in `api/.env`:
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
LOG_LEVEL=INFO
```

## Design Patterns

- **LLM Provider Abstraction**: Abstract base class `LLMProvider` with implementations for OpenAI, Anthropic, Bedrock
- **Deterministic Selectors**: Use stable CSS selectors (ID, data attributes) over XPath for web scraping
- **Queue-Based Processing**: All work flows through SQS queues with DynamoDB status tracking
- **Exponential Backoff**: Retry logic with dead letter queue for failed items
