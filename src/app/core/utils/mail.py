import logging
import smtplib
import ssl
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

        for path in files:
            response = requests.get(str(path["link"]), allow_redirects=True)
            if response.status_code == 200:  # Verifica que se pueda acceder al archivo
                part = MIMEBase("application", "octet-stream")
                part.set_payload(response.content)
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename={Path(path["link"]).name}',
                )
                msg.attach(part)
            else:
                logging.error(f"No se pudo descargar el archivo: {path}. Error: {response.text}")
                # Insert the files as links in the email body
                message += f'\n{path["type"]}: {path["link"]}.'

        msg.attach(MIMEText(message))

        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(server, port, context=context) as smtp:
                smtp.login(username, password)
                smtp.sendmail(send_from, send_to, msg.as_string())
        else:
            with smtplib.SMTP(server, port) as smtp:
                smtp.ehlo()
                if use_tls:  # Aquí debe ser True para el puerto 2525
                    context = ssl.create_default_context()
                    smtp.starttls(context=context)
                    smtp.ehlo()
                smtp.login(username, password)
                smtp.sendmail(send_from, send_to, msg.as_string())

    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return False
