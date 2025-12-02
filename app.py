import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------
# PAGE SETTINGS
# -----------------------------------------------------
st.set_page_config(page_title="Finance Dashboard", page_icon="💼", layout="wide")

st.markdown("""
    <style>
        .main {background-color: #0E1117;}
        .block-container {padding-top: 1rem;}
        .metric-card {
            background: rgba(30, 30, 30, 0.7);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 15px;
            border: 1px solid #30363D;
        }
        h2 {color: #24E39D !important; text-align: center;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2>💼 Professional Finance Dashboard</h2>", unsafe_allow_html=True)

# -----------------------------------------------------
# FILE UPLOADER
# -----------------------------------------------------
file = st.file_uploader("📂 Upload Finance CSV", type=["csv"])

# -----------------------------------------------------
# FUNCTION TO LOAD DATA SAFELY
# -----------------------------------------------------
def load_csv(file):
    try:
        df = pd.read_csv(file)

        df.columns = [c.lower().replace(" ", "_") for c in df.columns]

        # Detect date column
        for col in df.columns:
            if "date" in col:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Detect amount columns
        for col in df.columns:
            if "amount" in col or "expense" in col or "income" in col:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna()
        return df

    except Exception as e:
        st.error("❌ Error reading file: " + str(e))
        return None

# -----------------------------------------------------
# MAIN DASHBOARD IF FILE EXISTS
# -----------------------------------------------------


    

     # -------------------------
# Robust column detection + UI for mapping CSV fields
# -------------------------

# show the column names so user can map them (helps debug)
st.sidebar.markdown("### 🔎 Available columns in file")
st.sidebar.write(list(df.columns))

# helper: try to auto-suggest a column by keywords (returns first match or None)
def autosuggest(cols, keywords):
    for k in keywords:
        for c in cols:
            if k in c:
                return c
    return None

# initial suggestions
suggested_date = autosuggest(df.columns, ["date", "txn_date", "transaction_date", "time"])
suggested_amount = autosuggest(df.columns, ["amount", "amt", "price", "value", "cost", "expense", "total"])
suggested_category = autosuggest(df.columns, ["category", "cat", "type", "group"])

# Let user explicitly choose which columns to use (preselect suggestions if found)
st.sidebar.markdown("### ⚙️ Map your columns (pick the correct one)")
date_col = st.sidebar.selectbox("Date column (choose)", options=[None] + list(df.columns), index=0 if not suggested_date else (list(df.columns).index(suggested_date) + 1))
amount_col = st.sidebar.selectbox("Amount column (choose)", options=[None] + list(df.columns), index=0 if not suggested_amount else (list(df.columns).index(suggested_amount) + 1))
category_col = st.sidebar.selectbox("Category column (optional)", options=[None] + list(df.columns), index=0 if not suggested_category else (list(df.columns).index(suggested_category) + 1))

# Convert selected columns safely
if date_col:
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    except Exception:
        st.warning("Could not convert chosen date column to datetimes; some filters/plots may not work.")

if amount_col:
    try:
        df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
    except Exception:
        st.warning("Could not convert chosen amount column to numeric; some calculations may be incorrect.")

# If the user hasn't chosen an amount column, show an error and stop further KPIs (avoids KeyError)
if not amount_col:
    st.error("⚠️ Please select the **Amount column** from the sidebar. The app cannot compute totals without it.")
    st.stop()

# drop rows where amount is NaN after coercion (prevents weird sums)
df = df.dropna(subset=[amount_col])

# ---------- KPI METRICS (safe) ----------
total_amount = df[amount_col].sum()
num_transactions = len(df)

st.markdown("### KPI Summary")
col1, col2 = st.columns(2)
col1.metric("💸 Total Amount", f"₹ {total_amount:,.2f}")
col2.metric("📁 Transactions", f"{num_transactions}")

# Continue with charts using the selected columns (use checks)
st.subheader("📊 Visual Insights")

if category_col:
    # pie by category (safe)
    try:
        fig = px.pie(df, names=category_col, values=amount_col, title="Expense by Category")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("Could not draw category pie chart: " + str(e))

if date_col:
    # time series (safe)
    try:
        timeseries_df = df.dropna(subset=[date_col]).sort_values(date_col)
        fig2 = px.line(timeseries_df, x=date_col, y=amount_col, title="Expenses Over Time (by chosen date column)", markers=True)
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.warning("Could not draw time series chart: " + str(e))

# show final data table and download
st.subheader("📄 Data (mapped)")
st.dataframe(df, use_container_width=True)
st.download_button("⬇️ Download mapped CSV", df.to_csv(index=False), "mapped_budget.csv", "text/csv")

        # --------------------------
        # SIDEBAR FILTERS
        # --------------------------
        st.sidebar.header("🔍 Filters")

        if date_col:
            start, end = st.sidebar.date_input(
                "Select Date Range",
                [df[date_col].min(), df[date_col].max()]
            )
            df = df[(df[date_col] >= pd.to_datetime(start)) &
                    (df[date_col] <= pd.to_datetime(end))]

        if category_col:
            selected_cat = st.sidebar.multiselect(
                "Select Categories",
                df[category_col].unique()
            )
            if selected_cat:
                df = df[df[category_col].isin(selected_cat)]

        # -----------------------------------------------------
        # KPI METRICS
        # -----------------------------------------------------
        total_amount = df[amount_col].sum()

        monthly_expense = df.groupby(df[date_col].dt.to_period("M"))[amount_col].sum()

        avg_expense = monthly_expense.mean()

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<div class='metric-card'><h3>💸 Total Spend</h3><h2>₹ {total_amount:,.2f}</h2></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='metric-card'><h3>📉 Average Monthly Spend</h3><h2>₹ {avg_expense:,.2f}</h2></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='metric-card'><h3>📁 Total Transactions</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)

        st.write("")

        # -----------------------------------------------------
        # CHARTS SECTION
        # -----------------------------------------------------
        st.subheader("📈 Analytics Overview")

        # Monthly Trend Chart
        if date_col:
            monthly = df.groupby(df[date_col].dt.to_period("M"))[amount_col].sum().reset_index()
            monthly[date_col] = monthly[date_col].astype(str)

            fig1 = px.line(
                monthly,
                x=date_col,
                y=amount_col,
                title="Monthly Spending Trend",
                markers=True
            )
            st.plotly_chart(fig1, use_container_width=True)

        # Category-wise pie chart
        if category_col:
            fig2 = px.pie(
                df,
                names=category_col,
                values=amount_col,
                title="Category-wise Distribution"
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Bar chart by category
        if category_col:
            fig3 = px.bar(
                df.groupby(category_col)[amount_col].sum().reset_index(),
                x=category_col,
                y=amount_col,
                title="Expenses by Category",
                text_auto=True
            )
            st.plotly_chart(fig3, use_container_width=True)

        # -----------------------------------------------------
        # DATA TABLE + DOWNLOAD
        # -----------------------------------------------------
        st.subheader("📄 Transaction Table")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇ Download Filtered CSV",
            df.to_csv(index=False),
            "finance_filtered.csv",
            "text/csv"
        )

else:
    st.info("📥 Upload a CSV file to begin.")
