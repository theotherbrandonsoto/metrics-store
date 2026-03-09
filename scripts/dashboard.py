import streamlit as st
import duckdb
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Metrics Store Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── Connect to DuckDB ─────────────────────────────────────────
@st.cache_resource
def get_connection():
    return duckdb.connect(
        "/Users/brandon_soto/VS Code/metrics-store/data/metrics_store.duckdb"
    )

conn = get_connection()

# ── Load data ─────────────────────────────────────────────────
@st.cache_data
def load_metrics():
    return conn.execute("SELECT * FROM core_metrics").df()

@st.cache_data
def load_customers():
    return conn.execute("SELECT * FROM dim_customers").df()

@st.cache_data
def load_subscriptions():
    return conn.execute("SELECT * FROM fct_subscriptions").df()

metrics_df       = load_metrics()
customers_df     = load_customers()
subscriptions_df = load_subscriptions()

# ── Build agent context ───────────────────────────────────────
def build_system_prompt():
    metrics_data = metrics_df.to_string(index=False)
    tenure_counts = customers_df["tenure_segment"].value_counts().to_string()
    activity_counts = customers_df["activity_status"].value_counts().to_string()

    return f"""
You are an expert data analyst and business strategist with deep knowledge of
this SaaS metrics store project. You have access to the following live data.

== METRIC DEFINITIONS ==
- MRR: Sum of monthly_fee for active (non-churned) customers, grouped by plan
- Churn Rate: % of customers where is_churned = true, grouped by plan
- ARPU: Average monthly_fee among active customers
- Avg Weekly Usage Hours: Mean avg_weekly_usage_hours by plan (engagement metric)
- Avg Tenure: Mean tenure_months by plan
- At-Risk Customers: Customers with payment_failures > 0 AND last_login_days_ago > 30

== SCHEMA ==
stg_customers: user_id, signup_date, plan_type, monthly_fee,
               avg_weekly_usage_hours, support_tickets, payment_failures,
               tenure_months, last_login_days_ago, is_churned

dim_customers: user_id, signup_date, plan_type, monthly_fee, tenure_months,
               is_churned, tenure_segment (New/Established/Veteran),
               activity_status (Active/At Risk/Dormant)

fct_subscriptions: user_id, plan_type, monthly_fee, avg_weekly_usage_hours,
                   support_tickets, payment_failures, tenure_months,
                   last_login_days_ago, is_churned, is_at_risk

core_metrics (THE METRICS STORE): plan_type, mrr, active_customers,
                   avg_revenue_per_user, churn_rate_pct, churned_customers,
                   avg_weekly_usage_hours, avg_tenure_months,
                   avg_support_tickets, at_risk_customers

== LIVE METRICS DATA ==
{metrics_data}

== CUSTOMER SEGMENTS ==
Tenure Segments:
{tenure_counts}

Activity Status:
{activity_counts}

== ARCHITECTURE ==
This project is a metrics store built on the modern data stack:
CSV (Kaggle) → dbt (staging → marts → metrics) → DuckDB → Streamlit

You can answer questions about the metrics, explain what they mean in plain
English, and suggest business insights and strategic recommendations based on
the data. Be concise, direct, and always ground your answers in the actual
numbers above.
"""

# ── Anthropic client ──────────────────────────────────────────
@st.cache_resource
def get_anthropic_client():
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

client = get_anthropic_client()

# ── Header ────────────────────────────────────────────────────
st.title("📊 Metrics Store Dashboard")
st.caption("Powered by dbt + DuckDB · Single source of truth for all business metrics")
st.divider()

# ── Top KPIs ──────────────────────────────────────────────────
total_mrr       = metrics_df["mrr"].sum()
total_active    = metrics_df["active_customers"].sum()
total_churned   = metrics_df["churned_customers"].sum()
total_customers = total_active + total_churned
overall_churn   = round(100 * total_churned / total_customers, 2)
total_at_risk   = metrics_df["at_risk_customers"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total MRR",          f"${total_mrr:,.0f}")
k2.metric("Active Customers",   f"{total_active:,}")
k3.metric("Overall Churn Rate", f"{overall_churn}%")
k4.metric("At-Risk Customers",  f"{total_at_risk:,.0f}")

st.divider()

# ── Charts ────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.subheader("💰 MRR by Plan")
    st.bar_chart(metrics_df.set_index("plan_type")["mrr"], color="#4f8bf9")

with col2:
    st.subheader("📉 Churn Rate by Plan (%)")
    st.bar_chart(metrics_df.set_index("plan_type")["churn_rate_pct"], color="#f94f4f")

col3, col4 = st.columns(2)
with col3:
    st.subheader("⚡ Avg Weekly Usage Hours by Plan")
    st.bar_chart(metrics_df.set_index("plan_type")["avg_weekly_usage_hours"], color="#4ff9a0")

with col4:
    st.subheader("⚠️ At-Risk Customers by Plan")
    st.bar_chart(metrics_df.set_index("plan_type")["at_risk_customers"], color="#f9a84f")

st.divider()

# ── Full Metrics Table ─────────────────────────────────────────
st.subheader("📋 Full Metrics Store Output")
st.dataframe(
    metrics_df.style.format({
        "mrr":                    "${:,.0f}",
        "avg_revenue_per_user":   "${:,.2f}",
        "churn_rate_pct":         "{:.2f}%",
        "avg_weekly_usage_hours": "{:.2f}",
        "avg_tenure_months":      "{:.2f}",
        "avg_support_tickets":    "{:.2f}",
    }),
    use_container_width=True
)

st.divider()

# ── Customer Segments ──────────────────────────────────────────
st.subheader("👥 Customer Segments")
col5, col6 = st.columns(2)
with col5:
    tenure_counts = customers_df["tenure_segment"].value_counts().reset_index()
    tenure_counts.columns = ["segment", "count"]
    st.write("**By Tenure**")
    st.dataframe(tenure_counts, use_container_width=True, hide_index=True)

with col6:
    activity_counts = customers_df["activity_status"].value_counts().reset_index()
    activity_counts.columns = ["status", "count"]
    st.write("**By Activity Status**")
    st.dataframe(activity_counts, use_container_width=True, hide_index=True)

st.divider()

# ── AI Analytics Agent ─────────────────────────────────────────
st.subheader("🤖 AI Analytics Agent")
st.caption("Ask me anything about your metrics, what they mean, or what actions to take.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("e.g. Why is churn so high? Which plan should we focus on?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1024,
                system=build_system_prompt(),
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            reply = response.content[0].text
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

st.divider()
st.caption("Architecture: CSV → dbt (staging → marts → metrics) → DuckDB → Streamlit + Claude AI")