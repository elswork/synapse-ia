import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

class EmailSender:
    def __init__(self):
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.admin_email = os.getenv("ADMIN_EMAIL")

    def send_mep_email(self, name, country, email, subject, body_html, body_text, category="MEP", to_email=None):
        if not self.smtp_user or not self.smtp_password:
            raise ValueError("SMTP credentials not configured in .env")

        recipient = to_email if to_email else self.admin_email

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🏛️ {category} Proposal: {name} ({country})"
        msg["From"] = f"Anticitera Digital Nation <{self.smtp_user}>"
        msg["To"] = recipient

        # Content for the user to copy/paste easily
        # We'll prepend the actual recipient info if it's going to admin
        intro = ""
        if recipient == self.admin_email:
            intro = f"Para enviar a: {email}\nSubject: {subject}\n\n"
        
        part1 = MIMEText(intro + body_text, "plain")
        part2 = MIMEText(body_html, "html")

        msg.attach(part1)
        msg.attach(part2)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, recipient, msg.as_string())
            return True
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

if __name__ == "__main__":
    # Test
    sender = EmailSender()
    success = sender.send_mep_email(
        "Test MEP", "Greece", "test@europarl.europa.eu", 
        "Test Subject", "<h1>Test</h1><p>This is a test.</p>", "Test Plain Text"
    )
    print(f"Email sent: {success}")
