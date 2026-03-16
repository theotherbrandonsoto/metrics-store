# 📊 Metrics Store

A production-style metrics store built on the modern data stack — demonstrating automated data ingestion, a multi-layer dbt pipeline, a local DuckDB warehouse, a live Streamlit dashboard, an AI analytics agent powered by Claude, and an MCP server for direct Claude Desktop connectivity.

**Author:** theotherbrandonsoto &nbsp;|&nbsp; [GitHub](https://github.com/theotherbrandonsoto) &nbsp;|&nbsp; [LinkedIn](https://www.linkedin.com/in/hirebrandonsoto/)
| *Built with assistance from Claude.*
---

## 📌 Executive Summary

### The Business Problem
Most BI dashboards are built for analysts. Non-technical stakeholders — executives, CS leads, ops managers — either wait for someone to pull numbers for them or learn to live without the data entirely. The result is a bottleneck: one analyst fielding the same ad-hoc questions on repeat while the people who need answers most can't get them independently.

### The Solution
This project layers a conversational AI interface on top of a production-style metrics store. Stakeholders can ask plain-English questions directly against live DuckDB data — either through a Streamlit dashboard or via Claude Desktop using an MCP server — and get immediate, context-aware answers without writing a single query.

### Project Impact
When non-technical stakeholders can ask questions directly, analysts get their time back. Instead of fielding requests like "what's our churn rate by plan?" or "which customers are most at risk?", those answers are available on demand — in plain English, from the same verified metrics layer that powers the dashboard. Data access stops being a bottleneck and becomes a self-serve resource.

### Next Steps
In a production environment, the MCP server would connect to a cloud warehouse (Snowflake, BigQuery) rather than a local DuckDB file, with role-based access controls determining which metrics each user can query. Planned feature additions include multi-turn conversation memory so stakeholders can ask follow-up questions in context, and a query audit log so analysts can see what questions are being asked most — and use that signal to prioritize future dashboard builds.

---

## 🧠 What is a Metrics Store?

A metrics store is a middle layer between upstream data sources and downstream business applications. Rather than defining metrics independently in every BI tool, report, or pipeline, a metrics store establishes a **single source of truth** — metrics are defined once and reused everywhere.

This project implements that architecture at small scale, mirroring the approach used by companies like Airbnb, Uber, and LinkedIn.

---

## 🏗️ Architecture

```
Kaggle API  (automated ingestion)
     ↓
data/raw/   (CSV landing zone)
     ↓
dbt staging layer     stg_customers         — clean types, rename columns
dbt marts layer       dim_customers         — customer segments & attributes
                      fct_subscriptions     — subscription facts & risk flags
dbt metrics layer     core_metrics          — THE metrics store
     ↓
DuckDB                metrics_store.duckdb  — local analytical warehouse
     ↓  ↓
Streamlit             dashboard.py          — live business dashboard + AI chat
MCP Server            mcp-server-duckdb     — Claude Desktop direct connectivity
```

---

## 📐 dbt Layer Design

| Layer | Model | Purpose |
|---|---|---|
| Staging | `stg_customers` | Reads raw CSV, casts types, renames columns |
| Marts | `dim_customers` | One row per customer with tenure & activity segments |
| Marts | `fct_subscriptions` | Subscription facts including payment health & at-risk flag |
| Metrics | `core_metrics` | Aggregated metrics store — MRR, churn, engagement, risk |

---

## 📈 Metrics Defined

| Metric | Definition |
|---|---|
| **MRR** | Sum of `monthly_fee` for all active (non-churned) customers |
| **Churn Rate** | % of customers where `churn = Yes`, grouped by plan |
| **Avg Revenue Per User** | Mean `monthly_fee` among active customers |
| **Avg Weekly Usage Hours** | Mean `avg_weekly_usage_hours` by plan |
| **Avg Tenure** | Mean `tenure_months` by plan and churn status |
| **At-Risk Customers** | Customers with `payment_failures > 0` AND `last_login_days_ago > 30` |

---

## 🤖 AI Analytics Agent

The dashboard includes a natural language analytics agent powered by the Claude API. The agent has full awareness of:

- Every metric definition and how it is calculated
- The complete data schema across all dbt layers
- Live numbers pulled directly from DuckDB at runtime

Example questions you can ask:
- *"Why is churn so high?"*
- *"Which plan should we focus on?"*
- *"What does MRR tell us about the business?"*
- *"Which customers are most at risk and what should we do about it?"*

This turns the metrics store from a static dashboard into an interactive decision-support tool.

---

## 🔌 MCP Server — Claude Desktop Integration

This project includes a Model Context Protocol (MCP) server that connects Claude Desktop directly to the DuckDB warehouse. This means you can query your live metrics in plain English from Claude Desktop without opening the dashboard.

### Setup

**Prerequisites:** `uv` installed (`brew install uv`)

Add the following to your Claude Desktop config at `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "duckdb": {
      "command": "uvx",
      "args": [
        "mcp-server-duckdb",
        "--db-path",
        "/path/to/your/metrics-store/data/metrics_store.duckdb"
      ]
    }
  }
}
```

Restart Claude Desktop — the DuckDB connector will appear in the tools panel automatically.

### Example queries in Claude Desktop
- *"What tables are in my metrics store?"*
- *"What is the MRR for each plan?"*
- *"Which plan has the highest churn rate?"*
- *"Show me all at-risk customers by plan"*

---

## 🔍 Key Insights from the Data

- **Total MRR: ~$517K** across 1,195 active customers
- **Churn rate is ~57-58% uniformly across all plan types** — suggesting churn is a product-level problem, not a pricing or plan problem
- **~1,150 customers are classified as at-risk** across all plans, indicating a broad engagement issue requiring intervention
- Usage hours are consistent across plans (~12-13 hrs/week), meaning higher-paying customers are not more engaged

---

## 🛠️ Tech Stack

| Tool | Role |
|---|---|
| **Python** | Ingestion script, Streamlit dashboard, agent orchestration |
| **Kaggle API** | Automated dataset download |
| **dbt Core** | Data transformation and metrics layer |
| **DuckDB** | Local analytical warehouse |
| **Streamlit** | Business intelligence dashboard |
| **Claude API** | AI analytics agent (natural language Q&A) |
| **MCP Server** | Claude Desktop direct connectivity via `mcp-server-duckdb` |
| **pandas** | Data inspection and validation |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A [Kaggle account](https://www.kaggle.com) with an API token
- An [Anthropic account](https://console.anthropic.com) with an API key
- [Claude Desktop](https://claude.ai/download) (optional, for MCP integration)
- `uv` installed (optional, for MCP integration)

### 1. Clone the repo
```bash
git clone https://github.com/theotherbrandonsoto/metrics-store.git
cd metrics-store
```

### 2. Set up virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add credentials
Create a `.env` file in the project root:
```
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 4. Download the dataset
```bash
python scripts/ingest.py
```

### 5. Run the dbt pipeline
```bash
cd dbt_project
dbt run
dbt test
cd ..
```

### 6. Launch the dashboard
```bash
streamlit run scripts/dashboard.py
```

Open `http://localhost:8501` in your browser.

### 7. (Optional) Enable Claude Desktop MCP integration
Follow the MCP Server setup instructions above, then restart Claude Desktop.

---

## 📁 Project Structure

```
metrics-store/
├── data/
│   ├── raw/                  ← Kaggle data lands here (gitignored)
│   └── metrics_store.duckdb  ← DuckDB warehouse (gitignored)
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_customers.sql
│   │   │   └── schema.yml
│   │   ├── marts/
│   │   │   ├── dim_customers.sql
│   │   │   ├── fct_subscriptions.sql
│   │   │   └── schema.yml
│   │   └── metrics/
│   │       ├── core_metrics.sql
│   │       └── schema.yml
│   ├── tests/
│   │   └── assert_mrr_is_positive.sql
│   └── dbt_project.yml
├── scripts/
│   ├── ingest.py             ← Kaggle API download script
│   └── dashboard.py          ← Streamlit dashboard + AI agent
├── .env.example              ← Credential template (safe to commit)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧪 Data Quality Tests

19 dbt tests run automatically against the pipeline covering:

- **Uniqueness** — `user_id` is unique across all models
- **Not null** — key columns are never empty
- **Accepted values** — `plan_type`, `tenure_segment`, and `activity_status` only contain valid values
- **Custom assertion** — MRR is always a positive number

Run tests at any time with:
```bash
cd dbt_project
dbt test
```

---

## 💡 Why This Project?

Most portfolio data projects stop at a notebook or a dashboard. This project is intentionally architected like a **production data system**:

- **Separation of concerns** — ingestion, transformation, and serving are decoupled
- **Metrics as code** — business logic lives in version-controlled SQL, not buried in a BI tool
- **Reusability** — the metrics layer can serve a dashboard, an API, or a downstream pipeline without redefining logic
- **Freshness** — the Kaggle API integration means the pipeline can be re-run anytime to pull the latest data
- **AI-augmented** — the Claude integration demonstrates how a metrics store can power intelligent, conversational analytics
- **MCP-connected** — the MCP server exposes the warehouse as a live tool for AI agents, reflecting the cutting edge of the agentic data stack

This directly mirrors the modern data stack architecture used at companies like Airbnb, Uber, and LinkedIn.

---

*Dataset: [Customer Subscription Churn and Usage Patterns](https://www.kaggle.com/datasets/jayjoshi37/customer-subscription-churn-and-usage-patterns) via Kaggle*
