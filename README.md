heimer
======

A python script that generates simple file parsers.

Development
===========

To get the package simply pull from the repository:

    git clone https://github.com/ImpGuard/heimer.git <project_directory>

In order to install the dependencies, navigate to the project directory and use
pip. Note using virtualenv in this example is optional:

    virtualenv <venv>               # Create a virtual environment if desired
    source <venv>/bin/activate      # Activate the environment if installed
    pip install -r requirements.txt # Install the necessary modules

All the source files are located within the folder `heimer`. In order to test
the script, use nose within the home directory (which is installed as a
dependency):

    nosetests

See the documentation for [nose](https://nose.readthedocs.org/en/latest/) for
more information on how testing works. All tests are located within the
folder `tests`.
