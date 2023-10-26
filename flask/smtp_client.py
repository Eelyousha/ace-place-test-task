import os
import smtplib
import ssl
from dotenv import load_dotenv


class SMTPServer(object):
    def __init__(self):
        load_dotenv()

        SMTP_HOST = os.getenv("SMTP_HOST")
        SMTP_PORT = os.getenv("SMTP_PORT")
        SMTP_LOGIN = os.getenv("SMTP_LOGIN")
        SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

        context = ssl.create_default_context()
        self.server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        self.server.starttls(context=context)

        self.server.login(SMTP_LOGIN, SMTP_PASSWORD)

    def send_message(self, to: str, message: str):
        SMTP_EMAIL = os.getenv("SMTP_EMAIL")
        message = message.encode("utf-8")
        self.server.sendmail(SMTP_EMAIL, to, message)
