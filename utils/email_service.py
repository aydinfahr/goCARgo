

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import EmailStr

SMTP_SERVER = "localhost"
SMTP_PORT = 1025  # MailHog'un varsayılan SMTP portu

def send_verification_email(email: EmailStr, verification_link: str):
    sender_email = "noreply@gocargo.com"
    subject = "GoCargo - Verify Your Email"
    body = f"""
    <html>
        <body>
            <h2>Verify Your Email</h2>
            <p>Click the link below to verify your email:</p>
            <a href="{verification_link}">Verify Email</a>
        </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.sendmail(sender_email, email, msg.as_string())
        print(f"Verification email sent to {email}")
    except Exception as e:
        print(f"Error sending email: {e}")
