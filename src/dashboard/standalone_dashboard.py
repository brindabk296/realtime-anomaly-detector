import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import os

st.set_page_config(page_title="Anomaly Detector", layout="wide")

st.title("🔍 Cloud Log Anomaly Detection System")
st.markdown("*Real-time monitoring | AI-powered detection*")

API_URL = os.environ.get('API_URL', 'https://anomaly-api-bnuk.onrender.com')

# Sidebar
with st.sidebar:
    st.header("Controls")
    auto_refresh = st.checkbox("Auto Refresh (5 sec)", value=True)
    if st.button("Refresh Now"):
        st.rerun()
    st.markdown("---")
    st.caption(f"API: {API_URL}")

# Fetch logs
def fetch_logs():
    try:
        response = requests.get(f"{API_URL}/logs?limit=200", timeout=10)
        if response.status_code == 200:
            return response.json().get('logs', [])
    except Exception as e:
        st.error(f"API Error: {e}")
    return []

logs = fetch_logs()

if logs:
    df = pd.DataFrame(logs)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Detect anomalies
    df['is_anomaly'] = ((df['status_code'] >= 400) | (df['latency_ms'] > 2000)).astype(int)
    anomalies = df[df['is_anomaly'] == 1]
    critical_df = df[df['status_code'] >= 500]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Logs", len(df))
    col2.metric("Anomalies", len(anomalies))
    rate = len(anomalies)/len(df)*100 if len(df) > 0 else 0
    col3.metric("Anomaly Rate", f"{rate:.1f}%")
    col4.metric("Services", df['service'].nunique())
    
    # ============================================
    # EMAIL ALERTS SECTION (SIMULATED)
    # ============================================
    if len(critical_df) > 0:
        with st.expander("📧 Email Alerts Sent (Simulated)"):
            for _, row in critical_df.head(3).iterrows():
                st.code(f"""
To: guide@college.edu
Subject: CRITICAL ALERT - {row['service']}
Body: 
Time: {row['timestamp']}
Status: {row['status_code']}
Latency: {row['latency_ms']}ms
                """)
    
    # Alerts
    st.subheader("🚨 Anomaly Alerts")
    if len(anomalies) > 0:
        for _, row in anomalies.head(10).iterrows():
            time_str = str(row['timestamp'])[11:19]
            if row['status_code'] >= 500:
                st.error(f"🔴 CRITICAL | {time_str} | {row['service']} | Status: {row['status_code']} | {row['latency_ms']}ms")
            elif row['status_code'] >= 400:
                st.warning(f"🟡 WARNING | {time_str} | {row['service']} | Status: {row['status_code']} | {row['latency_ms']}ms")
            else:
                st.warning(f"🟠 SLOW | {time_str} | {row['service']} | Latency: {row['latency_ms']}ms")
    else:
        st.info("✅ No anomalies detected")
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Anomalies by Service")
        if len(anomalies) > 0:
            fig = px.bar(anomalies['service'].value_counts().reset_index(), 
                        x='service', y='count', title=" ")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Latency Distribution")
        fig = px.histogram(df, x='latency_ms', nbins=30, title=" ")
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("Recent Activity")
    st.dataframe(df[['timestamp', 'service', 'status_code', 'latency_ms', 'is_anomaly']].head(20))
    
    if auto_refresh:
        time.sleep(5)
        st.rerun()
else:
    st.warning("Waiting for logs...")
    st.info(f"API URL: {API_URL}")