Installation
============

This page describes how to download the package and what other files are needed to run it.

Getting the source code
-----------------------

Installing the package could be done by cloning the repository or via PyPI.

.. code-block:: console

    git clone https://github.com/PythonVilag/private-lecture-automation.git

or

.. code-block:: console

    pip install private-lecture-automation

The main advantage of using the cloning solution is that you are provided with a ``/data`` folder
that contains example files for the different functionalities.


Setting up necessary files
--------------------------

Currently all the available functionalities rely on sending out emails.
To achieve this the necessary information must be provided to the package.

The recommended way of doing this is by creating a ``.env`` file in the root directory of the package.
This file should look like this:

.. code-block:: bash

    EMAIL_ADDRESS = your@email.com
    EMAIL_PASSWORD = your_password
    HOST = smtp.gmail.com
    PORT = 465

In case you are using a different email provider, you should change the ``HOST`` and ``PORT`` variables accordingly.


Other configurations
--------------------

Different functionalities may require other files and configurations.
These are described in the corresponding sections.
