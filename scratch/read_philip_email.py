import imaplib
import email
from email.header import decode_header
import sys

def main():
    username = "elswork@gmail.com"
    password = "drwi efum akfv pfsa"
    
    print("Connecting to Gmail IMAP...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        print("Logged in successfully.")
    except Exception as e:
        print(f"Failed to connect or login: {e}")
        sys.exit(1)
        
    folder = '"[Gmail]/Todos"'
    print(f"Selecting {folder}...")
    status, _ = mail.select(folder, readonly=True)
    if status != "OK":
        print(f"Failed to select folder {folder}")
        sys.exit(1)
        
    status, messages = mail.search(None, 'ALL')
    if status == "OK" and messages[0]:
        mail_ids = messages[0].split()
        total = len(mail_ids)
        print(f"Total emails in Todos: {total}")
        
        # Let's inspect the last 50 emails
        start_idx = max(0, total - 50)
        recent_ids = mail_ids[start_idx:]
        
        print("\n--- Last 50 Emails in All Mail (Todos) ---")
        for mid in reversed(recent_ids):
            status, data = mail.fetch(mid, "(RFC822)")
            if status == "OK":
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Decode subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    try:
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                    except Exception:
                        subject = str(subject)
                        
                # Decode sender
                from_, encoding = decode_header(msg["From"])[0]
                if isinstance(from_, bytes):
                    try:
                        from_ = from_.decode(encoding or "utf-8", errors="ignore")
                    except Exception:
                        from_ = str(from_)
                        
                date_ = msg["Date"]
                print(f"ID: {mid.decode()} | From: {from_} | Subject: {subject} | Date: {date_}")
            else:
                print(f"Failed to fetch ID {mid.decode()}")
    else:
        print("No emails found.")
        
    mail.close()
    mail.logout()

if __name__ == "__main__":
    main()
