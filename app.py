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
if file:
    df = load_csv(file)

    if df is not None:

        # Detect columns dynamically
        date_col = next((c for c in df.columns if "date" in c), None)
        amount_col = next((c for c in df.columns if "amount" in c or "expense" in c), None)
        category_col = next((c for c in df.columns if "category" in c), None)

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
