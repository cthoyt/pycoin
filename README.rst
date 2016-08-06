pycoin
======

:code:`pycoin` is a command line utility to semi-randomly choose a movie to watch from the list of movies you would like to see.

Installation for Development
----------------------------

The best way to install :code:`pycoin` at the moment is via the following procedure. In addition to the source of the script, which you can obtain via :code:`git clone https://github.com/scolby33/pycoin.git`, this also requires :code:`virtualenv` and :code:`pip`. Most Python installations come with :code:`pip`, but if yours does not, the docs `here <https://pip.pypa.io/en/stable/installing/>`_ provide an overview of the process of getting this essential tool. Once :code:`pip` is installed, getting :code:`virtualenv` is as simple as :code:`pip install virtualenv`.

Once the requirements are met, switch to the root directory of the :code:`pycoin` source (the folder containing :code:`setup.py`) and execute the following commands::

virtualenv venv
source venv/bin/activate
pip install --editable .

Afterwards, :code:`pycoin` can be executed by name as long as you're in the virtualenv. To leave the virtualenv, execute :code:`deactivate`. To return to an existing installation, just navigate to the root directory of the :code:`pycoin` source again and run :code:`source venv/bin/activate`.
