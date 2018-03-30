======
Zigzag
======


.. image:: https://img.shields.io/travis/rcbops/zigzag.svg
        :target: https://travis-ci.org/rcbops/zigzag


Parse JUnitXML and upload test results to qTest Manager.

Quick Start Guide
-----------------

1. Clone the repo locally::

    $ git clone git@github.com:rcbops/zigzag.git

2. Install the package into your active Python environment::

    $ cd zigzag/
    $ python setup.py install

3. For more information on using the Zigzag launch help by::

    $ zigzag --help

4. Here is an example of uploading a results JUnitXML file from Molecule::

    $ export QTEST_API_TOKEN="SECRET"
    $ zigzag junit.xml 12345 TC-1

5. Checkout QA Symphony's website for more details on configuring `qTest Manager API`_ access.

Contributing
------------

See `CONTRIBUTING.rst`_ for more details on developing for the Zigzag project.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _CONTRIBUTING.rst: CONTRIBUTING.rst
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _qTest Manager API: https://support.qasymphony.com/hc/en-us/articles/115002958146-qTest-API-Specification