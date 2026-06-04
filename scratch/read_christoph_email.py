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
        
    mail.select("inbox")
    
    # We want to fetch message ID: 4
    mid = b"4"
    print(f"Fetching email with ID: {mid.decode()}")
    status, data = mail.fetch(mid, "(RFC822)")
    
    if status == "OK":
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        # Decode subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="ignore")
            
        # Decode sender
        from_, encoding = decode_header(msg["From"])[0]
        if isinstance(from_, bytes):
            from_ = from_.decode(encoding or "utf-8", errors="ignore")
            
        date_ = msg["Date"]
        print("\n" + "="*50)
        print(f"FROM: {from_}")
        print(f"SUBJECT: {subject}")
        print(f"DATE: {date_}")
        print("="*50 + "\n")
        
        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
                
        if body:
            print("--- FIRST 4000 CHARACTERS OF BODY ---")
            print(body[:4000])
            print("-------------------------------------")
        else:
            print("No text body found.")
        print("\n" + "="*50)
    else:
        print("Failed to fetch email.")
        
    mail.close()
    mail.logout()

if __name__ == "__main__":
    main()
