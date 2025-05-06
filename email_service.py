import os
import smtplib
from email.mime.text import MIMEText

def send_email(data):
    sender_email = os.getenv("sender_email")
    sender_password = os.getenv("sender_password")
    recipient_email = os.getenv("recipient_email")
    
    subject = "Availability Update"
    body = "\n\n".join([f"{tracker_name}:\n{msg}" for tracker_name, msg in data.items() if msg])
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    try:
        with smtplib.SMTP_SSL('smtp.aol.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")