"""
All the functions that are used by the private lecture automation package.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import json
import os
import smtplib
import textwrap
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.header import Header
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid

from dotenv import dotenv_values
from icalendar import Calendar, Event


@dataclass
class ConfigData:
    """Dataclass for storing the configuration data."""

    email_address: str
    email_password: str
    host: str
    port: int


data_folder = os.path.join(os.path.dirname(__file__), "data")


def send_introduction_email(
    recipient_email: str,
    included_images: list[str] | None = None,
    values_to_replace: dict[str, str] | None = None,
) -> None:
    """Sends out an email to the recipient with the introduction email template.

    Args:
        recipient_email (str): The email address of the recipient.
        included_images (list[str] | None, optional): A list of image names that are included in
        the email. Defaults to None.
        values_to_replace (dict[str, str] | None, optional): Key-value pairs defined in the form
        of a dictionary, there they key elements are replaced in the html template with the values.
        Defaults to None.
    """
    config_data = _load_config()
    if included_images is None:
        included_images = []
    included_image_ids = {}

    message = EmailMessage()
    message["Subject"] = "Különóra információk"
    message["From"] = formataddr((str(Header("PythonVilág", "utf-8")), config_data.email_address))
    message["To"] = recipient_email

    print(f"{data_folder}/introduction.html")

    with open(f"{data_folder}/introduction.html", mode="r", encoding="utf-8") as message_file:
        message_body = message_file.read()

    if values_to_replace is not None:
        for key, value in values_to_replace.items():
            message_body = message_body.replace(f"[{key}]", value)

    for image_name in included_images:
        included_image_ids[image_name] = make_msgid()
        message_body = message_body.replace(f"cid:{image_name}", f"cid:{included_image_ids[image_name][1:-1]}")

    message.add_alternative(message_body, subtype="html")

    try:
        for image_name in included_images:
            with open(f"{data_folder}/{image_name}", mode="rb") as img_file:
                message.get_payload()[0].add_related(
                    img_file.read(), "image", "png", cid=included_image_ids[image_name]
                )
    except KeyError:
        pass

    _send_email(config_data, message)


def check_calendar_event(number_of_days: int = 5) -> None:
    """Checks if there is a scheduled lesson in the next number_of_days days and if so, it sends
    out a calendar event to the client.

    Args:
        number_of_days (int, optional): The number of days we check ahead. Defaults to 5.
    """
    with open(f"{data_folder}/students.json", mode="r", encoding="utf-8") as students_file:
        students_data = json.load(students_file)

    for student_name, student_data in students_data.items():
        day = int(student_data["day"])
        today = datetime.now()
        days_ahead = day - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7

        if days_ahead == number_of_days:
            send_calendar_event(student_name)


def send_calendar_event(student_name: str, **kwargs: str) -> None:
    """Sends out a calendar event containing a meeting invitation for the next lesson of the
    student. It is also possible to temporarily overwrite some details of the next lesson.

    Args:
        student_name (str): The name of the student stored in the students.json file.
        **kwargs (str): Key-value pairs defined in the form of a dictionary where if the key is
        present in the student's data, it will be temporarily overwritten with the value.
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
        """
    )
    text_part = MIMEText(message_body, "plain")
    message.attach(text_part)

    ical_part = _create_calendar_event(student_data, config_data.email_address)
    message.attach(ical_part)

    _send_email(config_data, message)


def _load_config() -> ConfigData:
    """Tries to load the configuration data from the .env file. If it fails, it tries to load the
    configuration data from the environment variables.

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
        raise KeyError("Config variable is missing. Check .env file or add environment variables.") from exception

    return config_data


def _load_student_data(student_name: str, increment_occasion_number: bool = True) -> dict[str, str]:
    """_summary_.

    Args:
        student_name (str): _description_
        increment_occasion_number (bool, optional): _description_. Defaults to True.

    Returns:
        dict[str, str]: _description_
    """
    with open(f"{data_folder}/students.json", "r+", encoding="utf8") as students_file:
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
    """_summary_.

    Args:
        student_data (dict[str, str]): _description_
        email_address (str): _description_

    Returns:
        MIMEApplication: _description_
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

            {student_data["content_link"]}"""
        ),
    )

    ## Start and end time
    day = int(student_data["day"])
    hour = int(student_data["time"][:2])
    minute = int(student_data["time"][2:])
    duration = int(student_data["duration"])
    today = datetime.now()

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
    """_summary_.

    Args:
        config_data (ConfigData): _description_
        message (EmailMessage | MIMEMultipart): _description_
    """
    with smtplib.SMTP_SSL(config_data.host, config_data.port) as smtp:
        smtp.login(config_data.email_address, config_data.email_password)
        smtp.send_message(message)
