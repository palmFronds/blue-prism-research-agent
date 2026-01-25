# CLAUDE.md

Guidance for Claude Code when working with this repository.

## Project Identity

**Research Context Aggregator** — A deterministic pipeline that gathers, cleans, structures, and packages research context for downstream consumers.

**Critical clarification**: No LLM calls are implemented or required. This system produces context, not answers. Reasoning is delegated to downstream consumers.

## Architecture

```
Blue Prism → Browser → Extraction → Cleaning → Structuring → Context Output
```

### Pipeline Stages

1. **Blue Prism Controller**: Orchestrates the aggregation pipeline
2. **Browser Automation**: Chrome/Edge navigation via stable CSS selectors
3. **Content Extraction**: HTML parsing with error containment
4. **Content Cleaning**: Text normalization, noise removal
5. **Structuring**: Schema enforcement, metadata attachment
6. **Context Packaging**: JSON + Markdown + optional prompt templates

### Key Components

- **Blue Prism Objects**: ChromeNavigation, ContentExtraction, ContextFormatter, ExceptionHandler, AuditLogger
- **Bridge Service**: Python Flask API for Blue Prism ↔ external communication
- **Output Formats**: Structured JSON, human-readable Markdown, prompt templates

## Project Structure

```
research-context-aggregator/
├── bridge/                 # Python Flask bridge service
│   └── ...
├── blue-prism/             # Blue Prism objects and processes
│   ├── objects/
│   └── processes/
├── schemas/                # JSON schema definitions
│   └── context-pack.schema.json
├── templates/              # Prompt templates (no execution)
│   ├── claude.template.md
│   ├── gpt.template.md
│   └── local.template.md
└── docs/                   # Documentation
```

## Terminology

Use these terms consistently:

| Correct Term | Incorrect Terms |
|--------------|-----------------|
| Context Formatter | AI Client |
| Aggregation Pipeline | Research Agent |
| Context Pack | Final Report |
| Prompt-Ready Context Output | Prompt Generation |
| Downstream Consumer | AI Model, LLM |

## Design Principles

### Determinism First
- Same input must produce identical output
- No randomness in extraction or formatting
- Reproducible results for debugging and auditing

### Model-Agnostic
- Output works with any downstream consumer
- No assumptions about which LLM (if any) will process the context
- Human analysts are equally valid consumers

### Zero Runtime Dependencies
- No API keys required
- No external service calls
- Self-contained execution

### Context Over Answers
- System produces structured information
- System does not interpret, summarize, or reason
- Reasoning responsibility is explicitly delegated downstream

## Output Schema

Context Packs follow this structure:

```json
{
  "context_pack": {
    "version": "string",
    "generated_at": "ISO8601 timestamp",
    "query": "string",
    "source_count": "integer",
    "sources": [
      {
        "url": "string",
        "title": "string",
        "extracted_at": "ISO8601 timestamp",
        "content": "string",
        "word_count": "integer",
        "metadata": {}
      }
    ],
    "aggregated_content": "string",
    "statistics": {
      "total_words": "integer",
      "total_sources": "integer",
      "successful_extractions": "integer",
      "failed_extractions": "integer"
    }
  }
}
```

## Build & Development

### Bridge Service Setup
```bash
cd bridge
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

### Run Tests
```bash
cd bridge
pytest tests/
```

## Environment Variables

Required in `bridge/.env`:
```
FLASK_ENV=development
LOG_LEVEL=INFO
```

**Note**: No API keys are required. This is intentional.

## Design Patterns

- **Deterministic Selectors**: Stable CSS selectors (ID, data attributes) over brittle XPath
- **Error Containment**: Per-source failures do not halt the pipeline
- **In-Memory Processing**: No intermediate disk writes
- **Schema Enforcement**: All outputs validate against defined schemas

## Code Review Guidelines

When reviewing contributions:

1. **Reject LLM integration**: This system does not call LLMs. Period.
2. **Verify determinism**: Ensure no randomness or non-reproducible behavior
3. **Check terminology**: Use "Context Pack", not "Report"; "Aggregation Pipeline", not "Agent"
4. **Validate outputs**: All Context Packs must conform to schema
5. **Preserve debuggability**: Maintain clear logging and state inspection
