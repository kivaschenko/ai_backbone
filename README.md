# AI Backbone - Intelligent Business Automation System

A comprehensive AI agent system for automating business operations across CRM, finance, marketing, and operations platforms.

## Architecture

The system is built on five distinct layers:

### 1. Data Connectors Layer (`core/connectors/`)
Python services for pulling/pushing data from external platforms:
- **Zoho CRM** - Deals, contacts, activities
- **QuickBooks** - Invoices, payments, customers
- **Google Ads & Meta Ads** - Campaign performance
- **Time Doctor** - Time tracking and project data
- **Google Sheets** - Data import/export

### 2. Unified Data Layer (`core/database/`)
PostgreSQL database with normalized schemas:
- `crm_*` tables - CRM data
- `finance_*` tables - Financial data
- `marketing_*` tables - Advertising data
- `operations_*` tables - Time tracking data

### 3. Event & Orchestration Layer (`core/orchestration/`)
Background task management:
- **Scheduler** - Cron-based and interval-based job scheduling
- **Task Queue** - Asynchronous task execution with retry logic
- **Workflow** - Multi-step process orchestration with dependencies

### 4. AI Agents Layer (`core/agents/`)
Specialized agents with LLM capabilities:
- **CRM Agent** - Sales pipeline analysis and deal insights
- **Finance Agent** - Cash flow analysis and AR management
- **Marketing Agent** - Campaign performance and ROAS optimization
- **Operations Agent** - Time tracking and project profitability

### 5. Dashboard & API Layer (`core/api/`)
RESTful API endpoints:
- Agent analysis endpoints
- Data sync triggers
- Scheduler management
- Real-time cohort dashboards

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- API credentials for integrated platforms

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai_backbone
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Initialize database:
```bash
python scripts/init_db.py
```

6. Start the API server:
```bash
python -m core.api.main
```

The API will be available at `http://localhost:8000`

## Usage Examples

### Analyzing CRM Data

```python
from core.agents.crm_agent import CRMAgent

# Initialize agent
agent = CRMAgent(
    agent_id="crm_1",
    llm_config={
        "model": "gpt-4",
        "api_key": "your-api-key"
    }
)

# Analyze deals
result = agent.process({
    "deals": [...],  # Your deal data
    "query": "What are the top at-risk deals this month?"
})

print(result["insights"])
```

### Scheduling Data Syncs

```python
from core.orchestration.scheduler import scheduler

# Schedule Zoho CRM sync every hour
scheduler.add_interval_job(
    job_id="zoho_sync",
    func=sync_zoho_crm,
    hours=1
)

# Schedule daily financial report at 9 AM
scheduler.add_cron_job(
    job_id="daily_report",
    func=generate_financial_report,
    hour="9",
    minute="0"
)

scheduler.start()
```

### Creating Workflows

```python
from core.orchestration.workflow import Workflow

# Create multi-step workflow
workflow = Workflow(workflow_id="monthly_analysis", name="Monthly Business Analysis")

workflow.add_step("fetch_crm", "Fetch CRM Data", fetch_crm_data)
workflow.add_step("fetch_finance", "Fetch Finance Data", fetch_finance_data)
workflow.add_step("analyze", "AI Analysis", run_analysis, depends_on=["fetch_crm", "fetch_finance"])
workflow.add_step("report", "Generate Report", create_report, depends_on=["analyze"])

# Execute workflow
workflow.execute()
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Agent Analysis
```bash
POST /agents/crm/analyze
POST /agents/finance/analyze
POST /agents/marketing/analyze
POST /agents/operations/analyze
```

### Data Sync
```bash
POST /sync/zoho-crm
POST /sync/quickbooks
POST /sync/ads
POST /sync/time-doctor
```

### Dashboard
```bash
GET /dashboard/cohort/overview
GET /dashboard/metrics/realtime
```

## Configuration

Configuration is managed through environment variables or a config file. See `.env.example` for all available options.

Key configurations:
- Database connection
- LLM provider and API keys
- Platform API credentials
- Scheduler settings
- Logging preferences

## Development

### Project Structure
```
ai_backbone/
├── core/
│   ├── connectors/       # Data integration layer
│   ├── database/         # Database models and connection
│   ├── orchestration/    # Scheduling and task management
│   ├── agents/          # AI agents
│   ├── api/             # REST API endpoints
│   └── utils/           # Utilities and helpers
├── tests/               # Test suite
├── scripts/             # Utility scripts
├── logs/                # Application logs
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template
```

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black core/

# Lint code
flake8 core/

# Type checking
mypy core/
```

## Key Features

✅ **Multi-Platform Integration** - Connect to CRM, accounting, ads, and time tracking systems
✅ **Unified Data Model** - Normalized schemas for cross-platform analysis
✅ **AI-Powered Insights** - LLM-based agents for intelligent analysis
✅ **Automated Workflows** - Schedule and orchestrate complex business processes
✅ **Real-Time Dashboards** - Cohort analysis across all business metrics
✅ **Extensible Architecture** - Easy to add new connectors and agents

## Roadmap

- [ ] Add more platform connectors (HubSpot, Stripe, etc.)
- [ ] Implement real-time webhooks
- [ ] Build interactive dashboard UI
- [ ] Add agent memory persistence
- [ ] Implement multi-agent collaboration
- [ ] Add ML models for predictive analytics

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

[Your License Here]

## Support

For questions or issues, please open an issue on GitHub or contact [your-email@example.com]
