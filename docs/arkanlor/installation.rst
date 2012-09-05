Installation
============

Requirements
------------
To run arkanlor either locally or on a server, you need to install following
Software system wide:
    * python
    * python-imaging (often referred to as PIL)
    * python-twisted (you can install this with pip in some setups)
    * python-numpy (or if installed by pip: liblapack-dev libblas-dev )
    * pip

You might want to create a virtual environment (to your liking)
Now check out the project into a working folder if you havent already.
Install the rest of the requirements with pip:
    * pip -r requirements.txt
    (contains platform indepenent dependencies only, like django)

Database Setup
--------------
Atm. database is not automatically generated.
If you are familiar with django, then you might wanna know, arkanlor is also a django app.
in src/ execute manage.py:
    python manage.py syncdb
Create an admin account.

now in src/arkanlor run:
    python generate_world.py
This creates a world entry in the database.

You can now already start and test the server:
    python start.py

The standard database is created in project root / arkanlor.db
You can use the django settings to target any other db system you want
Create a local_settings.py file to overwrite standard settings in src/arkanlor
You can also wrap arkanlor in a django application and target the same
database through a webserver.


