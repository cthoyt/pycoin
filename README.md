#pycoin

`pycoin` is a command line utility to semi-randomly choose a movie to watch from the list of movies you would like to see.

##Installation for Development

The best way to install `pycoin` at the moment is via the following procedure. In addition to the source of the script, which you can obtain via `git clone https://github.com/scolby33/pycoin.git`, this also requires `virtualenv` and `pip`. Most Python installations come with `pip`, but if yours does not, the docs [here](https://pip.pypa.io/en/stable/installing/) provide an overview of the process of getting this essential tool. Once `pip` is installed, getting `virtualenv` is as simple as `pip install virtualenv`.

Once the requirements are met, switch to the root directory of the `pycoin` source (the folder containing `setup.py`) and execute the following commands:

```bash
virtualenv venv
source venv/bin/activate
pip install --editable .
```

Afterwards, `pycoin` can be executed by name as long as you're in the virtualenv. To leave the virtualenv, execute `deactivate`. To return to an existing installation, just navigate to the root directory of the `pycoin` source again and run `source venv/bin/activate`.
