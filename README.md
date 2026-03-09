# 📊 Metrics Store

A production-style metrics store built on the modern data stack — demonstrating automated data ingestion, a multi-layer dbt pipeline, a local DuckDB warehouse, a live Streamlit dashboard, and an AI analytics agent powered by Claude.

**Author:** theotherbrandonsoto &nbsp;|&nbsp; [GitHub](https://github.com/theotherbrandonsoto) &nbsp;|&nbsp; [LinkedIn](https://www.linkedin.com/in/hirebrandonsoto/)

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
     ↓
Streamlit             dashboard.py          — live business dashboard
     ↓
Claude AI             AI analytics agent    — plain English Q&A on your metrics
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
| **pandas** | Data inspection and validation |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A [Kaggle account](https://www.kaggle.com) with an API token
- An [Anthropic account](https://console.anthropic.com) with an API key

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

This directly mirrors the modern data stack architecture used at companies like Airbnb, Uber, and LinkedIn.

---

*Dataset: [Customer Subscription Churn and Usage Patterns](https://www.kaggle.com/datasets/jayjoshi37/customer-subscription-churn-and-usage-patterns) via Kaggle*