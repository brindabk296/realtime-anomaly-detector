import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Anomaly Detector", 
    page_icon="🚨", 
    layout="wide"
)

# Custom CSS for white theme
st.markdown("""
<style>
    /* Main background - Light gray */
    .stApp {
        background: #f5f7fa;
    }
    
    /* Header styling - Dark header for contrast */
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: #94a3b8;
        margin-top: 0.5rem;
    }
    
    /* Metric cards - White background with shadow */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
        border-top: 4px solid;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    .metric-card h3 {
        font-size: 2rem;
        margin: 0;
        color: #1e293b;
    }
    .metric-card p {
        margin: 0.5rem 0 0 0;
        color: #64748b;
        font-size: 0.9rem;
    }
    
    /* Alert boxes - Keep colored for visibility */
    .critical {
        background: linear-gradient(135deg, #dc2626, #b91c1c);
        color: white;
        padding: 12px 15px;
        border-radius: 10px;
        margin: 8px 0;
        font-weight: bold;
        box-shadow: 0 3px 10px rgba(220,38,38,0.2);
    }
    .warning {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 12px 15px;
        border-radius: 10px;
        margin: 8px 0;
        font-weight: bold;
        box-shadow: 0 3px 10px rgba(245,158,11,0.2);
    }
    .slow {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 12px 15px;
        border-radius: 10px;
        margin: 8px 0;
        font-weight: bold;
        box-shadow: 0 3px 10px rgba(59,130,246,0.2);
    }
    
    /* Sidebar styling - WHITE BACKGROUND */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: white !important;
        border-right: 1px solid #e2e8f0;
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }
    
    /* Sidebar text color for dark mode elements */
    .css-1d391kg .stMarkdown, [data-testid="stSidebar"] .stMarkdown {
        color: #1e293b;
    }
    
    /* Sidebar headers */
    [data-testid="stSidebar"] h3 {
        color: #1e293b;
    }
    
    /* Sidebar captions */
    [data-testid="stSidebar"] .stCaption {
        color: #64748b;
    }
    
    /* Sidebar info boxes */
    [data-testid="stSidebar"] .stAlert {
        background-color: #f1f5f9;
        color: #1e293b;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #cbd5e1, #94a3b8, #cbd5e1, transparent);
    }
    
    /* Table styling */
    .stDataFrame {
        background: white;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #e2e8f0;
    }
    
    /* Metric labels */
    .stMetric {
        background: white;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Buttons */
    .stButton button {
        background: #1e293b;
        color: white;
        border: none;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background: #334155;
        transform: translateY(-2px);
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚨 Anomaly Eye</h1>
    <p>Real-time AI-powered log monitoring | Instant threat detection</p>
</div>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"

# Sidebar
with st.sidebar:
    st.markdown("### 🎮 Dashboard Controls")
    auto_refresh = st.checkbox("🔄 Live Auto-Refresh", value=True)
    st.markdown("---")
    if st.button("📊 Refresh Data Now", use_container_width=True):
        st.rerun()
    st.markdown("---")
    st.markdown("### 📋 Detection Rules")
    st.info("""
    🔴 **Critical** - HTTP 500+ Errors  
    🟠 **Warning** - HTTP 400+ Errors  
    🔵 **Slow** - Latency > 2000ms  
    """)
    st.markdown("---")
    st.caption("⚡ Powered by Isolation Forest ML")

# Fetch data
@st.cache_data(ttl=5, show_spinner=False)
def fetch_logs():
    try:
        response = requests.get(f"{API_URL}/logs?limit=200", timeout=3)
        if response.status_code == 200:
            return response.json().get('logs', [])
    except:
        pass
    return []

logs = fetch_logs()

if logs:
    df = pd.DataFrame(logs)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Detect anomalies
    df['is_anomaly'] = ((df['status_code'] >= 400) | (df['latency_ms'] > 2000)).astype(int)
    anomalies = df[df['is_anomaly'] == 1]
    critical_df = df[df['status_code'] >= 500]
    warning_df = df[(df['status_code'] >= 400) & (df['status_code'] < 500)]
    slow_df = df[(df['status_code'] < 400) & (df['latency_ms'] > 2000)]
    
    # Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #3b82f6;">
            <h3>📊 {len(df)}</h3>
            <p>Total Logs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #ef4444;">
            <h3>🚨 {len(anomalies)}</h3>
            <p>Total Anomalies</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        rate = len(anomalies)/len(df)*100 if len(df) > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #f59e0b;">
            <h3>⚠️ {rate:.1f}%</h3>
            <p>Anomaly Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #dc2626;">
            <h3>🔴 {len(critical_df)}</h3>
            <p>Critical</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #8b5cf6;">
            <h3>🏢 {df['service'].nunique()}</h3>
            <p>Services</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Anomaly Alerts Section
    st.markdown("---")
    st.markdown("## 🚨 Live Threat Alerts")
    st.markdown("*Real-time anomaly detection from your log stream*")
    
    if len(anomalies) > 0:
        for _, row in anomalies.head(8).iterrows():
            time_str = str(row['timestamp'])[11:19]
            if row['status_code'] >= 500:
                st.markdown(f"""
                <div class="critical">
                    🔥 CRITICAL THREAT | {time_str} | {row['service']} | HTTP {row['status_code']} | {row['latency_ms']}ms
                </div>
                """, unsafe_allow_html=True)
            elif row['status_code'] >= 400:
                st.markdown(f"""
                <div class="warning">
                    ⚠️ WARNING | {time_str} | {row['service']} | HTTP {row['status_code']} | {row['latency_ms']}ms
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="slow">
                    🐌 PERFORMANCE | {time_str} | {row['service']} | Latency {row['latency_ms']}ms
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ All systems operational - No anomalies detected")
    
    # Charts
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 📊 Anomalies by Service")
        if len(anomalies) > 0:
            service_counts = anomalies['service'].value_counts().reset_index()
            service_counts.columns = ['service', 'count']
            fig = px.bar(service_counts, x='service', y='count', 
                        color='count', 
                        color_continuous_scale='Reds',
                        text='count')
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_color='#1e293b',
                title_font_color='#1e293b',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📭 No anomalies to display")
    
    with col2:
        st.markdown("## 📈 Latency Trend")
        df_time = df.set_index('timestamp').resample('10S').agg({
            'latency_ms': 'mean',
            'status_code': lambda x: sum(1 for v in x if v >= 400)
        }).fillna(0).reset_index()
        
        fig = px.line(df_time, x='timestamp', y='latency_ms',
                      title="Average Response Time Over Time",
                      color_discrete_sequence=['#3b82f6'])
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color='#1e293b',
            title_font_color='#1e293b',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activity Table
    st.markdown("---")
    st.markdown("## 📋 Recent Activity")
    
    display_df = df[['timestamp', 'service', 'status_code', 'latency_ms', 'is_anomaly']].head(12).copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
    
    def status_icon(code):
        if code >= 500:
            return "🔥 CRITICAL"
        elif code >= 400:
            return "⚠️ ERROR"
        else:
            return "✅ OK"
    
    display_df['Status'] = display_df['status_code'].apply(status_icon)
    display_df = display_df.rename(columns={
        'timestamp': 'Time',
        'service': 'Service',
        'latency_ms': 'Latency',
        'status_code': 'Code'
    })
    st.dataframe(display_df[['Time', 'Service', 'Code', 'Latency', 'Status']], 
                use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; color: #64748b;">
        <p>🕐 Live Feed | Last scan: {datetime.now().strftime('%H:%M:%S')} | 🧠 ML Model: Isolation Forest</p>
        <p style="font-size: 0.8rem;">Monitoring {df['service'].nunique()} services in real-time</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()
        
else:
    st.warning("⏳ Connecting to log stream...")
    st.info("Start the API server with:")
    st.code("uvicorn src.api.simple_server:app --reload --port 8000", language="bash")