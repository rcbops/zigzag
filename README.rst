======
Zigzag
======


.. image:: https://img.shields.io/travis/rcbops/zigzag.svg
        :target: https://travis-ci.org/rcbops/zigzag


Parse JUnitXML and upload test results to qTest Manager.

Quick Start Guide
-----------------

1. Install ``zigzag`` from PyPI with pip::

    $ pip install rpc-zigzag

2. For more information on using the Zigzag launch help by::

    $ zigzag --help

3. Here is an example of uploading a results JUnitXML file from Molecule::

    $ export QTEST_API_TOKEN="SECRET"
    $ zigzag junit.xml 12345

4. Checkout QA Symphony's website for more details on configuring `qTest Manager API`_ access.

Choosing a Parent Test Cycle
----------------------------

By default, ``zigzag`` will discover the appropriate parent test cycle by inspecting the provided JUnitXML. However,
a test cycle can be specified manually by using the ``--qtest-test-cycle`` command-line option. It should be noted that
the intended parent test cycle should be named after the product release code name. (e.g. Queens)

It is assumed that this test cycle was created beforehand if you're using the ``--qtest-test-cycle`` command-line
option. By using a test cycle with a product release code name the resulting execution result hierarchy will group
results ina sensible manner.

Contributing
------------

See `CONTRIBUTING.rst`_  and `developer_docs.rst`_ for more details on developing for the Zigzag project.

Release Process
---------------

See `release_process.rst`_ for information on the release process for 'zigzag'

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _CONTRIBUTING.rst: CONTRIBUTING.rst
.. _developer_docs.rst: docs/developer_docs.rst
.. _release_process.rst: docs/release_process.rst
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _qTest Manager API: https://support.qasymphony.com/hc/en-us/articles/115002958146-qTest-API-Specification
