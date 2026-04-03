import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Romina NaviFreight Hub", 
    layout="wide", 
    page_icon="🚢"
)

# 2. HIGH-VISIBILITY CSS (Fixes the text/background mixing)
st.markdown("""
    <style>
    /* Main Background */
    .main { background-color: #f0f2f6; }

    /* KPI Metric Cards Styling */
    [data-testid="stMetric"] {
        background-color: #1e293b !important; /* Deep Navy Blue */
        border-left: 5px solid #3b82f6 !important; /* Blue Accent Line */
        padding: 15px 20px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }

    /* Force Metric Label Text to be visible (Silver/Gray) */
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important; 
        font-weight: 600 !important;
        font-size: 16px !important;
    }

    /* Force Metric Value Text to be bright (White) */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Success/Delta coloring (The arrows) */
    [data-testid="stMetricDelta"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        padding: 2px 5px !important;
        border-radius: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading Engine
@st.cache_data
def load_data():
    path = "../data/processed/Unified_Logistics_Final_2025.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        df['Booking_Date'] = pd.to_datetime(df['Booking_Date'])
        return df
    return pd.DataFrame()

df_raw = load_data()

# 4. Sidebar Navigation & Global Filters
st.sidebar.markdown("## 🛡️ Romina Logistics")
st.sidebar.markdown("---")

if not df_raw.empty:
    st.sidebar.header("🔍 Global Filters")

    selected_carrier = st.sidebar.multiselect(
        "Shipping Line:", 
        options=sorted(df_raw['Carrier'].unique()), 
        default=df_raw['Carrier'].unique()
    )

    selected_hub = st.sidebar.multiselect(
        "Inland Hub (Mojo/Kality):", 
        options=sorted(df_raw['Origin_Inland'].unique()), 
        default=df_raw['Origin_Inland'].unique()
    )

    risk_mode = st.sidebar.radio(
        "Filter by Risk Status:",
        ["All Shipments", "High Risk Only", "Cleared Only"]
    )

    # Filter Application
    df = df_raw[(df_raw['Carrier'].isin(selected_carrier)) & (df_raw['Origin_Inland'].isin(selected_hub))]

    if risk_mode == "High Risk Only":
        df = df[df['VGM_Alert'] != "CLEAR"]
    elif risk_mode == "Cleared Only":
        df = df[df['VGM_Alert'] == "CLEAR"]

    # 5. Dashboard Header
    st.title("🚢 NaviFreight: Operational Cockpit")
    st.caption("Advanced Weight Verification & Revenue Protection for Romina PLC")

    # 6. High-Visibility Executive KPIs
    critical_count = len(df[df['VGM_Alert'] != "CLEAR"])
    revenue_at_risk = critical_count * 5000 
    accuracy_rate = ((len(df) - critical_count) / len(df)) * 100 if len(df) > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Containers Analyzed", len(df))
    m2.metric("VGM Discrepancies", critical_count, delta=f"{critical_count} Roll Risks", delta_color="inverse")
    m3.metric("Revenue Protected", f"${revenue_at_risk:,}")
    m4.metric("System Accuracy", f"{accuracy_rate:.1f}%")

    st.markdown("---")

    # 7. Interconnected Charts
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Carrier Reliability Index")
        fig_carrier = px.bar(
            df.groupby(['Carrier', 'VGM_Alert']).size().reset_index(name='Count'),
            x="Carrier", y="Count", color="VGM_Alert",
            color_discrete_map={"CLEAR": "#27ae60", "CRITICAL: ROLL RISK": "#e74c3c"},
            barmode="group", height=400, template="plotly_white"
        )
        st.plotly_chart(fig_carrier, use_container_width=True)

    with col_right:
        st.subheader("Weight Deviation Analysis (KG)")
        fig_scatter = px.scatter(
            df, x="Declared_Weight_KG", y="Weight_Variance", 
            color="VGM_Alert", size=df['Weight_Variance'].abs(),
            hover_data=['Booking_Ref', 'Grade'],
            color_discrete_map={"CLEAR": "#27ae60", "CRITICAL: ROLL RISK": "#e74c3c"},
            template="plotly_white"
        )
        fig_scatter.add_hline(y=50, line_dash="dash", line_color="#e74c3c", annotation_text="Limit")
        fig_scatter.add_hline(y=-50, line_dash="dash", line_color="#e74c3c")
        st.plotly_chart(fig_scatter, use_container_width=True)

    # 8. Actionable Data Table
    st.subheader("📋 Urgent Action Checklist")
    st.dataframe(
        df[['Booking_Ref', 'Carrier', 'Grade', 'Origin_Inland', 'Weight_Variance', 'VGM_Alert']]
        .sort_values(by="Weight_Variance", ascending=False),
        use_container_width=True, hide_index=True
    )

    # 9. Sidebar Download
    st.sidebar.markdown("---")
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download Daily Logistics Report",
        data=csv,
        file_name='Romina_Logistics_Report_2025.csv',
        mime='text/csv',
    )
else:
    st.error("Data source missing.")

st.caption(" **Developed by Aklilu Abera** : **Import and Export officer** | **Supply Chain Data Analyst** ")
