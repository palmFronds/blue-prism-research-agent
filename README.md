# AI Research Assistant - Blue Prism RPA
Automated research assistant that searches Google, extracts content from top results, and synthesizes comprehensive research reports.

![Process Flow](docs/workflow_diagram.png)

## 🎯 Features

- **Automated Web Research**: Launches browser, executes Google searches, navigates to top results
- **Intelligent Content Extraction**: Custom HTML parsing for Google results and article content
- **AI-Powered Synthesis**: Integrates with OpenAI GPT-5-nano for multi-source analysis
- **Professional Output**: Generates formatted reports with citations

## 🏗️ Architecture

[Google Search] → [Parse Results] → [Extract Content] 
                        ↓
                  [AI Analysis] → [Generate Report]

**Tech Stack:**
- Blue Prism 7.x (RPA Platform)
- OpenAI GPT-5-nano API
- C# .NET (Code Stages)
- Chrome/Edge Browser Automation

## 📋 Prerequisites

- Blue Prism 7.0+ installed
- OpenAI API account & key
- Chrome or Edge browser
- Windows 10/11
- .NET Framework 4.7.2+

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ai-research-rpa.git
cd ai-research-rpa
```

### 2. Import to Blue Prism
1. Open Blue Prism
2. File → Import → Release Package
3. Select `blueprism/AI_Research_Assistant.bprelease`
4. Import all dependencies

### 3. Configure
1. Open Process: "AI Research Assistant"
2. Navigate to **Config** page
3. Set data items:
   - `api_key`: Your OpenAI API key
   - `search_query`: Topic to research
   - `output_directory`: Where to save reports

### 4. Run Demo
```
Process → Run
Monitor in Control Room
Check output in C:\AI_Research_Reports\
```

## 📖 Documentation

- [Setup Guide](config/setup_instructions.md) - Detailed installation
- [Architecture](docs/architecture.md) - System design & decisions
- [API Integration](docs/api_integration.md) - OpenAI integration details
- [Demo Guide](docs/demo_guide.md) - Running the demonstration

## 🎬 Demo

**Watch 3-minute demo:** [demo/demo_video.mp4](demo/demo_video.mp4)
**Sample Outputs:** Check [sample_outputs/](sample_outputs/) for example reports

## 🔧 Key Technical Decisions

### Why Blue Prism?
- Enterprise-grade RPA platform
- Strong exception handling
- Centralized control room
- Object-based reusability

### Why GPT-5-nano Batch API?
- 400k token context window (fits 5+ full articles)
- Cost-effective for research synthesis
- Asynchronous processing for scale

### Custom HTML Parsing vs. OCR
- Google's consistent structure allows reliable CSS selectors
- Faster than OCR/vision models
- More accurate text extraction

## 📊 Performance

| Metric | Value |
|--------|-------|
| Avg. Runtime | 60-90 seconds |
| Sources Analyzed | 5 per query |
| Success Rate | 95%+ |
| Token Usage | ~50k-100k per report |

**Your Name**
- GitHub: [@palmFronds](https://github.com/palmFronds)
- LinkedIn: [Dheeraj Aaditya](https://www.linkedin.com/in/dheeraj-aaditya/)