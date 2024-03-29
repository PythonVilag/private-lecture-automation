"""
Private Lecture Automation package content.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import json
import os
import smtplib
import textwrap
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.header import Header
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid
from pathlib import Path

from dotenv import dotenv_values
from icalendar import Calendar, Event


@dataclass
class ConfigData:
    """Dataclass for storing the configuration data."""

    email_address: str
    email_password: str
    host: str
    port: int


data_folder = Path(__file__).parent / "data"


def send_introduction_email(
    recipient_email: str,
    included_images: list[str] | None = None,
    values_to_replace: dict[str, str] | None = None,
) -> None:
    """Send out an email to the recipient with the introduction email template.

    Args:
        recipient_email (str): The email address of the recipient.
        included_images (list[str] | None, optional): A list of image names that are included in
        the email. Defaults to None.
        values_to_replace (dict[str, str] | None, optional): Keys to be replaced in the HTML template with the values.
        Defaults to None.
    """
    config_data = _load_config()

    if not included_images:
        included_images = []
    included_image_ids = {}

    message = EmailMessage()
    message["Subject"] = "Különóra információk"
    message["From"] = formataddr((str(Header("PythonVilág", "utf-8")), config_data.email_address))
    message["To"] = recipient_email

    with Path(f"{data_folder}/introduction.html").open(encoding="utf-8") as message_file:
        message_body = message_file.read()

    if values_to_replace:
        for key, value in values_to_replace.items():
            message_body = message_body.replace(f"[{key}]", value)

    for image_name in included_images:
        included_image_ids[image_name] = make_msgid()
        message_body = message_body.replace(f"cid:{image_name}", f"cid:{included_image_ids[image_name][1:-1]}")

    message.add_alternative(message_body, subtype="html")

    try:
        for image_name in included_images:
            with Path(f"{data_folder}/{image_name}").open(mode="rb") as image_file:
                message.get_payload()[0].add_related(
                    image_file.read(),
                    "image",
                    "png",
                    cid=included_image_ids[image_name],
                )
    except KeyError:
        print(f"Image {image_name} could not be found and is not included in the email.")  # noqa: T201

    _send_email(config_data, message)


def check_calendar_event(number_of_days: int = 5) -> None:
    """Check if there is a scheduled lesson in the next number_of_days days.

    If there is, it sends out a calendar event to the client.

    Args:
        number_of_days (int, optional): The number of days we check ahead. Defaults to 5.
    """
    with Path(f"{data_folder}/students.json").open(encoding="utf-8") as students_file:
        students_data = json.load(students_file)

    for student_name, student_data in students_data.items():
        day = int(student_data["day"])
        today = datetime.now(tz=UTC)
        days_ahead = day - today.weekday()
        days_ahead = days_ahead if days_ahead > 0 else days_ahead + 7

        if days_ahead == number_of_days:
            send_calendar_event(student_name)


def send_calendar_event(student_name: str, **kwargs: str) -> None:
    """Send out a calendar event containing the meeting invitation for the next lesson of the student.

    It is also possible to temporarily overwrite some details of the next lesson.

    Args:
        student_name (str): The name of the student stored in the students.json file.
        **kwargs (str): Keys present in the student's data will be temporarily overwritten with the value.
    """
    config_data = _load_config()

    student_data = _load_student_data(student_name)
    if kwargs:
        student_data.update(kwargs)

    message = MIMEMultipart()

    subject_text = f"Python Programozás {student_data['occasion_number']} - {student_data['name']}"
    message["Subject"] = subject_text

    message["From"] = formataddr((str(Header("PythonVilág", "utf-8")), config_data.email_address))
    message["To"] = student_data["email"]

    message_body = textwrap.dedent(
        f"""\
        Kedves {student_data["name"]}!

        A levélhez csatolva küldöm a következő óra naptári eseményét.
        A korábbi órák tartalmát megtalálod az alábbi linken:
        {student_data["content_link"]}

        Üdvözlettel,
        Dani
        """,
    )
    text_part = MIMEText(message_body, "plain")
    message.attach(text_part)

    ical_part = _create_calendar_event(student_data, config_data.email_address)
    message.attach(ical_part)

    _send_email(config_data, message)


def _load_config() -> ConfigData:
    """Load configurations from the .env file or environment variables.

    Raises:
        KeyError: If the configuration data is missing from the .env file and the environment.

    Returns:
        ConfigData: The configuration data.
    """
    config = dotenv_values(".env")
    if not config:
        config = dict(os.environ)
    try:
        config_data = ConfigData(
            email_address=str(config["EMAIL_ADDRESS"]),
            email_password=str(config["EMAIL_PASSWORD"]),
            host=str(config["HOST"]),
            port=int(str(config["PORT"])),
        )
    except KeyError as exception:
        error_message = "Config variable is missing. Check .env file or add environment variables."
        raise KeyError(error_message) from exception

    return config_data


def _load_student_data(student_name: str, increment_occasion_number: bool = True) -> dict[str, str]:  # noqa: FBT001, FBT002
    """Load the student's data from the students.json file.

    Args:
        student_name (str): The key of the student in the students.json file.
        increment_occasion_number (bool, optional): If True, the occasion number will be incremented by 1 in
        the students.json file. Defaults to True.

    Returns:
        dict[str, str]: The student's data from the file.
    """
    with Path(f"{data_folder}/students.json").open("r+", encoding="utf8") as students_file:
        students = json.load(students_file)
        student_data = dict(students[student_name])

        if increment_occasion_number:
            students = deepcopy(students)
            incremented_occasion_number = str(int(students[student_name]["occasion_number"]) + 1)
            students[student_name]["occasion_number"] = incremented_occasion_number
            students_file.seek(0)
            json.dump(students, students_file, ensure_ascii=False, indent=4)
            students_file.truncate()

    return student_data


def _create_calendar_event(student_data: dict[str, str], email_address: str) -> MIMEApplication:
    """Create a calendar event for the student's next lesson.

    Args:
        student_data (dict[str, str]): The student's data.
        email_address (str): The email address of the sender.

    Returns:
        MIMEApplication: The calendar event as an attachment.
    """
    # Event
    event = Event()
    event["organizer"] = f"mailto:{email_address}"

    ##  Event summary
    event.add(
        name="summary",
        value=f"Python Programozás {student_data['occasion_number']} - {student_data['name']}",
    )

    ## Description
    event.add(
        name="description",
        value=textwrap.dedent(
            f"""\
            A korábbi órák tartalmát megtalálod az alábbi linken:

            {student_data["content_link"]}""",
        ),
    )

    ## Start and end time
    day = int(student_data["day"])
    hour = int(student_data["time"][:2])
    minute = int(student_data["time"][2:])
    duration = int(student_data["duration"])
    today = datetime.now(tz=UTC)

    days_ahead = day - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7

    lesson_datetime = today + timedelta(days_ahead)
    lesson_datetime = lesson_datetime.replace(hour=hour, minute=minute, second=0)

    lesson_start = lesson_datetime
    lesson_end = lesson_datetime + timedelta(minutes=duration)

    event.add("dtstart", lesson_start)
    event.add("dtend", lesson_end)

    # Calendar
    calendar = Calendar()

    calendar.add_component(event)
    ical_data = calendar.to_ical()

    ical_part = MIMEApplication(ical_data, "octet-stream", Name="event.ics")
    ical_part["Content-Disposition"] = 'attachment; filename="event.ics"'

    return ical_part


def _send_email(config_data: ConfigData, message: EmailMessage | MIMEMultipart) -> None:
    """Send out an email with the given message.

    Args:
        config_data (ConfigData): Configuration data of the sender's email server.
        message (EmailMessage | MIMEMultipart): The content of the email to be sent.
    """
    with smtplib.SMTP_SSL(config_data.host, config_data.port) as smtp:
        smtp.login(config_data.email_address, config_data.email_password)
        smtp.send_message(message)
