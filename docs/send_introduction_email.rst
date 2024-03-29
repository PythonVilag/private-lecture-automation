Send Introduction Email
=======================

Upon request the script sends out an email containing the most up-to-date information about the lectures.


Setting up the email template
-----------------------------

For the script an html template must be prepared that will be used as the body of the email.
This template must be located at ``data/introduction.html``.

The html file can contain placeholders that will be replaced before the email is sent.
This can be useful when you want to make the email more personal, or you want to include data that changes regularly.
The placeholders must be surrounded by square brackets, e.g. ``[NAME]``, ``[PRICE]``.

It is also possible to include images in the email.
The images must be located in the ``data/`` folder as well.
It is important to keep in mind, that in order to include images the html file must also be extended with the
appropriate ``<img src="cid:IMAGE_NAME"`` tag.


Using Send Introduction Email
-----------------------------

A simple example of using the `send_introduction_email` functionality:

.. code-block:: python

    from private_lecture_automation import send_introduction_email

    send_introduction_email(
        recipient_email="john.doe@example.com",  # email address of the recipient
        included_images=["logo.png"],  # images included in the email
        values_to_replace={  # values that will be replaced in the email template
            "NAME": "John Doe",
            "PRICE": "10 USD",
        },
    )
