from private_lecture_automation.main import ConfigData


def test_config_data() -> None:
    config_data = ConfigData(
        email_address="your@email.com",
        email_password="your_password",
        host="smtp.gmail.com",
        port=465,
    )
