import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Professional Finance Dashboard",
    layout="wide",
    page_icon="💼"
)

# ---------------------------------------------------------
# CUSTOM STYLE (Dark Premium UI)
# ---------------------------------------------------------
st.markdown("""
    <style>
    .main {background-color: #0E1117;}
    .block-container {padding-top: 1rem;}
    .metric-card {
        background: rgba(30, 30, 30, 0.7);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Professional Finance Dashboard")
st.markdown("Upload your CSV, map the columns, and explore insights.")

# ---------------------------------------------------------
# FILE UPLOADER
# ---------------------------------------------------------
file = st.file_uploader("Upload Budget CSV File", type=["csv"])

if file is None:
    st.info("📄 Please upload a CSV file to begin.")
    st.stop()

# ---------------------------------------------------------
# LOAD DATA SAFELY
# ---------------------------------------------------------
try:
    df = pd.read_csv(file)
except Exception as e:
    st.error(f"❌ Error loading CSV: {e}")
    st.stop()

if df.empty:
    st.error("Uploaded file is empty. Please upload a valid CSV.")
    st.stop()

# ---------------------------------------------------------
# SIDEBAR — COLUMN MAPPING
# ---------------------------------------------------------
st.sidebar.header("⚙️ Configure Columns")

st.sidebar.markdown("### 🔎 Available Columns")
st.sidebar.write(list(df.columns))

def autosuggest(cols, keywords):
    for k in keywords:
        for c in cols:
            if k in c.lower():
                return c
    return None

suggested_date = autosuggest(df.columns, ["date", "time"])
suggested_amount = autosuggest(df.columns, ["amount", "amt", "price", "value", "cost", "expense"])
suggested_category = autosuggest(df.columns, ["category", "cat", "type"])

# Selectboxes
date_col = st.sidebar.selectbox(
    "Select Date Column (optional)",
    options=[None] + list(df.columns),
    index=(list(df.columns).index(suggested_date) + 1) if suggested_date else 0
)

amount_col = st.sidebar.selectbox(
    "Select Amount Column (Required)",
    options=[None] + list(df.columns),
    index=(list(df.columns).index(suggested_amount) + 1) if suggested_amount else 0
)

category_col = st.sidebar.selectbox(
    "Select Category Column (optional)",
    options=[None] + list(df.columns),
    index=(list(df.columns).index(suggested_category) + 1) if suggested_category else 0
)

# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------
if amount_col is None:
    st.error("⚠️ You must select an Amount column.")
    st.stop()

# TYPES — SAFE CONVERSION
try:
    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
except:
    st.warning("Amount column could not be fully converted to numbers.")

df = df.dropna(subset=[amount_col])  # Remove rows without amount

if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
st.subheader("📊 Key Metrics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("💸 Total Amount", f"₹ {df[amount_col].sum():,.2f}")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("📁 Transactions", f"{len(df)}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# CHARTS
# ---------------------------------------------------------
st.subheader("📈 Visual Insights")

# CATEGORY PIE CHART
if category_col:
    try:
        fig = px.pie(
            df,
            names=category_col,
            values=amount_col,
            title="Expense Distribution by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("Could not generate category chart: " + str(e))

# TIME SERIES CHART
if date_col:
    try:
        df_ts = df.dropna(subset=[date_col]).sort_values(date_col)
        fig2 = px.line(
            df_ts,
            x=date_col,
            y=amount_col,
            markers=True,
            title="Expenses Over Time"
        )
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.warning("Could not generate time series chart: " + str(e))

# ---------------------------------------------------------
# DATA TABLE + DOWNLOAD
# ---------------------------------------------------------
st.subheader("📄 Final Data Preview")
st.dataframe(df, use_container_width=True)

st.download_button(
    "⬇️ Download Processed CSV",
    df.to_csv(index=False),
    "processed_budget.csv",
    "text/csv"
)

