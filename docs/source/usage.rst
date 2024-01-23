===============================
Panthyr email example code
===============================

Example code:

.. code:: python

    >>> from panthyr_email.p_email import pEmail

    >>>     mail = pEmail(
        server='server',
        username='username',
        password='password',
        port=587
    )
    mail.create_email(
        to='to_email',
        subject='subject line',
        text="body text",
        station_id="test_station",
    )
    mail.add_attachment(
        r'path_to_file/file_as_path.txt'
    )
    pathlib_path = pathlib.Path('path_to_file/file_as_path.txt')
    mail.add_attachment(
        pathlib_path
    )
    mail.send()