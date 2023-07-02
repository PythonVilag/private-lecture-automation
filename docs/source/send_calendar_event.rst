Send Calendar Event
===================

Upon request the script sends out an email containing the calendar event of the next lecture for the client.


Setting up student data
-----------------------

For the script an json object must be prepared that is used to contain information about the students.
This file must be located at ```data/students.json``.

The file is structured as follows:

.. code-block:: JSON

    {
        "John Doe": {  // The reference name
            "name": "John Doe",  // The name the student will be addressed with
            "email": "john.doe@example.com",  // Address the calendar event will be sent to
            "content_link": "https://www.pythonvilag.hu/",  // Student specific content link
            "day": "2",  // The day of the week the lecture is held on (Monday = 0, ...)
            "time": "1630",  // The time of the lecture in 24h format
            "duration": "90", // The duration of the lecture in minutes
            "occasion_number": "6"  // The number of upcoming lecture
        },
    }


Using Send Calendar Event
-------------------------

A simple example of using the `send_calendar_event` functionality:

.. code-block:: python

    from private_lecture_automation import send_calendar_event

    send_calendar_event(
        student_name="Arany Barna",  # Student reference, must match key in the json file
        time="1700",  # Optional: temporal change in the lecture time
        duration="60",  # Optional: temporal change in the lecture duration
    )
