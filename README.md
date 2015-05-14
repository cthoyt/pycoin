#pycoin

`pycoin` is a command line utility to semi-randomly choose a movie to watch from the list of movies you would like to see.

`pycoin` is being developed as an exercise in test-driven development. It is currently in a very incomplete state and will be updated as time allows. When I am comfortable with its completion level (basically, that it is useable in some form instead of just a collection of tests and classes as it is now), the license will be changed to be more permissive.

##Installation for Development
I recommend you install in a `virtualenv`.

    python setup.py develop

To run the tests:

    python setup.py test -a --cov=pycoin
