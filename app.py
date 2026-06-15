import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics_engine import UPIAnalyticsEngine
import datetime

# --- SET PAGE CONFIG ---
st.set_page_config(
    page_title="UPI Decision Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    [data-testid="stSidebar"] { background-color: #161B22; }
    .stMetric {
        background-color: #1F2937;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
    }
    h1, h2, h3 { color: #FFD700 !important; }
    .insight-card {
        background-color: #1F2937;
        padding: 20px;
        border-radius: 10px;
        border-right: 5px solid #00D1FF;
        margin-bottom: 10px;
    }
    .impact-high { border-left: 5px solid #FF4B4B; }
    .impact-medium { border-left: 5px solid #FFA500; }
    .impact-critical { border-left: 5px solid #FF00FF; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_resource
def get_engine():
    return UPIAnalyticsEngine()

engine = get_engine()
df = engine.df
latest = df.iloc[-1]
prev = df.iloc[-2]
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# --- SIDEBAR ---
st.sidebar.title("UPI Analytics")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e1/UPI-Logo.png", width=100)
page = st.sidebar.selectbox("Navigate Dashboard", [
    "1. Executive Overview",
    "2. Adoption Story",
    "3. Seasonality & Behavior",
    "4. Market Disruption",
    "5. Forecasting & Planning",
    "6. AI Insight Generator"
])

# --- PAGE 1: EXECUTIVE OVERVIEW ---
if page == "1. Executive Overview":
    st.title("UPI Executive Intelligence Platform")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Monthly Vol (Lakhs)", f"{latest['UPI_Volume_Lakhs']:,.0f}", f"{latest['MoM_Growth_Vol']:.1f}% MoM")
    c2.metric("Monthly Value (Cr)", f"₹{latest['UPI_Value_Cr']:,.0f}", f"{latest['MoM_Growth_Val']:.1f}% MoM")
    c3.metric("Avg Ticket Size", f"₹{latest['Average_Ticket_Size']:,.0f}", f"{((latest['Average_Ticket_Size']/prev['Average_Ticket_Size'])-1)*100:.1f}%")
    c4.metric("Annual CAGR", f"{engine.get_cagr():.1f}%", "Historical")

    c5, c6, c7 = st.columns(3)
    c5.metric("Digital Penetration", f"{latest['Digital_Penetration_Score']:.1f}/100", "Adoption index")
    c6.metric("Transaction Density", f"{latest['Transaction_Density']:,.0f}", "Trans/Day (Avg)")
    c7.metric("Vol-Val Ratio", f"{latest['Vol_Val_Ratio']:.4f}", "Mix")

    col_l, col_r = st.columns([2, 1])
    with col_l:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df['Date'], y=df['UPI_Volume_Lakhs'], name='Volume (Lakhs)', line=dict(color='#00D1FF', width=3)))
        fig_trend.add_trace(go.Scatter(x=df['Date'], y=df['UPI_Value_Cr']/10, name='Value (Cr / 10)', line=dict(color='#FFD700', width=3)))
        fig_trend.update_layout(title="Growth Trajectory", template='plotly_dark')
        st.plotly_chart(fig_trend, width='stretch')

    with col_r:
        st.markdown("### Strategic Insights")
        for ins in engine.generate_executive_insights():
            st.markdown(f"""<div class="insight-card impact-{ins['impact'].lower()}"><strong>{ins['title']}</strong><br/><small>{ins['text']}</small></div>""", unsafe_allow_html=True)

# --- PAGE 2: ADOPTION STORY ---
elif page == "2. Adoption Story":
    st.title("The UPI Adoption Story")
    col1, col2 = st.columns(2)
    with col1:
        fig_log = px.line(df, x='Date', y='UPI_Volume_Lakhs', title="Log Scale Adoption Curve", log_y=True, color_discrete_sequence=['#FFD700'])
        fig_log.update_layout(template='plotly_dark')
        st.plotly_chart(fig_log, width='stretch')
    with col2:
        df['Year'] = df['Date'].dt.year
        yearly = df.groupby('Year')['UPI_Volume_Lakhs'].sum().reset_index()
        fig_yr = px.bar(yearly, x='Year', y='UPI_Volume_Lakhs', title="Annual Cumulative Volume", color='UPI_Volume_Lakhs', color_continuous_scale='Blues')
        fig_yr.update_layout(template='plotly_dark')
        st.plotly_chart(fig_yr, width='stretch')

    st.subheader("Velocity Milestones")
    milestones = [1000, 5000, 10000, 50000, 100000, 140000]
    m_data = []
    for m in milestones:
        reached = df[df['UPI_Volume_Lakhs'] >= m]
        if not reached.empty:
            m_data.append({'Milestone': f"{m/10000:.1f}B Trans.", 'Date': reached.iloc[0]['Date']})
    fig_m = px.scatter(pd.DataFrame(m_data), x='Date', y=[1]*len(m_data), text='Milestone', title="Growth Phase Timeline", size=[20]*len(m_data), color='Date')
    fig_m.update_traces(textposition='top center')
    fig_m.update_layout(template='plotly_dark', showlegend=False, yaxis_visible=False)
    st.plotly_chart(fig_m, width='stretch')

# --- PAGE 3: SEASONALITY ---
elif page == "3. Seasonality & Behavior":
    st.title("Seasonality & Behavior")
    res = engine.get_seasonality_stats()
    c1, c2 = st.columns(2)
    with c1:
        fig_trend = px.line(res.trend.reset_index(), x='Date', y='trend', title="Structural Trend")
        fig_trend.update_layout(template='plotly_dark')
        st.plotly_chart(fig_trend, width='stretch')
    with c2:
        fig_seas = px.line(res.seasonal.reset_index()[:12], x='Date', y='seasonal', title="Seasonal Cycle")
        fig_seas.update_layout(template='plotly_dark')
        st.plotly_chart(fig_seas, width='stretch')

# --- PAGE 4: MARKET DISRUPTION ---
elif page == "4. Market Disruption":
    st.title("Market Disruption")
    share_df = engine.get_market_share()
    fig_share = go.Figure()
    colors = ['#00D1FF', '#FFD700', '#00FFA3', '#FF4B4B']
    names = ['UPI', 'Cards', 'IMPS', 'ATM (Cash)']
    cols = ['UPI_Volume_Lakhs_Share', 'Cards_Volume_Lakhs_Share', 'IMPS_Volume_Lakhs_Share', 'ATM_Volume_Lakhs_Share']
    for i, col in enumerate(cols):
        fig_share.add_trace(go.Scatter(x=share_df['Date'], y=share_df[col], name=names[i], stackgroup='one', fillcolor=colors[i]))
    fig_share.update_layout(title="Evolution of Payment Mode Share (%)", template='plotly_dark')
    st.plotly_chart(fig_share, width='stretch')

# --- PAGE 5: FORECASTING ---
elif page == "5. Forecasting & Planning":
    st.title("Predictive Intelligence")
    forecast = engine.get_forecast()
    fig_fore = go.Figure()
    fig_fore.add_trace(go.Scatter(x=df['Date'], y=df['UPI_Volume_Lakhs'], name='Historical', line=dict(color='#00D1FF', width=3)))
    fig_fore.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast', line=dict(color='#FFD700', dash='dash')))
    fig_fore.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], mode='lines', line_color='rgba(255,215,0,0.2)', name='Upper'))
    fig_fore.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], mode='lines', fill='tonexty', line_color='rgba(255,215,0,0.2)', name='Lower'))
    fig_fore.update_layout(title="Volume Forecast (24 Months)", template='plotly_dark')
    st.plotly_chart(fig_fore, width='stretch')

# --- PAGE 6: AI INSIGHT GENERATOR ---
else:
    st.title("Decision Intelligence Engine")
    for i, ins in enumerate(engine.generate_executive_insights()):
        with st.expander(f"Strategy {i+1}: {ins['title']}", expanded=True):
            st.write(ins['text'])
            st.markdown("- **Strategic Action:** Optimize infrastructure for high-velocity flows.")

st.markdown("---")
st.caption("Produced by Senior FinTech Analyst | NPCI Analytics Mirror | 2024")
