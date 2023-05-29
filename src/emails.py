import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Email:
    """Class to send emails using Gmail SMTP server."""

    def __init__(self, sender: str, password: str) -> None:
        """Initialize the Email class."""
        self.sender = sender
        self.password = password

    def send(self, subject: str, body: str, receivers: list[str]) -> None:
        """Send an email to the specified receivers."""
        msg = MIMEMultipart()
        msg["From"] = self.sender
        msg["To"] = ", ".join(receivers)
        msg["Subject"] = subject
        msg.attach(MIMEText(body.encode("utf-8"), "html", "utf-8"))

        Email.__send(msg, self.sender, self.password, receivers)

    @staticmethod
    def __send(
        message: MIMEMultipart, sender_email: str, password: str, receivers: list[str]
    ) -> None:
        """Helper method use Gmail to send the email."""
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receivers, message.as_string())
