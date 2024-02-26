"""
Short description and source of base code.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import importlib.metadata

from private_lecture_automation.main import (
    check_calendar_event,
    send_calendar_event,
    send_introduction_email,
)

__all__ = ["send_introduction_email", "send_calendar_event", "check_calendar_event"]
__version__ = importlib.metadata.version("private-lecture-automation")
