import os
import smtplib
from email.mime.text import MIMEText

def send_email(data):
    sender_email = os.getenv("sender_email")
    sender_password = os.getenv("sender_password")
    recipient_email = os.getenv("recipient_email")
    
    subject = "Tracker Availability Update"
    body = "<br><br>".join([f"{tracker_name}:<br>{msg}" for tracker_name, msg in data.items() if msg])
    
    if not body:
        print("No new content to send.")
        return
    
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    try:
        with smtplib.SMTP_SSL('smtp.aol.com', 465) as server:
            print(f"Email details - sender: {sender_email}, password: {sender_password}, receiver: {recipient_email}")

            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")