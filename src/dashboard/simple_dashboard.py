"""
Simple dashboard - polls API every 5 seconds
No WebSocket connection issues
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

st.set_page_config(page_title="Anomaly Detector", layout="wide")

st.title("🔍 Cloud Log Anomaly Detection System")
st.markdown("*Real-time monitoring | AI-powered detection*")

API_URL = "http://localhost:8000"

# Auto-refresh button
auto_refresh = st.sidebar.checkbox("Auto-refresh (every 5 seconds)", value=True)

if st.sidebar.button("🔄 Refresh Now"):
    st.rerun()

# Fetch data from API
def fetch_data():
    try:
        # Get window logs
        response = requests.get(f"{API_URL}/window?limit=200", timeout=5)
        if response.status_code == 200:
            logs = response.json().get('logs', [])
        else:
            logs = []
        
        # Get stats
        stats_response = requests.get(f"{API_URL}/stats", timeout=5)
        if stats_response.status_code == 200:
            stats = stats_response.json()
        else:
            stats = {}
            
        return logs, stats
    except Exception as e:
        st.error(f"API Error: {e}")
        return [], {}

# Main content
logs, stats = fetch_data()

if logs:
    df = pd.DataFrame(logs)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Identify anomalies (status code >= 400 OR latency > 2000ms)
    df['is_anomaly'] = ((df['status_code'] >= 400) | (df['latency_ms'] > 2000)).astype(int)
    df['anomaly_score'] = df.apply(
        lambda x: 0.9 if x['status_code'] >= 500 else 
                  0.7 if x['status_code'] >= 400 else 
                  0.6 if x['latency_ms'] > 2000 else 0.1, axis=1
    )
    
    anomalies_df = df[df['is_anomaly'] == 1]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Logs", len(df))
    col2.metric("Anomalies Detected", len(anomalies_df))
    col3.metric("Anomaly Rate", f"{len(anomalies_df)/len(df)*100:.1f}%")
    col4.metric("Window Size", stats.get('total', len(df)))
    
    # Live Alerts
    st.subheader("🚨 Anomaly Alerts")
    
    if len(anomalies_df) > 0:
        for _, row in anomalies_df.head(15).iterrows():
            if row['status_code'] >= 500:
                severity = "🔴 CRITICAL"
            elif row['status_code'] >= 400:
                severity = "🟡 WARNING"
            else:
                severity = "🟠 PERFORMANCE"
            
            st.warning(f"{severity} | {row['timestamp'][:19]} | "
                      f"{row['service']} | Status: {row['status_code']} | "
                      f"Latency: {row['latency_ms']}ms | {row['message'][:80]}")
    else:
        st.info("No anomalies detected")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Anomalies by Service")
        if len(anomalies_df) > 0:
            service_counts = anomalies_df['service'].value_counts().reset_index()
            service_counts.columns = ['service', 'count']
            fig = px.bar(service_counts, x='service', y='count')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Latency Distribution")
        fig = px.histogram(df, x='latency_ms', nbins=30, title="Response Times")
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📋 Recent Logs")
    display_df = df[['timestamp', 'service', 'status_code', 'latency_ms', 'is_anomaly', 'message']].head(30)
    st.dataframe(display_df, use_container_width=True)
    
else:
    st.warning("No logs received. Make sure API server is running:")
    st.code("uvicorn src.api.server:app --reload --port 8000")

# Auto-refresh logic
if auto_refresh:
    time.sleep(5)
    st.rerun()