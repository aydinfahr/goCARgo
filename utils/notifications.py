# utils/notifications.py

from twilio.rest import Client
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from fastapi import BackgroundTasks

# ✅ Twilio API Credentials (Çevre değişkenlerinden alınmalı)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "YOUR_TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "YOUR_TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "YOUR_TWILIO_PHONE")

# Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ✅ SendGrid API Credentials
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "YOUR_SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@example.com")

# ✅ Sistem Admin Bilgileri (Çevre değişkenleri ile alınmalı)
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "+1234567890")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")

def send_notifications(background_tasks: BackgroundTasks, user_phone: str, user_email: str):
    """
    Sends both SMS and Email notifications asynchronously using BackgroundTasks.
    """
    background_tasks.add_task(send_sms, user_phone, "Your ride has been confirmed! ✅")
    background_tasks.add_task(send_email, user_email, "Booking Confirmed ✅", "<h1>Your ride is confirmed!</h1>")

def send_sms(to_number: str, message: str):
    """
    Sends an SMS notification using Twilio API.
    """
    try:
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        print(f"✅ SMS Sent to {to_number} | SID: {message.sid}")
        return True
    except Exception as e:
        print(f"🚨 SMS Sending Failed: {e}")
        return False

def send_email(to_email: str, subject: str, content: str):
    """
    Sends an email notification using SendGrid API.
    """
    try:
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Email Sent to {to_email} | Status Code: {response.status_code}")
        return True
    except Exception as e:
        print(f"🚨 Email Sending Failed: {e}")
        return False

def send_notification(user_id: int, message: str):
    """
    Kullanıcıya bildirim gönderir (SMS veya e-posta).
    """
    print(f"Notification sent to user {user_id}: {message}")

def moderate_text(text: str) -> bool:
    """
    Metin moderasyonu yapar (örneğin, uygunsuz içerik kontrolü).
    """
    inappropriate_words = ["badword1", "badword2"]  # Örnek uygunsuz kelimeler
    for word in inappropriate_words:
        if word in text.lower():
            return False  # Uygunsuz içerik bulundu
    return True  # Metin uygun

def send_payment_receipt(email: str, amount: float, ride_id: int):
    """
    Sends a payment receipt to the user's email.
    """
    message = Mail(
        from_email=os.getenv("SENDER_EMAIL"),
        to_emails=email,
        subject="Payment Receipt - GoCarGo",
        html_content=f"""
        <h3>Payment Receipt</h3>
        <p>Thank you for your payment of <b>${amount}</b> for Ride ID: {ride_id}.</p>
        <p>Have a great trip!</p>
        """
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"Email sent! Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

# ✅ **SİSTEM BİLDİRİMLERİ GÖNDERME FONKSİYONU**
def send_system_notifications():
    """
    Sends system-wide notifications (example: maintenance alerts).
    """
    message = "🚀 System update: New features added to goCARgo!"
    subject = "🔔 goCARgo System Notification"

    # ✅ **Adminlere SMS ve E-Posta Gönder**
    send_sms(ADMIN_PHONE, message)
    send_email(ADMIN_EMAIL, subject, message)

    print("✅ System-wide notifications sent!")
