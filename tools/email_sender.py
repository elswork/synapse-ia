import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Try to import boto3 for AWS SES
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

load_dotenv()

class EmailSender:
    def __init__(self):
        # Fallback SMTP Setup
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.admin_email = os.getenv("ADMIN_EMAIL", "elswork@gmail.com")
        self.sender_email = os.getenv("SENDER_EMAIL", self.smtp_user or "no-reply@anticitera.deft.work")
        self.sender_name = "Anticitera Digital Nation"
        
        # AWS SES Setup
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "eu-west-1")
        self.ses_configuration_set = os.getenv("SES_CONFIGURATION_SET", "")
        
        self.use_ses = bool(BOTO3_AVAILABLE and self.aws_access_key_id and self.aws_secret_access_key)
        
        if self.use_ses:
            print(f"📧 Inicializando EmailSender: Modo AMAZON SES API ({self.aws_region})")
            self.ses_client = boto3.client(
                'ses',
                region_name=self.aws_region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
        else:
            print("📧 Inicializando EmailSender: Modo SMTP Tradicional (Fallback)")

    def _send_via_ses(self, recipient, subject, body_html, body_text):
        """Envía el correo usando la API de Amazon SES"""
        try:
            message = {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'},
                    'Html': {'Data': body_html, 'Charset': 'UTF-8'}
                }
            }
            
            kwargs = {
                'Source': f"{self.sender_name} <{self.sender_email}>",
                'Destination': {'ToAddresses': [recipient]},
                'Message': message
            }
            
            # Usar Configuration Set si está definido (para traqueo de rebotes)
            if self.ses_configuration_set:
                kwargs['ConfigurationSetName'] = self.ses_configuration_set
                
            response = self.ses_client.send_email(**kwargs)
            return True
        except ClientError as e:
            print(f"❌ Error SES API: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            print(f"❌ Error fatal SES: {str(e)}")
            return False

    def _send_via_smtp(self, recipient, subject, body_html, body_text):
        """Envía el correo usando el SMTP original como fallback"""
        if not self.smtp_user or not self.smtp_password:
            print("❌ Error: No se configuró ni SES ni credenciales SMTP")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.sender_name} <{self.sender_email}>"
        msg["To"] = recipient

        part1 = MIMEText(body_text, "plain")
        part2 = MIMEText(body_html, "html")
        msg.attach(part1)
        msg.attach(part2)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender_email, recipient, msg.as_string())
            return True
        except Exception as e:
            print(f"❌ Error SMTP: {e}")
            return False

    def send_mep_email(self, name, country, email, subject, body_html, body_text, category="MEP", to_email=None):
        recipient = to_email if to_email else self.admin_email
        full_subject = f"🏛️ {category} Proposal: {name} ({country})"
        
        intro = ""
        if recipient == self.admin_email:
            intro = f"Para enviar a: {email}\nSubject: {subject}\n\n"
            
        full_body_text = intro + body_text
        
        if self.use_ses:
            return self._send_via_ses(recipient, full_subject, body_html, full_body_text)
        else:
            return self._send_via_smtp(recipient, full_subject, body_html, full_body_text)

    def send_direct_email(self, to_email, subject, body_html, body_text):
        if self.use_ses:
            return self._send_via_ses(to_email, subject, body_html, body_text)
        else:
            return self._send_via_smtp(to_email, subject, body_html, body_text)

if __name__ == "__main__":
    # Test
    sender = EmailSender()
    success = sender.send_mep_email(
        "Test Subject", "Atlantis", "test@example.com", 
        "Test Subject", "<h1>Test</h1><p>This is a test.</p>", "Test Plain Text"
    )
    print(f"Email sent: {success}")

