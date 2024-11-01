import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formataddr, formatdate
from pathlib import Path

import requests

from app.core.config import settings


def send_mail(
    send_to,
    subject,
    message,
    send_from=settings.SMTP_FROM,
    files=[],
    server=settings.SMTP_HOST,
    port=settings.SMTP_PORT,
    username=settings.SMTP_USER,
    password=settings.SMTP_PASSWORD,
    use_tls=True):

    try:
        msg = MIMEMultipart()
        msg["From"] = formataddr(("Facturacion INSORPA", send_from))
        msg["To"] = COMMASPACE.join(send_to)
        msg["Date"] = formatdate(localtime=True)
        msg["Subject"] = subject

        msg.attach(MIMEText(message))

        for path in files:
            response = requests.get(path)
            part = MIMEBase("application", "octet-stream")
            part.set_payload(response.content)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={Path(path).name}",
            )
            msg.attach(part)

        smtp = smtplib.SMTP(server, port)
        smtp.starttls()
        smtp.login(username, password)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return False
