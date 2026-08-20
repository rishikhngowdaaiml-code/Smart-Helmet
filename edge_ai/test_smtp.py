import smtplib
from email.message import EmailMessage
import sys

def send_test_email(to_email):
    msg = EmailMessage()
    msg.set_content("Hello! This is a test from the Edge AI Smart Helmet system.")
    msg['Subject'] = 'Traffic Violation Report'
    msg['From'] = 'smarthelmet@local.system'
    msg['To'] = to_email

    try:
        # Using Gmail's primary MX record
        server = smtplib.SMTP('gmail-smtp-in.l.google.com', 25)
        server.set_debuglevel(1)
        server.send_message(msg)
        server.quit()
        print("Success")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    send_test_email("rishi11gowda@gmail.com")
