import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


EMAIL_USER = ""
EMAIL_PASS = ""
EMAIL_RECIPIENTS = ["orestis.panagopou@upatras.gr"]


def send_mail(html_table, subject="PatrasAir offline stations"):
    """Sends mail to multiple recipients if necessary"""
    toaddr = ", ".join(EMAIL_RECIPIENTS)
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = toaddr
    msg["Subject"] = subject
    msg.attach(MIMEText(html_table, "html"))
    server = smtplib.SMTP_SSL("smtp.upatras.gr", 465)
    # gmail settings:
    # server = smtplib.SMTP("smtp.gmail.com", 587)
    # server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    text = msg.as_string()
    server.sendmail(EMAIL_USER, EMAIL_RECIPIENTS, text)
    server.quit()
    logger.info(f"Mail sent")
