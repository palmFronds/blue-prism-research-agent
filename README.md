# Simple AI Research Assistant – Blue Prism RPA

Automated research assistant that performs end-to-end web research and prepares structured, AI-ready prompts from multiple sources.

> **⚠️ Current Status**  
> ✅ **Complete & Functional**: Browser automation, search execution, content extraction, cleaning, aggregation, and JSON request formatting—everything up to the chat API interface works  
> ⏳ **Under Construction**: Chat API integration (API call execution and response handling) + Project-wide Exception Handling

![Process Flow](bridge/Process%20Structure.png)

---

## Overview

This project implements a production-style research pipeline in **Blue Prism**. The system executes autonomous research runs from a seed URL, leveraging browser automation, content extraction, and AI-powered analysis to generate comprehensive research reports.

The research controller orchestrates the entire workflow: launching a browser, scraping search results, extracting and cleaning content from multiple pages, formatting prompts for AI analysis, and generating final reports. Results live in memory and logs for real-time inspection and debugging.

---

## Process Flow

The system follows a structured workflow:

**1. Initialization**
- Accepts process inputs: `Research_Question`, `Num_Pages`, `Max_Results`, and `Result_Count`
- Launches browser automation instance

**2. Browser Scraping**
- Executes initial scraping operations
- Retrieves search results and URLs

**3. Extraction Loop**
- Navigates to each URL in the result set
- Extracts raw HTML content
- Cleans and normalizes article text
- Adds processed content to in-memory collection
- Iterates through URLs until page count limit is reached

**4. AI Client** *(Formatting: ✅ Complete | API Integration: ⏳ Under Construction)*
- ✅ Formats aggregated content into structured prompt
- ✅ Constructs OpenAI-compatible JSON request
- ⏳ Executes API call to AI model (GPT-5-nano): *under construction*
- ⏳ Processes AI response: *under construction*

**5. Output**
- ⏳ Generates final research report: *pending AI integration*
- ✅ Returns structured JSON payload (ready for API call)

---

## Features

- **Deterministic Browser Automation**: Chrome/Edge automation without OCR dependencies
- **Robust Content Extraction**: Custom HTML parsing with error handling
- **In-Memory Processing**: All data aggregation occurs in memory, no disk writes during execution
- **Structured AI Integration**: Fully formatted OpenAI-compatible JSON requests
- **Error Resilience**: Per-page failure containment with comprehensive logging
- **Debug-Friendly**: Real-time inspection of data items and process state

---

## Tech Stack

- **RPA Platform**: Blue Prism 7.x
- **Code Language**: C# .NET (Code Stages)
- **Browser Automation**: Chrome / Edge
- **AI Model**: OpenAI GPT-5-nano
- **Bridge Service**: Python Flask API (see `bridge/` directory)

## Author

**Dheeraj Aaditya**  
GitHub: [@palmFronds](https://github.com/palmFronds)  
LinkedIn: [Dheeraj Aaditya](https://www.linkedin.com/in/dheeraj-aaditya)