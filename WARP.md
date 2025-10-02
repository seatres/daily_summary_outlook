# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is an automated workflow system that processes daily summary emails from Outlook, analyzes them using Gemini AI, and sends analysis results back via email. The system runs on a configurable schedule (default: 10 PM China Standard Time) and supports multiple email providers.

### Quick Navigation
- [Essential Commands](#essential-commands)
- [System Architecture](#system-architecture)
- [Development Workflow](#development-workflow)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Essential Commands

### Setup & Installation
```bash
# Install the workflow-tools package (must be done first)
cd workflow-tools
pip install -e .[all]
cd ..

# Install main application dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp env.example .env
# Edit .env with your credentials
```

### Run the Application
```bash
# Start the scheduled workflow (runs continuously)
python main.py

# Test single execution without scheduling (modify main.py temporarily)
# Change main.py to call workflow.process_daily_summary() directly
```

### Testing
```bash
# Test Outlook IMAP connection
python tests/test_outlook_imap.py

# Test QQ email connection  
python tests/test_qq_email.py

# Verify installation and configuration
chmod +x scripts/test_installation.sh
./scripts/test_installation.sh
```

### Deployment (macOS)
```bash
# Install as LaunchD service for automatic scheduling
chmod +x scripts/install_launchd.sh
./scripts/install_launchd.sh

# Check service status
launchctl list | grep dailysummary

# View service logs
tail -f logs/launchd_out.log
tail -f logs/launchd_err.log
```

### Monitoring & Logs
```bash
# View today's workflow logs
tail -f logs/workflow_$(date +%Y%m%d).log

# List all log files
ls -lh logs/

# View execution history
ls -lt history/ | head -5

# View specific history record
cat history/history_YYYYMMDD_HHMMSS.json
```

### Development Tools
```bash
# Validate workflow-tools configuration
cd workflow-tools
python validate_config.py

# Validate dependencies
python validate_dependencies.py

# Run Codacy analysis (if configured)
.codacy/cli.sh --tool="ruff" --directory="."
```

## System Architecture

### Two-Tier Architecture

**Main Application Layer** (`main.py`, `config.py`):
- `DailySummaryWorkflow` class orchestrates the 4-step process
- Centralized configuration management in `config.py`
- Comprehensive logging and history tracking

**Reusable Tools Layer** (`workflow-tools/`):
- Modular components designed like n8n nodes
- Base classes with concrete implementations
- Cross-project reusability

### Core Data Flow
```
Email Provider → Email Client → Content Organization → AI Analysis → SMTP Delivery
     ↓              ↓               ↓                    ↓            ↓
  (IMAP/Graph) → (Filtering) → (Chronological) → (Gemini 2.5) → (Results)
```

### Supported Email Client Types

1. **`imap`**: Outlook personal accounts (@outlook.com, @hotmail.com)
   - Uses IMAP for reading, SMTP for sending
   - Requires app-specific password

2. **`graph`**: Outlook organizational accounts  
   - Microsoft Graph API (OAuth) for reading
   - Requires Azure AD app registration with `Mail.Read` permission

3. **`qq`**: QQ email (@qq.com)
   - Pre-configured IMAP/SMTP servers
   - Uses authorization code (not password)

4. **`generic`**: Any IMAP-compatible provider
   - Manual IMAP/SMTP server configuration required

### Key Modules

**workflow-tools/workflow_tools/**:
- `email/`: Email client implementations with base classes
- `ai_models/`: AI client implementations (currently Gemini)
- `scheduler/`: APScheduler-based task scheduling
- `storage/`: Storage clients (Cloudflare R2, extensible to S3)  
- `notes/`: Notes integration (Notion, extensible to Obsidian)
- `utils/`: Common utilities (config, caching, file operations)
- `exceptions/`: Custom exception hierarchies for each module

### Email Processing Logic

Email filtering uses strict criteria defined in `config.py`:
- Subject must contain `EMAIL_FILTER_SUBJECT` (default: "每日记录")
- Sender must contain `EMAIL_FILTER_SENDER` 
- Time range: last `EMAIL_SEARCH_HOURS` hours (default: 24)

### AI Integration

`GeminiClient` auto-detects SDK version:
- **New SDK** (`google-genai`): Better timeout control
- **Old SDK** (`google-generativeai`): Automatic fallback
- Custom analysis prompt defined in `config.py`

### History Tracking

Three configurable levels via `HISTORY_LEVEL`:
- `minimal`: timestamp, success status, email count  
- `normal`: adds email subjects and summary preview (500 chars)
- `detailed`: full email bodies and complete analysis

## Development Workflow

### Configuration Priority
1. Environment variables in `.env` file
2. Default values in `config.py` 
3. Workflow-tools internal defaults

### Email Client Selection
Set `EMAIL_CLIENT_TYPE` in `.env` to choose client implementation:
- Each type requires different credential configuration
- Graph API requires Azure AD app setup with admin consent
- IMAP clients need app-specific passwords

### Testing Email Connections
Before running the full workflow, test individual email connections:
```bash
# Test your chosen email provider
python tests/test_outlook_imap.py  # for imap/graph types
python tests/test_qq_email.py      # for qq type
```

### Retry Logic
All major operations include retry mechanisms:
- 3 attempts with 5-second delays (configurable in `config.py`)
- Applies to email fetching, AI analysis, and email sending

### Adding New Components

**New Email Provider**:
```python
# In workflow-tools/workflow_tools/email/
from .base.email_base import EmailClientBase

class NewEmailClient(EmailClientBase):
    # Implement required methods
    pass
```

**New AI Model**:
```python  
# In workflow-tools/workflow_tools/ai_models/
from .base.ai_client_base import AIClientBase

class OpenAIClient(AIClientBase):
    # Implement required methods
    pass
```

## Configuration

### Environment Variables Required
```bash
# Email client type selection
EMAIL_CLIENT_TYPE=imap  # or graph, qq, generic

# Outlook settings (for imap/graph types)
OUTLOOK_EMAIL=your-email@outlook.com
OUTLOOK_IMAP_PASSWORD=your-app-password
OUTLOOK_SMTP_PASSWORD=your-app-password

# Graph API settings (for graph type only)
OUTLOOK_CLIENT_ID=your-client-id
OUTLOOK_CLIENT_SECRET=your-client-secret  
OUTLOOK_TENANT_ID=your-tenant-id

# Generic IMAP settings (for generic type only)
EMAIL_ADDRESS=your-email@domain.com
EMAIL_PASSWORD=your-password
IMAP_SERVER=imap.domain.com
SMTP_SERVER=smtp.domain.com

# AI configuration
GEMINI_API_KEY=your-gemini-api-key

# Email filtering
EMAIL_FILTER_SENDER=sender@domain.com
SUMMARY_RECIPIENT=recipient@domain.com

# Optional settings
SAVE_HISTORY=true
HISTORY_LEVEL=detailed  # minimal, normal, detailed
LOG_LEVEL=INFO
```

### Schedule Configuration
Configure in `config.py`:
- `TIMEZONE`: Default "Asia/Shanghai" 
- `SCHEDULE_HOUR`: Default 22 (10 PM)
- `SCHEDULE_MINUTE`: Default 0

## Troubleshooting

### Email Connection Issues
```bash
# Test credentials with specific email client
python tests/test_outlook_imap.py

# Check if IMAP/SMTP settings are correct
# Verify app-specific passwords for personal accounts
# Ensure Azure AD permissions granted for Graph API
```

### AI Analysis Failures  
```bash
# Verify API key is valid
# Check API quota in Google Cloud Console
# Review network connectivity to Gemini API
```

### Scheduling Problems
```bash
# Check if LaunchD service is loaded
launchctl list | grep dailysummary

# View service logs for errors
tail -f logs/launchd_err.log

# Verify timezone configuration in config.py
```

### Dependency Issues
```bash
# Validate workflow-tools installation
cd workflow-tools
python validate_dependencies.py

# Reinstall with all extras  
pip install -e .[all]
```

### Log Analysis
```bash
# Filter for errors in today's log
grep -i error logs/workflow_$(date +%Y%m%d).log

# View full execution trace
grep -A 10 -B 5 "开始执行每日总结任务" logs/workflow_$(date +%Y%m%d).log
```

## Key Files Reference

- **`main.py`**: Application entry point and workflow orchestration
- **`config.py`**: Centralized configuration with environment variable loading
- **`.env`**: Environment-specific settings (copy from `env.example`)
- **`workflow-tools/`**: Reusable component library
- **`tests/`**: Integration tests for email clients
- **`scripts/`**: Deployment and maintenance scripts
- **`docs/`**: Comprehensive documentation in Chinese
- **`logs/`**: Daily rotating log files  
- **`history/`**: JSON execution history files

For detailed documentation, see `README.md`, `CLAUDE.md`, and files in the `docs/` directory.