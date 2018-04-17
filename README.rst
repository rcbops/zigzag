======
Zigzag
======


.. image:: https://img.shields.io/travis/rcbops/zigzag.svg
        :target: https://travis-ci.org/rcbops/zigzag


Parse JUnitXML and upload test results to qTest Manager.

Quick Start Guide
-----------------

1. Install ``zigzag`` from PyPI with pip::

    $ pip install -e git+git://github.com/ryan-rs/qtest-swagger-client.git@master#egg=swagger-client-1.0.0
    $ pip install rpc-zigzag

2. For more information on using the Zigzag launch help by::

    $ zigzag --help

3. Here is an example of uploading a results JUnitXML file from Molecule::

    $ export QTEST_API_TOKEN="SECRET"
    $ zigzag junit.xml 12345 TC-1

4. Checkout QA Symphony's website for more details on configuring `qTest Manager API`_ access.

Choosing a Parent Test Cycle
----------------------------

The intended parent test cycle should be one that is named after the product release code name. (e.g. Queens) It is
assumed that this test cycle was created beforehand. By using a test cycle with a product release code name the
resulting execution result hierarchy will group results in a sensible manner.

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