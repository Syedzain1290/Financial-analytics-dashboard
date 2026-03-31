# ============================================================
# 💚  Financial Transactions Dashboard
# ============================================================
# Perfectly configured for:
#   Banking_Transactions_USA_2023_2024.csv
#
# Install:
#   pip install streamlit pandas numpy plotly
#
# Run:
#   streamlit run financial_analytics_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Banking Transactions Dashboard USA 2023-2024 ",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@700&display=swap');

    .stApp { background-color: #f8fafc; color: #1e293b; }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    #MainMenu, footer, header { visibility: hidden; }

    [data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    [data-testid="metric-container"] label {
        color: #64748b !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }

    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 1.6rem !important;
    }

    .section-title {
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        color: #16a34a;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }

    .dashboard-header {
        background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(22,163,74,0.08);
    }

    .header-title {
        font-family: 'Space Mono', monospace;
        font-size: 1.4rem;
        font-weight: 700;
        color: #16a34a;
    }

    .header-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD & PREPARE DATA — matched to your CSV columns
# ============================================================

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)

    # ── Your CSV columns mapped to dashboard standard names ──
    df.rename(columns={
        "Transaction_Date":   "date",
        "Transaction_Amount": "amount",
        "Category":           "type",
        "Transaction_Status": "status",
        "Fraud_Flag":         "fraud_raw",
        "City":               "city",
        "Payment_Method":     "payment_method",
        "Customer_Age":       "age",
        "Customer_Gender":    "gender",
        "Customer_Income":    "income",
        "Transaction_Type":   "debit_credit",
    }, inplace=True)

    # Parse dates
    df["date"]     = pd.to_datetime(df["date"], errors="coerce")
    df["month"]    = df["date"].dt.to_period("M").astype(str)
    df["day_name"] = df["date"].dt.day_name()
    df["hour"]     = df["date"].dt.hour

    # Convert Fraud_Flag: "Yes" → 1, "No" → 0
    df["is_fraud"] = df["fraud_raw"].map({"Yes": 1, "No": 0}).fillna(0).astype(int)

    # Clean amount
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0).abs()

    return df

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 💚 Financial Transactions Dashboard")
    st.markdown("---")
    uploaded = st.file_uploader(
        "Upload your dataset (.csv)",
        type=["csv"],
        help="Upload Banking_Transactions_USA_2023_2024.csv"
    )
    st.markdown("---")
    st.markdown("### 🔍 Filters")

# ============================================================
# LOAD DATA
# ============================================================

if uploaded:
    df = load_data(uploaded)
else:
    try:
        df = load_data("Banking_Transactions_USA_2023_2024.csv")
        st.sidebar.success("✅ Dataset loaded automatically!")
    except:
        st.sidebar.warning("⬆️ Please upload your CSV file above!")
        st.stop()

# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:
    months_available = sorted(df["month"].unique())
    selected_months  = st.multiselect(
        "Select Months",
        options=months_available,
        default=months_available[-3:] if len(months_available) >= 3 else months_available
    )

    types_available = sorted(df["type"].unique())
    selected_types  = st.multiselect(
        "Categories",
        options=types_available,
        default=types_available
    )

    min_amt   = int(df["amount"].min())
    max_amt   = int(df["amount"].max())
    amt_range = st.slider(
        "Amount Range ($)",
        min_value=min_amt,
        max_value=max_amt,
        value=(min_amt, max_amt)
    )

    show_fraud = st.checkbox("Show Fraud Only", value=False)

    st.markdown("---")
    st.markdown(
        "<div style='font-family:Inter;font-size:0.75rem;color:#64748b'>"
        "</div>",
        unsafe_allow_html=True
    )

# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df[
    (df["month"].isin(selected_months)) &
    (df["type"].isin(selected_types)) &
    (df["amount"] >= amt_range[0]) &
    (df["amount"] <= amt_range[1])
]
if show_fraud:
    filtered = filtered[filtered["is_fraud"] == 1]

if len(filtered) == 0:
    st.warning("No data matches your filters. Please adjust the sidebar filters.")
    st.stop()

# ============================================================
# HEADER
# ============================================================

