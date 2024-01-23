#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99

__author__ = 'Dieter Vansteenwegen'
__email__ = 'dieter.vansteenwegen@vliz.be'
__project__ = 'Panthyr'
__project_link__ = 'https://waterhypernet.org/equipment/'

import logging
import pathlib
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union


def initialize_logger() -> logging.Logger:
    """Set up logger
    If the module is ran as a module, name logger accordingly as a sublogger.
    Returns:
        logging.Logger: logger instance
    """
    if __name__ == '__main__':
        return logging.getLogger(__name__)
    else:
        return logging.getLogger()


log = initialize_logger()


class pEmail:
    def __init__(
        self,
        server: str,
        username: str,
        password: str,
        sender: Union[str, None] = None,
        port: int = 587,
    ) -> None:
        """pEmail object constructor.

        Args:
            server (str): server address.
            username (str): username for login
            password (str): password for login
            sender (Union[str, None]): sender email adress. If None, username is used as sender
            port (int): port to connect to server. Either 587 (STARTTLS) or 465 (TTL)
                    Defaults to 587 (STARTTLS)

        Raises:
            ValueError: If port is not 587 or 465
        """
        self._server = server
        self._username = username
        self._password = password
        self._sender = sender or username
        self._port = port
        if self._port not in [587, 465]:
            msg = f'Port must be either 587 (STARTTLS) or 465 (TTL), not {port}.'
            raise ValueError(msg)

    def create_email(self, to: str, subject: str, text: str, station_id: str) -> None:
        """Create email to sender.

        Create email with receiver, subject line and text.

        Args:
            station_id (str): station id of the sender
            to (str): email address of receiver
            subject (str): subject line
            text (str): body text
        """
        self._to = to
        self._msg = MIMEMultipart()
        self._msg['From'] = self._sender
        self._msg['To'] = to
        self._msg['Subject'] = f'[PANTHYR {station_id}] {subject}'
        self._msg.attach(MIMEText(text, 'plain'))

    def add_text(self, text: str) -> None:
        self._msg.attach(MIMEText(text, 'plain'))

    def add_attachment(self, fn: Union[pathlib.Path, str]) -> None:
        """Add an attachment to email.

        Args:
            fn (Union[pathlib.Path, str]): Path to file to attach.

        Raises:
            ValueError: If attachment file does not exist.
        """
        if not isinstance(fn, pathlib.Path):
            fn = pathlib.Path(fn)
        if not (fn.exists() and fn.is_file()):
            msg = f'Requested attachment {fn} does not exist.'
            raise ValueError(msg)
        part = MIMEBase('application', 'octet-stream')

        with fn.open(mode='rb') as attachment:
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename = {fn.name}')
        self._msg.attach(part)

    def send(self) -> None:
        """Send email message.

        Converts message to string and send using SSL or STARTTLS over SMTP.
        """
        msg = 'Sending email message.'
        log.debug(msg)
        msg_txt = self._msg.as_string()

        context = ssl.create_default_context()
        if self._port == 465:  # SSL
            log.debug('Starting connection over SSL.')
            with smtplib.SMTP_SSL(
                host=self._server,
                port=465,
                context=context,
            ) as server:
                server.login(user=self._username, password=self._password)
                server.sendmail(from_addr=self._sender, to_addrs=self._to, msg=msg_txt)
        elif self._port == 587:  # TLS
            log.debug('Starting connection using TLS over SMTP.')
            with smtplib.SMTP(host=self._server, port=587) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(user=self._username, password=self._password)
                server.sendmail(from_addr=self._sender, to_addrs=self._to, msg=msg_txt)
