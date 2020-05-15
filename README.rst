configmagick_wine
=================

|Pypi Status| |license| |maintenance|

|Build Status| |Codecov Status| |Better Code| |code climate| |snyk security|

.. |license| image:: https://img.shields.io/github/license/webcomics/pywine.svg
   :target: http://en.wikipedia.org/wiki/MIT_License
.. |maintenance| image:: https://img.shields.io/maintenance/yes/2019.svg
.. |Build Status| image:: https://travis-ci.org/bitranox/configmagick_wine.svg?branch=master
   :target: https://travis-ci.org/bitranox/configmagick_wine
.. for the pypi status link note the dashes, not the underscore !
.. |Pypi Status| image:: https://badge.fury.io/py/configmagick-wine.svg
   :target: https://badge.fury.io/py/configmagick_wine
.. |Codecov Status| image:: https://codecov.io/gh/bitranox/configmagick_wine/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/bitranox/configmagick_wine
.. |Better Code| image:: https://bettercodehub.com/edge/badge/bitranox/configmagick_wine?branch=master
   :target: https://bettercodehub.com/results/bitranox/configmagick_wine
.. |snyk security| image:: https://snyk.io/test/github/bitranox/configmagick_wine/badge.svg
   :target: https://snyk.io/test/github/bitranox/configmagick_wine
.. |code climate| image:: https://api.codeclimate.com/v1/badges/7c7107a97c1ac7c03b35/maintainability
   :target: https://codeclimate.com/github/bitranox/configmagick_wine/maintainability
   :alt: Maintainability

some convenience functions for logging

supports python 3.7 and possibly other dialects.

`100% code coverage <https://codecov.io/gh/bitranox/configmagick_wine>`_, mypy static type checking, tested under `Linux, OsX, Windows and Wine <https://travis-ci.org/bitranox/configmagick_wine>`_, automatic daily builds  and monitoring

----

- `Installation and Upgrade`_
- `Basic Usage`_
- `Requirements`_
- `Acknowledgements`_
- `Contribute`_
- `Report Issues <https://github.com/bitranox/configmagick_wine/blob/master/ISSUE_TEMPLATE.md>`_
- `Pull Request <https://github.com/bitranox/configmagick_wine/blob/master/PULL_REQUEST_TEMPLATE.md>`_
- `Code of Conduct <https://github.com/bitranox/configmagick_wine/blob/master/CODE_OF_CONDUCT.md>`_
- `License`_
- `Changelog`_

----

Installation and Upgrade
------------------------

From source code:

.. code-block:: bash

    # normal install
    python setup.py install
    # test without installing
    python setup.py test

via pip latest Release:

.. code-block:: bash

    # latest Release from pypi
    pip install configmagick_wine

    # test without installing
    pip install configmagick_wine --install-option test

via pip latest Development Version:

.. code-block:: bash

    # upgrade all dependencies regardless of version number (PREFERRED)
    pip install --upgrade git+https://github.com/bitranox/configmagick_wine.git --upgrade-strategy eager
    # normal install
    pip install --upgrade git+https://github.com/bitranox/configmagick_wine.git
    # test without installing
    pip install git+https://github.com/bitranox/configmagick_wine.git --install-option test

via requirements.txt:

.. code-block:: bash

    # Insert following line in Your requirements.txt:
    # for the latest Release:
    configmagick_wine
    # for the latest Development Version :
    git+https://github.com/bitranox/configmagick_wine.git

    # to install and upgrade all modules mentioned in requirements.txt:
    pip install --upgrade -r /<path>/requirements.txt

via python:

.. code-block:: python

    # for the latest Release
    python -m pip install upgrade configmagick_wine

    # for the latest Development Version
    python -m pip install upgrade git+https://github.com/bitranox/configmagick_wine.git

Basic Usage
-----------

TBA

Requirements
------------
following modules will be automatically installed :

.. code-block:: bash

    ## Test Requirements
    ## following Requirements will be installed temporarily for
    ## "setup.py install test" or "pip install <package> --install-option test"
    typing ; python_version < "3.5"
    pathlib; python_version < "3.4"
    mypy ; platform_python_implementation != "PyPy" and python_version >= "3.5"
    pytest
    pytest-pep8 ; python_version < "3.5"
    pytest-pycodestyle ; python_version >= "3.5"
    pytest-mypy ; platform_python_implementation != "PyPy" and python_version >= "3.5"
    pytest-runner

    ## Project Requirements
    fire
    configmagick_linux @ git+https://github.com/bitranox/configmagick_linux.git

Acknowledgements
----------------

- special thanks to "uncle bob" Robert C. Martin, especially for his books on "clean code" and "clean architecture"

Contribute
----------

I would love for you to fork and send me pull request for this project.
- `please Contribute <https://github.com/bitranox/configmagick_wine/blob/master/CONTRIBUTING.md>`_

License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

---

Changelog
=========

0.0.1
-----
2019-09-03: Initial public release

