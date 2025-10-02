# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an automated workflow system that reads daily summary emails from Outlook, analyzes them using Gemini AI, and sends the analysis results back via email. The system runs on a schedule (default: daily at 10 PM China Standard Time).

## Key Architecture

### Two-Part Structure

1. **Main Application** (`main.py`, `config.py`): Orchestrates the workflow
2. **Reusable Tools Package** (`workflow-tools/`): Modular components similar to n8n nodes

The workflow-tools package is designed for reusability across projects and provides base classes with concrete implementations for:
- **Email**: `OutlookClient` (Microsoft Graph API for reading, SMTP for sending)
- **AI Models**: `GeminiClient` (supports both old and new Google GenAI SDK versions)
- **Scheduler**: `APSchedulerClient` (cron-based scheduling)
- **Storage**: `R2Client` (Cloudflare R2), extensible to S3
- **Notes**: `NotionClient`, extensible to Obsidian

### Workflow Execution Pattern

The `DailySummaryWorkflow` class in `main.py` follows a 4-step process:
1. **Fetch emails** via Graph API (filters by subject "每日总结" and sender)
2. **Organize content** by sorting emails chronologically
3. **AI analysis** using Gemini with custom prompt from `config.py`
4. **Send results** via SMTP to configured recipient

Each step includes retry logic (3 attempts with 5-second delays) configured in `config.py`.

## Development Commands

### Installation

```bash
# Install workflow-tools package (run from workflow-tools directory)
cd workflow-tools
pip install -e .[all]
cd ..

# Install main application dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Start the scheduled workflow (runs daily at configured time)
python main.py
```

### Testing

To test the workflow once without scheduling, modify `main.py`:

```python
if __name__ == "__main__":
    workflow = DailySummaryWorkflow()
    workflow.initialize_clients()
    workflow.process_daily_summary()  # Direct execution
```

### Configuration

All configuration is centralized in `config.py` and `.env`:
- Email filters: `EMAIL_FILTER_SUBJECT`, `EMAIL_FILTER_SENDER`, `EMAIL_SEARCH_HOURS`
- Schedule: `SCHEDULE_HOUR`, `SCHEDULE_MINUTE`, `TIMEZONE`
- AI prompt: `AI_ANALYSIS_PROMPT`
- History tracking: `SAVE_HISTORY`, `HISTORY_LEVEL` (minimal/normal/detailed)

Environment variables must be set in `.env` (see `env.example` for template).

## Important Implementation Details

### Microsoft Graph API Authentication

Uses OAuth 2.0 client credentials flow with these required Azure AD app permissions:
- `Mail.Read` (required)
- `Mail.ReadWrite` (optional, for marking as read)

Admin consent must be granted in Azure Portal after configuring permissions.

### Email Filtering

The system uses strict filtering in `outlook_client.py`:
- Subject must exactly match `EMAIL_FILTER_SUBJECT`
- Sender must exactly match `EMAIL_FILTER_SENDER`
- Time range is last `EMAIL_SEARCH_HOURS` hours

### Gemini Client Compatibility

`GeminiClient` auto-detects SDK version:
- **New SDK** (`google-genai`): Better timeout control, uses `genai.Client()`
- **Old SDK** (`google-generativeai`): Falls back automatically

Settings are imported from `config.py` (main project) or use defaults if unavailable.

### History Tracking

Three levels configurable via `HISTORY_LEVEL`:
- `minimal`: timestamp, success status, email count
- `normal`: adds email subjects and summary preview (500 chars)
- `detailed`: full email bodies and complete analysis

Files saved as JSON in `history/` with timestamp in filename.

### Logging

Daily rotating logs in `logs/` directory:
- Format: `workflow_YYYYMMDD.log`
- Max size: 10MB per file
- Backup count: 5 files
- Encoding: UTF-8 (supports Chinese characters)

## Adding New Components

### New Email Provider

Extend `EmailClientBase` in `workflow-tools/workflow_tools/email/`:

```python
from .base.email_base import EmailClientBase

class GmailClient(EmailClientBase):
    # Implement required methods
    pass
```

### New AI Model

Extend `AIClientBase` in `workflow-tools/workflow_tools/ai_models/`:

```python
from .base.ai_client_base import AIClientBase

class OpenAIClient(AIClientBase):
    # Implement required methods
    pass
```

## Codacy Integration

This project uses Codacy for code quality. Per `.cursor/rules/codacy.mdc`:
- After editing files, run `codacy_cli_analyze` for each modified file
- After dependency changes, run `codacy_cli_analyze` with `tool: "trivy"` for security scanning
- Fixed repository: `gh/seatres/daily_summary_outlook`
