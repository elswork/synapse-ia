import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailAdapter:
    def __init__(self, smtp_server: str, smtp_port: int, user: str, password: str):
        self.server = smtp_server
        self.port = smtp_port
        self.user = user
        self.password = password

    def send(self, to_email: str, subject: str, html_content: str, text_content: str) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.user
            msg["To"] = to_email

            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            msg.attach(part1)
            msg.attach(part2)

            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.user, to_email, msg.as_string())
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
