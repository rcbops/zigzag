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

3. Configuring Zigzag::

    The zigzag config file is defined by the json schema at: zigzag/data/schema/zigzag-config.schema.json which is generated using a jinja2 template. (See [zigzag/data/configs/zigzag-config-example.json](https://github.com/rcbops/zigzag/tree/master/zigzag/data/configs/zigzag-config-example.json) for an example)

    Any test suite property from the incoming junit.xml can be interpolated, by name, into the template. (See the example.)

    The config file must be specified at execution time.

    Because the template is rendered using jinja2, arbitrary python code can be used to inform the values. You could have a module hierarchy with one of the nodes set to the datetime of the zigzag execution, for instance.

    Presently there are three required config properties
    - project_id: The qtest project id to reference when uploading test results.
    - test_cycle:  A string name of the root node of the hierarchy for storing test results in qtest.
    - module_hierarchy: A list, of length => 0, of hierarchical nodes where test results will be stored in qtest.
    - path_to_test_exec_dir: A string representing an arbitrary path between the root of the project being tested and the directory where tests will be executed. This is used in failure link generation.

4. Here is an example of uploading a results JUnitXML file from Molecule::

    $ export QTEST_API_TOKEN="SECRET"
    $ zigzag /path/to/config.json /path/to/junit.xml

5. Checkout QA Symphony's website for more details on configuring `qTest Manager API`_ access.

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
