 
import smtplib

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "senin_emailin@gmail.com"
SMTP_PASSWORD = "uygulama_sifren"

try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    print("✅ SMTP bağlantısı başarılı!")
    server.quit()
except Exception as e:
    print(f"🚨 SMTP bağlantısı başarısız: {e}")