st.markdown(f"""
<div class="dashboard-header">
    <div>
        <div class="header-title">💚 Financial Transactions Dashboard USA 2023-2024/div>
        <div class="header-subtitle">Real-time transaction monitoring & fraud intelligence · {len(df):,} transactions loaded</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# ROW 1 — KPI METRICS
# ============================================================

st.markdown('<div class="section-title">📊 Key Metrics</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

total_txns   = len(filtered)
total_volume = filtered["amount"].sum()
avg_txn      = filtered["amount"].mean()
fraud_count  = filtered["is_fraud"].sum()
fraud_rate   = (fraud_count / total_txns * 100) if total_txns > 0 else 0
success_rate = (filtered[filtered["status"] == "Success"].shape[0] / total_txns * 100)
avg_income   = filtered["income"].mean()

with col1: st.metric("Total Transactions", f"{total_txns:,}")
with col2: st.metric("Total Volume",       f"${total_volume/1e6:.2f}M")
with col3: st.metric("Avg Transaction",    f"${avg_txn:,.0f}")
with col4: st.metric("Fraud Detected",     f"{fraud_count:,}",
                     delta=f"{fraud_rate:.2f}% rate", delta_color="inverse")
with col5: st.metric("Success Rate",       f"{success_rate:.1f}%")
with col6: st.metric("Avg Income",         f"${avg_income:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# ROW 2 — TRANSACTION TRENDS
# ============================================================

st.markdown('<div class="section-title">📈 Transaction Trends</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])

with col_left:
    monthly = filtered.groupby("month").agg(
        total_amount=("amount", "sum"),
        count=("amount", "count")
    ).reset_index()

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(
        go.Bar(x=monthly["month"], y=monthly["total_amount"],
               name="Volume ($)", marker_color="#3fb950", opacity=0.8),
        secondary_y=False
    )
    fig_trend.add_trace(
        go.Scatter(x=monthly["month"], y=monthly["count"],
                   name="# Transactions",
                   line=dict(color="#58a6ff", width=2),
                   mode="lines+markers"),
        secondary_y=True
    )
    fig_trend.update_layout(
        title="Monthly Transaction Volume & Count",
        paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
        font=dict(color="#64748b", family="Inter"),
        legend=dict(bgcolor="#ffffff"),
        margin=dict(t=40, b=20, l=10, r=10), height=320
    )
    fig_trend.update_xaxes(gridcolor="#e2e8f0", tickangle=45)
    fig_trend.update_yaxes(gridcolor="#e2e8f0", secondary_y=False, title_text="Volume ($)")
    fig_trend.update_yaxes(gridcolor="#e2e8f0", secondary_y=True,  title_text="Count")
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    cat_counts = filtered["type"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]

    fig_donut = px.pie(
        cat_counts, values="count", names="category",
        hole=0.55,
        color_discrete_sequence=px.colors.sequential.Greens_r,
        title="Spending by Category"
    )
    fig_donut.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
        font=dict(color="#64748b", family="Inter"),
        margin=dict(t=40, b=10, l=10, r=10), height=320,
        legend=dict(bgcolor="#ffffff", font=dict(size=9))
    )
    fig_donut.update_traces(textfont_color="#1e293b")
    st.plotly_chart(fig_donut, use_container_width=True)

# ============================================================
# ROW 3 — FRAUD ANALYSIS
# ============================================================

st.markdown('<div class="section-title">🚨 Fraud Intelligence</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    fraud_monthly = filtered.groupby("month")["is_fraud"].sum().reset_index()
    fraud_monthly.columns = ["month", "fraud_count"]
    fig_fraud = px.bar(
        fraud_monthly, x="month", y="fraud_count",
        title="Fraud Cases Per Month",
        color_discrete_sequence=["#f87171"]
    )
    fig_fraud.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
        font=dict(color="#64748b", family="Inter"),
        margin=dict(t=40, b=20, l=10, r=10), height=280, showlegend=False
    )
    fig_fraud.update_xaxes(gridcolor="#e2e8f0", tickangle=45)
    fig_fraud.update_yaxes(gridcolor="#e2e8f0")
    st.plotly_chart(fig_fraud, use_container_width=True)

with col2:
    fraud_cat = filtered.groupby("type")["is_fraud"].agg(["sum","count"]).reset_index()
    fraud_cat.columns = ["category", "fraud_count", "total"]
    fraud_cat["fraud_rate"] = (fraud_cat["fraud_count"] / fraud_cat["total"] * 100).round(2)
    fraud_cat = fraud_cat.sort_values("fraud_rate", ascending=True)

    fig_fraud_cat = px.bar(
        fraud_cat, x="fraud_rate", y="category",
        orientation="h",
        title="Fraud Rate by Category (%)",
        color_discrete_sequence=["#fbbf24"]
    )
    fig_fraud_cat.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
        font=dict(color="#64748b", family="Inter"),
        margin=dict(t=40, b=20, l=10, r=10), height=280, showlegend=False
    )
    fig_fraud_cat.update_xaxes(gridcolor="#e2e8f0")
    fig_fraud_cat.update_yaxes(gridcolor="#e2e8f0")
    st.plotly_chart(fig_fraud_cat, use_container_width=True)

with col3:
    fraud_amt = filtered[filtered["is_fraud"] == 1]["amount"]
    legit_amt = filtered[filtered["is_fraud"] == 0]["amount"].sample(
        min(len(fraud_amt) * 3, len(filtered[filtered["is_fraud"] == 0])),
        random_state=42
    )
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Histogram(
        x=legit_amt, name="Legitimate",
        marker_color="#3fb950", opacity=0.7, nbinsx=30
    ))
    fig_dist.add_trace(go.Histogram(
        x=fraud_amt, name="Fraud",
        marker_color="#f87171", opacity=0.7, nbinsx=30
    ))
    fig_dist.update_layout(
        title="Fraud vs Legit Amount",
        barmode="overlay",
        paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
        font=dict(color="#64748b", family="Inter"),
        margin=dict(t=40, b=20, l=10, r=10), height=280,
        legend=dict(bgcolor="#ffffff")
    )
    fig_dist.update_xaxes(gridcolor="#e2e8f0", title="Amount ($)")
    fig_dist.update_yaxes(gridcolor="#e2e8f0")
    st.plotly_chart(fig_dist, use_container_width=True)

# ============================================================
# ROW 4 — CUSTOMER INSIGHTS
# ============================================================

st.markdown('<div class="section-title">👤 Customer Insights</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    gender_spend = filtered.groupby("gender")["amount"].sum().reset_index()
    gender_spend.columns = ["gender", "total_spend"]
    fig_gender = px.pie(
        gender_spend, values="total_spend", names="gender",
        title="Spending by Gender",
        color_discrete_sequence=["#58a6ff", "#f778a1", "#a78bfa"]
    )
    fig_gender.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
        font=dict(color="#64748b", family="Inter"),
        margin=dict(t=40, b=10, l=10, r=10), height=280
    )
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    fig_age = px.histogram(
        filtered, x="age", nbins=20,
        title="Customer Age Distribution",
        color_discrete_sequence=["#a78bfa"]
    )
    fig_age.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
        font=dict(color="#64748b", family="Inter"),
        margin=dict(t=40, b=20, l=10, r=10), height=280, showlegend=False
    )
    fig_age.update_xaxes(gridcolor="#e2e8f0", title="Age")
    fig_age.update_yaxes(gridcolor="#e2e8f0", title="Count")
    st.plotly_chart(fig_age, use_container_width=True)

with col3:
    city_vol = filtered.groupby("city")["amount"].sum().sort_values(ascending=False).head(8).reset_index()
    city_vol.columns = ["city", "volume"]
    fig_city = px.bar(
        city_vol, x="volume", y="city",
        orientation="h",
        title="Top Cities by Volume",
        color_discrete_sequence=["#58a6ff"]
    )
    fig_city.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
        font=dict(color="#64748b", family="Inter"),
        margin=dict(t=40, b=20, l=10, r=10), height=280, showlegend=False
    )
    fig_city.update_xaxes(gridcolor="#e2e8f0", title="Total Volume ($)")
    fig_city.update_yaxes(gridcolor="#e2e8f0")
    st.plotly_chart(fig_city, use_container_width=True)

# ============================================================
# ROW 5 — BEHAVIORAL HEATMAP + PAYMENT METHODS
# ============================================================

st.markdown('<div class="section-title">🕐 Behavioral Patterns</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    hour_day = filtered.groupby(["day_name", "hour"]).size().reset_index(name="count")
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    hour_day["day_name"] = pd.Categorical(hour_day["day_name"], categories=day_order, ordered=True)
    pivot = hour_day.sort_values("day_name").pivot(index="day_name", columns="hour", values="count").fillna(0)
    fig_heat = px.imshow(
        pivot, title="Transaction Heatmap (Day × Hour)",
        color_continuous_scale="Greens",
        labels=dict(x="Hour of Day", y="Day", color="Transactions"),
        aspect="auto"
    )
    fig_heat.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
        font=dict(color="#64748b", family="Inter"),
        margin=dict(t=40, b=20, l=10, r=10), height=300
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with col2:
    pay_counts = filtered["payment_method"].value_counts().reset_index()
    pay_counts.columns = ["method", "count"]
    fig_pay = px.bar(
        pay_counts, x="count", y="method",
        orientation="h",
        title="Transactions by Payment Method",
        color_discrete_sequence=["#3fb950"]
    )
    fig_pay.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
        font=dict(color="#64748b", family="Inter"),
        margin=dict(t=40, b=20, l=10, r=10), height=300, showlegend=False
    )
    fig_pay.update_xaxes(gridcolor="#e2e8f0", title="Count")
    fig_pay.update_yaxes(gridcolor="#e2e8f0")
    st.plotly_chart(fig_pay, use_container_width=True)

# ============================================================
# ROW 6 — FRAUD ALERTS TABLE
# ============================================================

st.markdown('<div class="section-title">🚨 Recent Fraud Alerts</div>', unsafe_allow_html=True)

fraud_alerts = filtered[filtered["is_fraud"] == 1].sort_values("date", ascending=False).head(10)

if len(fraud_alerts) > 0:
    display_df = fraud_alerts[["date","amount","type","city","status","payment_method"]].copy()
    display_df["amount"] = display_df["amount"].apply(lambda x: f"${x:,.2f}")
    display_df["date"]   = display_df["date"].dt.strftime("%Y-%m-%d %H:%M")
    display_df.columns   = ["Date","Amount","Category","City","Status","Payment Method"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("No fraud detected in the selected filters.")

# ============================================================
# ROW 7 — AUTO INSIGHTS
# ============================================================

st.markdown('<div class="section-title">💡 Auto-Generated Insights</div>', unsafe_allow_html=True)

peak_hour     = filtered.groupby("hour").size().idxmax()
peak_day      = filtered.groupby("day_name").size().idxmax()
top_category  = filtered["type"].value_counts().idxmax()
top_city      = filtered["city"].value_counts().idxmax()
top_payment   = filtered["payment_method"].value_counts().idxmax()
high_risk_cat = fraud_cat.sort_values("fraud_rate", ascending=False).iloc[0]["category"]
high_val      = filtered[filtered["amount"] > filtered["amount"].quantile(0.95)]
high_val_fraud = high_val["is_fraud"].sum()

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:1.2rem;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
        <div style="font-family:'Space Mono',monospace;font-size:0.75rem;color:#16a34a;margin-bottom:1rem">PATTERN INSIGHTS</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.9rem;color:#1e293b;line-height:2.2">
            🕐 Peak transaction hour : <b>{peak_hour}:00</b><br>
            📅 Busiest day           : <b>{peak_day}</b><br>
            🛍️ Top spending category : <b>{top_category}</b><br>
            🏙️ Top city by volume    : <b>{top_city}</b><br>
            💳 Most used payment     : <b>{top_payment}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:1.2rem;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
        <div style="font-family:'Space Mono',monospace;font-size:0.75rem;color:#16a34a;margin-bottom:1rem">RISK SUMMARY</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.9rem;color:#1e293b;line-height:2.2">
            📊 Transactions analyzed  : <b>{total_txns:,}</b><br>
            🚨 Fraud detected         : <b style="color:#dc2626">{fraud_count:,} ({fraud_rate:.2f}%)</b><br>
            ⚠️ Highest fraud category : <b style="color:#d97706">{high_risk_cat}</b><br>
            💰 High-value (top 5%)    : <b>{len(high_val):,}</b><br>
            🔴 Fraud in high-value    : <b style="color:#dc2626">{high_val_fraud:,}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;font-family:'Inter',sans-serif;font-size:0.75rem;color:#cbd5e1;padding:1rem">
    Financial Transactions Dashboard · Built with Python & Streamlit · 
</div>
""", unsafe_allow_html=True)
