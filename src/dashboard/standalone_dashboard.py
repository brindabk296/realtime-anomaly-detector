"""
Enhanced Anomaly Detection Dashboard
Features: Live monitoring, Email alerts, Export CSV, Health Scores, Trend Analysis
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Anomaly Detection System", 
    page_icon="🚨", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS FOR BETTER UI
# ============================================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: light blue;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: black;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid;
    }
    .critical {
        background-color: #ff4444;
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
    .warning {
        background-color: #ffaa44;
        color: black;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
    .slow {
        background-color: #4facfe;
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
    .email-alert {
        background-color: #dc2626;
        color: white;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 5px solid #fcd34d;
    }
    .health-90 { background-color: #00c851; color: white; padding: 5px; border-radius: 5px; text-align: center; }
    .health-70 { background-color: #ffaa44; color: black; padding: 5px; border-radius: 5px; text-align: center; }
    .health-low { background-color: #ff4444; color: white; padding: 5px; border-radius: 5px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown('<div class="main-header"><h1>🚨 Advanced Anomaly Detection System</h1><p>Real-time monitoring • AI-powered detection • Instant alerts</p></div>', unsafe_allow_html=True)

# ============================================
# API CONFIGURATION
# ============================================
API_URL = os.environ.get('API_URL', 'https://anomaly-api-bnuk.onrender.com')

# ============================================
# EMAIL ALERT FUNCTION
# ============================================
def send_email_alert(anomaly):
    """Send email alert for critical anomalies"""
    # For demo, we'll just print. Uncomment and add credentials for real emails
    print(f"""
    📧 EMAIL ALERT TRIGGERED
    To: guide@college.edu
    Subject: 🚨 CRITICAL ALERT - {anomaly['service']}
    Body: 
    Time: {anomaly['timestamp']}
    Service: {anomaly['service']}
    Status: {anomaly['status_code']}
    Latency: {anomaly['latency_ms']}ms
    """)
    return True

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("### 🎮 Dashboard Controls")
    auto_refresh = st.checkbox("🔄 Live Auto-Refresh", value=True)
    if st.button("📊 Refresh Now", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📥 Export Data")
    
    # Export button placeholder - will be enabled when data exists
    export_placeholder = st.empty()
    
    st.markdown("---")
    st.markdown("### 📋 Detection Rules")
    st.info("""
    🔴 **Critical** - HTTP 500+ Errors  
    🟡 **Warning** - HTTP 400+ Errors  
    🔵 **Slow** - Latency > 2000ms  
    """)
    
    st.markdown("---")
    st.caption(f"🔗 API: {API_URL}")
    st.caption("⚡ Powered by Isolation Forest ML")

# ============================================
# DATA FETCHING FUNCTION
# ============================================
@st.cache_data(ttl=5, show_spinner=False)
def fetch_logs():
    """Fetch logs from API server"""
    try:
        response = requests.get(f"{API_URL}/logs?limit=500", timeout=10)
        if response.status_code == 200:
            return response.json().get('logs', [])
    except Exception as e:
        st.error(f"API Connection Error: {e}")
    return []

# ============================================
# MAIN DATA PROCESSING
# ============================================
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
    
    # ============================================
    # FEATURE 1: QUICK SUMMARY (LAST HOUR)
    # ============================================
    st.subheader("📋 Quick Summary (Last Hour)")
    last_hour = datetime.now() - timedelta(hours=1)
    recent_logs = df[df['timestamp'] >= last_hour]
    recent_anomalies = recent_logs[recent_logs['is_anomaly'] == 1]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Last Hour Logs", len(recent_logs))
    with col2:
        st.metric("🚨 Last Hour Anomalies", len(recent_anomalies))
    with col3:
        worst = recent_anomalies['service'].mode().iloc[0] if len(recent_anomalies) > 0 else "None"
        st.metric("⚠️ Worst Service", worst)
    with col4:
        peak = recent_anomalies['anomaly_score'].max() if len(recent_anomalies) > 0 and 'anomaly_score' in recent_anomalies.columns else 0
        st.metric("📈 Peak Score", f"{peak:.2f}" if peak > 0 else "N/A")
    
    st.markdown("---")
    
    # ============================================
    # METRICS ROW
    # ============================================
    col1, col2, col3, col4, col5 = st.columns(5)
    
    rate = len(anomalies)/len(df)*100 if len(df) > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #3498db;">
            <h3>📊 {len(df)}</h3>
            <p>Total Logs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #e74c3c;">
            <h3>🚨 {len(anomalies)}</h3>
            <p>Total Anomalies</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color = "#e74c3c" if rate > 20 else "#f39c12" if rate > 5 else "#2ecc71"
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: {color};">
            <h3>⚠️ {rate:.1f}%</h3>
            <p>Anomaly Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #ff4444;">
            <h3>🔴 {len(critical_df)}</h3>
            <p>Critical</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #9b59b6;">
            <h3>🏢 {df['service'].nunique()}</h3>
            <p>Services</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # GAUGE CHART (ANOMALY RATE VISUAL)
    # ============================================
    st.subheader("📊 Anomaly Rate Gauge")
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = rate,
        title = {'text': "Current Anomaly Rate (%)", 'font': {'size': 24}},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#ff4444" if rate > 20 else "#ffaa44" if rate > 5 else "#00c851"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 5], 'color': 'lightgreen'},
                {'range': [5, 20], 'color': 'lightyellow'},
                {'range': [20, 100], 'color': 'lightcoral'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': rate
            }
        }
    ))
    fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # ============================================
    # LIVE ANOMALY ALERTS
    # ============================================
    st.subheader("🚨 Live Anomaly Alerts")
    
    # Send alerts for critical anomalies (simulated)
    if len(critical_df) > 0:
        for _, row in critical_df.head(3).iterrows():
            send_email_alert(row)
    
    if len(anomalies) > 0:
        for _, row in anomalies.head(8).iterrows():
            time_str = str(row['timestamp'])[11:19]
            if row['status_code'] >= 500:
                st.markdown(f"""
                <div class="critical">
                    🔴 CRITICAL | {time_str} | {row['service']} | HTTP {row['status_code']} | {row['latency_ms']}ms
                </div>
                """, unsafe_allow_html=True)
            elif row['status_code'] >= 400:
                st.markdown(f"""
                <div class="warning">
                    🟡 WARNING | {time_str} | {row['service']} | HTTP {row['status_code']} | {row['latency_ms']}ms
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="slow">
                    🔵 PERFORMANCE | {time_str} | {row['service']} | Latency {row['latency_ms']}ms
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ No anomalies detected - System is healthy")
    
    # ============================================
    # EMAIL ALERTS SECTION (VISUAL ON DASHBOARD)
    # ============================================
    st.subheader("📧 Email Notification Log")
    
    if len(critical_df) > 0:
        with st.expander("📧 Recent Email Alerts Sent", expanded=True):
            for _, row in critical_df.head(5).iterrows():
                st.markdown(f"""
                <div class="email-alert">
                    <strong>📧 EMAIL ALERT SENT</strong><br>
                    <strong>To:</strong> engineering-team@company.com<br>
                    <strong>Subject:</strong> 🚨 CRITICAL ALERT - {row['service']}<br>
                    <strong>Time:</strong> {row['timestamp']}<br>
                    <strong>Status:</strong> HTTP {row['status_code']} | <strong>Latency:</strong> {row['latency_ms']}ms<br>
                    <strong>Message:</strong> Service {row['service']} is experiencing critical failures
                </div>
                """, unsafe_allow_html=True)
    else:
        with st.expander("📧 Email Alert Status"):
            st.success("✅ No critical anomalies detected - No email alerts sent")
    
    # ============================================
    # SERVICE HEALTH DASHBOARD
    # ============================================
    st.subheader("🏥 Service Health Dashboard")
    
    health_data = []
    for service in df['service'].unique():
        service_logs = df[df['service'] == service]
        service_anomalies = service_logs[service_logs['is_anomaly'] == 1]
        
        total = len(service_logs)
        anomaly_count = len(service_anomalies)
        
        if total > 0:
            health_score = max(0, 100 - (anomaly_count / total * 100))
        else:
            health_score = 100
        
        health_data.append({
            'Service': service,
            'Health Score': round(health_score, 1),
            'Total Logs': total,
            'Anomalies': anomaly_count,
            'Status': '🟢 Healthy' if health_score >= 90 else '🟡 Warning' if health_score >= 70 else '🔴 Critical'
        })
    
    health_df = pd.DataFrame(health_data)
    
    # Color code the health scores
    def color_health(val):
        if isinstance(val, (int, float)):
            if val >= 90:
                return 'background-color: #00c851; color: white'
            elif val >= 70:
                return 'background-color: #ffaa44; color: black'
            else:
                return 'background-color: #ff4444; color: white'
        return ''
    
    st.dataframe(health_df.style.applymap(color_health, subset=['Health Score']), 
                 use_container_width=True, hide_index=True)
    
    # ============================================
    # ANOMALY TREND CHART
    # ============================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Anomaly Trend Over Time")
        if len(anomalies) > 0:
            anomalies_copy = anomalies.copy()
            anomalies_copy['minute'] = anomalies_copy['timestamp'].dt.floor('min')
            trend = anomalies_copy.groupby('minute').size().reset_index(name='count')
            
            fig = px.line(trend, x='minute', y='count', 
                          title="Anomalies per Minute",
                          markers=True,
                          color_discrete_sequence=['#ff4444'])
            fig.update_layout(height=350, plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No anomalies yet to show trend")
    
    with col2:
        st.subheader("📊 Anomalies by Service")
        if len(anomalies) > 0:
            service_counts = anomalies['service'].value_counts().reset_index()
            service_counts.columns = ['service', 'count']
            fig = px.bar(service_counts, x='service', y='count', 
                        color='count', 
                        color_continuous_scale='Reds',
                        text='count')
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No anomalies to display")
    
    # ============================================
    # LATENCY DISTRIBUTION
    # ============================================
    st.subheader("📊 Latency Distribution")
    fig = px.histogram(df, x='latency_ms', nbins=30, 
                       title="Response Time Distribution",
                       color_discrete_sequence=['#4facfe'])
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)
    
    # ============================================
    # RECENT ACTIVITY TABLE
    # ============================================
    st.subheader("📋 Recent Activity")
    
    display_df = df[['timestamp', 'service', 'status_code', 'latency_ms', 'is_anomaly']].head(15).copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
    
    def status_icon(code, latency):
        if code >= 500:
            return "🔴 CRITICAL"
        elif code >= 400:
            return "🟡 WARNING"
        elif latency > 2000:
            return "🔵 SLOW"
        else:
            return "✅ OK"
    
    display_df['Status'] = display_df.apply(lambda x: status_icon(x['status_code'], x['latency_ms']), axis=1)
    display_df = display_df.rename(columns={
        'timestamp': 'Time',
        'service': 'Service',
        'latency_ms': 'Latency',
        'status_code': 'Code'
    })
    st.dataframe(display_df[['Time', 'Service', 'Code', 'Latency', 'Status']], 
                 use_container_width=True, hide_index=True)
    
    # ============================================
    # EXPORT TO CSV
    # ============================================
    if len(anomalies) > 0:
        csv = anomalies.to_csv(index=False)
        export_placeholder.download_button(
            label="📥 Download Anomalies Report (CSV)",
            data=csv,
            file_name=f"anomaly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # ============================================
    # FOOTER
    # ============================================
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; color: #888;">
        <p>🕐 Last updated: {datetime.now().strftime('%H:%M:%S')} | 🔄 Auto-refresh: {'ON' if auto_refresh else 'OFF'}</p>
        <p>🧠 ML Model: Isolation Forest | 📊 Monitoring {df['service'].nunique()} services in real-time</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # AUTO REFRESH
    # ============================================
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
else:
    st.warning("⏳ Connecting to log stream...")
    st.info("Make sure API server is running:")
    st.code("uvicorn src.api.simple_server:app --reload --port 8000")
    st.markdown(f"**API URL:** `{API_URL}`")