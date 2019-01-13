=================
pytest-concurrent
=================
.. image:: https://badges.gitter.im/pytest-concurrent/Lobby.svg
   :alt: Join the chat at https://gitter.im/pytest-concurrent/Lobby
   :target: https://gitter.im/pytest-concurrent/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
   
.. image:: https://badge.fury.io/py/pytest-concurrent.svg
    :target: https://badge.fury.io/py/pytest-concurrent
    :alt: See package version on PYPI

.. image:: https://travis-ci.org/reverbc/pytest-concurrent.svg?branch=master
    :target: https://travis-ci.org/reverbc/pytest-concurrent
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/66752as6ai1v85re/branch/master?svg=true
    :target: https://ci.appveyor.com/project/reverbc/pytest-concurrent/branch/master
    :alt: See Build Status on AppVeyor
   
Concurrently execute pytest testing with `multi-thread`, `multi-process` and `gevent`

----

This `Pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.


Features
--------

* Testing concurrently with pytest, using one of the three modes
    - Multiprocess (--concmode=mproc)
    - Multithread (--concmode=mthread)
    - Asynchronous Network with gevent (--concmode=asyncnet)
* The ability to designate the amount of work to be used for testing
* The ability to put your tests into separate groups

Requirements
------------

* Python3 version [3.4+]
* Make sure you have the latest version of pytest installed for your environment


Installation
------------

You can install "pytest-concurrent" via `pip`_ from `PyPI`_::

    $ pip install pytest-concurrent


Usage
-----

* Use this plugin by running pytest normally and use --concmode [mode name]
* [mode name] should be one of the following (mproc, mthread, or asyncnet)

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-concurrent" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/reverbc/pytest-concurrent/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi
