# Research Context Aggregator: Blue Prism RPA

A deterministic pipeline that gathers, cleans, structures, and packages high-quality research context for downstream consumers. This system produces **context**.

## Project Definition

This is a **context aggregation system**. It performs the hardest part of AI-assisted research: assembling clean, reliable, structured context from web sources. The system deliberately stops before reasoning, that responsibility belongs to downstream consumers (chatbots, analysts, LLMs, etc.).

## Context Aggregation Over Agentic Browsing

| Agentic Browsing | Context Aggregation |
|------------------|---------------------|
| LLM decides what to click | Deterministic navigation rules |
| Non-reproducible results | Identical output for identical input |
| Requires API keys at runtime | Zero external dependencies |
| Failures are opaque | Failures are debuggable |
| Model-specific | Model-agnostic |
| Expensive per-run | Fixed compute cost |
| "Trust the agent" | "Inspect the data" |

---

## Overall Architecture

```
Research Query
     │
     ▼
┌─────────────────┐
│   Blue Prism    │  Orchestration layer
│   Controller    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Browser      │  Chrome/Edge automation
│   Automation    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Content      │  HTML parsing, text extraction
│   Extraction    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Content      │  Normalization, deduplication
│    Cleaning     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Structuring   │  Schema enforcement, metadata
│   & Packaging   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Context Pack   │  JSON + Markdown + Templates
│    Output       │
└─────────────────┘
         │
         ▼
   Downstream Consumer
   (Claude, GPT, Analyst, Local Model, etc.)
```

## Process Flow

**1. Initialization**
- Accepts inputs: `Research_Question`, `Num_Pages`, `Max_Results`, `Result_Count`
- Launches browser automation instance

**2. Browser Scraping**
- Executes deterministic search operations
- Retrieves result URLs via stable CSS selectors

**3. Extraction Loop**
- Navigates to each URL sequentially
- Extracts raw HTML content
- Cleans and normalizes article text
- Adds processed content to in-memory collection
- Continues until page limit reached or sources exhausted

**4. Context Formatter**
- Aggregates all extracted content
- Applies schema structure
- Generates prompt-ready context output
- Packages as Context Pack (JSON + Markdown)

**5. Output**
- Returns structured Context Pack
- Ready for consumption by any downstream system

---

## Output Formats

The aggregation pipeline produces a **Context Pack** containing:

### 1. Structured JSON Context

```json
{
  "context_pack": {
    "version": "1.0",
    "generated_at": "2025-01-15T10:30:00Z",
    "query": "Original research question",
    "source_count": 5,
    "sources": [
      {
        "url": "https://example.com/article",
        "title": "Article Title",
        "extracted_at": "2025-01-15T10:29:45Z",
        "content": "Cleaned article text...",
        "word_count": 1250,
        "metadata": {
          "domain": "example.com",
          "extraction_method": "article_body"
        }
      }
    ],
    "aggregated_content": "Combined text from all sources...",
    "statistics": {
      "total_words": 6200,
      "total_sources": 5,
      "successful_extractions": 5,
      "failed_extractions": 0
    }
  }
}
```

## Features

- **Deterministic Execution**: Same input produces same output, every time
- **Model-Agnostic Output**: Works with Claude, GPT, Llama, Mistral, or human analysts
- **Zero API Keys Required**: No external service dependencies at runtime
- **In-Memory Processing**: No disk writes during execution
- **Error Containment**: Per-source failure isolation with full logging
- **Debug-Friendly**: Real-time inspection of pipeline state
- **Structured Data**: Enforced schema for reliable downstream parsing

## Tech Stack

- **RPA Platform**: Blue Prism 7.x
- **Code Language**: C# .NET (Code Stages)
- **Browser Automation**: Chrome / Edge
- **Bridge Service**: Python Flask API (see `bridge/` directory)

## Author

**Dheeraj Aaditya**

GitHub: [@palmFronds](https://github.com/palmFronds)
LinkedIn: [Dheeraj Aaditya](https://www.linkedin.com/in/dheeraj-aaditya)