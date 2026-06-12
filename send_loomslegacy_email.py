import os
import smtplib
from email.message import EmailMessage


SMTP_HOST = os.environ.get("PICKWISE_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("PICKWISE_SMTP_PORT", "587"))
SMTP_USER = os.environ.get("PICKWISE_SMTP_USER", "sivashankarimurugesan@pickwisecom.com")
SMTP_PASSWORD = os.environ.get("PICKWISE_SMTP_PASSWORD")


def build_message():
    message = EmailMessage()
    message["To"] = "support@loomslegacy.com"
    message["From"] = f"Niharika <{SMTP_USER}>"
    message["Subject"] = "Hi from Niharika"
    message.set_content(
        """Hi Looms Legacy team,

This is Sivashankari from Niharika. I wanted to say hi and connect with your team.

I am also building PickWise, a lightweight recommendation assistant that can help shoppers choose the right products before checkout. I would be happy to offer Looms Legacy a free trial if you would like to try it on your store.

Best,
Sivashankari Murugesan
Niharika
sivashankarimurugesan@pickwisecom.com
"""
    )
    return message


def main():
    if not SMTP_PASSWORD:
        raise SystemExit("Set PICKWISE_SMTP_PASSWORD before sending.")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(build_message())

    print("Email sent to support@loomslegacy.com")


if __name__ == "__main__":
    main()
