import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_alert_email(anomaly):
    """Send email when critical anomaly detected"""
    
    # Your email credentials (use a test email)
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"  # Use Gmail App Password
    receiver_email = "guide_email@college.edu"
    
    subject = f"🚨 CRITICAL ALERT: Anomaly Detected in {anomaly['service']}"
    
    body = f"""
    Anomaly Detected!
    
    Time: {anomaly['timestamp']}
    Service: {anomaly['service']}
    Status Code: {anomaly['status_code']}
    Latency: {anomaly['latency_ms']}ms
    Message: {anomaly['message']}
    
    Please check the dashboard immediately.
    Dashboard: https://anomaly-dashboard-1s3k.onrender.com
    """
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Alert email sent for {anomaly['service']}")
    except Exception as e:
        print(f"Email failed: {e}")

# For testing without real email
def print_alert(anomaly):
    print(f"""
    📧 EMAIL ALERT (Simulated)
    To: guide@college.edu
    Subject: CRITICAL ALERT - {anomaly['service']}
    Body: {anomaly['status_code']} error at {anomaly['timestamp']}
    """)