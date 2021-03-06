instaparse
======

A python script that generates simple file parsers.

Development
===========

To get the package simply pull from the repository:

    git clone https://github.com/ImpGuard/instaparse.git <project_directory>

In order to install the dependencies, navigate to the project directory and use
pip. Note using virtualenv in this example is optional:

    virtualenv <venv>               # Create a virtual environment if desired
    source <venv>/bin/activate      # Activate the environment if installed
    pip install -r requirements.txt # Install the necessary modules
    ...
    ...
    deactivate                      # Leave the virtual environment when work is finished

All the source files are located within the folder `instaparse`. In order to test
the script, use nose within the home directory (which is installed as a
dependency):

    make check                      # Calls nose indirectly

See the documentation for [nose](https://nose.readthedocs.org/en/latest/) for
more information on how testing works. All tests are located within the
folder `tests`.

Link to [documentation](docs/specs.md)
