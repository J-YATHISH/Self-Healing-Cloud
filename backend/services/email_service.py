import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load .env from backend root (parent of services/)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(parent_dir, ".env"))

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_USER")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD")

    async def send_alert_email(self, recipient_email, alert_name, incident_data):
        if not self.sender_email or not self.sender_password:
            print("⚠️ Email Service: GMAIL_USER or GMAIL_APP_PASSWORD not set. Skipping email.")
            return False

        message = MIMEMultipart("alternative")
        message["Subject"] = f"🚨 CLOUD ALERT: {alert_name}"
        message["From"] = f"Cloud RCA Agent <{self.sender_email}>"
        message["To"] = recipient_email

        # ... (parts of the email remain the same)
        text = f"""
        Alert Triggered: {alert_name}
        
        Incident Details:
        - Trace ID: {incident_data.get('trace_id')}
        - Category: {incident_data.get('category')}
        - Priority: {incident_data.get('priority')}
        - Summary: {incident_data.get('redacted_text')}
        
        Action Required: Please check the Mission Control dashboard.
        """
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background-color: #0d1117; padding: 20px; color: #fff; border-radius: 10px;">
              <h2 style="color: #00d1ff;">🚨 Alert Triggered: {alert_name}</h2>
              <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 5px; border-left: 4px solid #00d1ff;">
                <p><strong>Trace ID:</strong> <code>{incident_data.get('trace_id')}</code></p>
                <p><strong>Category:</strong> {incident_data.get('category')}</p>
                <p><strong>Priority:</strong> {incident_data.get('priority')}</p>
                <p><strong>Summary:</strong> {incident_data.get('redacted_text')}</p>
              </div>
              <p style="margin-top: 20px;">
                <a href="http://localhost:5173/incidents" style="background-color: #00d1ff; color: #000; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">VIEW IN MISSION CONTROL</a>
              </p>
            </div>
          </body>
        </html>
        """

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        try:
            import aiosmtplib
            async with aiosmtplib.SMTP(hostname=self.smtp_server, port=self.smtp_port, use_tls=False) as server:
                await server.starttls()
                await server.login(self.sender_email, self.sender_password)
                await server.send_message(message)
            print(f"✅ Alert email sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

email_service = EmailService()
