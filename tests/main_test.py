from private_lecture_automation.main import ConfigData


def test_config_data() -> None:
    ConfigData(
        email_address="your@email.com",
        email_password="your_password",  # noqa: S106
        host="smtp.gmail.com",
        port=465,
    )
