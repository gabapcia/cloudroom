import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from util.exceptions import MailError


def send_message(subject:str, template:str) -> None:
    message = Mail(
        from_email='no-reply@cloudroom.com.br',
        to_emails=os.getenv('MY_EMAIL'),
        subject=subject,
        html_content=template
    )
    try:
        SendGridAPIClient(os.getenv('SENDGRID_API_KEY')).send(message)
    except Exception as e:
        raise MailError
