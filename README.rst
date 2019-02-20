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

3. Configuring Zigzag::

    The zigzag config file is defined by the json schema at: zigzag/data/schema/zigzag-config.schema.json which is generated using a jinja2 template. (See [zigzag/data/configs/zigzag-config-example.json](https://github.com/rcbops/zigzag/tree/master/zigzag/data/configs/zigzag-config-example.json) for an example)

    Any test suite property from the incoming junit.xml can be interpolated, by name, into the template. (See the example.)

    The config file must be specified at execution time.

    Because the template is rendered using jinja2, arbitrary python code can be used to inform the values. You could have a module hierarchy with one of the nodes set to the datetime of the zigzag execution, for instance.


    - project_id: (Required) The qtest project id to reference when uploading test results.
    - test_cycle:  (Required) A string name of the root node of the hierarchy for storing test results in qtest.
    - module_hierarchy: (Required) A list, of length => 0, of hierarchical nodes where test results will be stored in qtest. This config option has access to the strftime module.  A special variable is made avalable to this option 'zz_testcase_class', it will interpolate to the value of the fully qualified class name for a given test.  An example of these being used can be found in `molecule-config-example.json`_
    - path_to_test_exec_dir: A string representing an arbitrary path between the root of the project being tested and the directory where tests will be executed. This is used in failure link generation.
    - build_url: The URL of the build that generated the XML to be processed
    - build_number: The build number from the CI system

    The following configs are project specific, these values should be accurate for the version of the project under test.
    - project_repo_name: The name of the repo of the project under test
    - project_branch: The branch of the project under test
    - project_fork: The fork of the project under test
    - project_commit: The commit sha of the project under test

    The following configs are test specific, these values should be accurate for the version of the tests that generated the XML.
    If your tests are located in the same repo as your project these values will be the same as above.
    - test_repo_name: The name of the repo that containing the tests used to generate the XML
    - test_branch: The branch of the repository that contains the tests used to generate the XML
    - test_fork: The fork of the repository that contains the tests used to generate the XML
    - test_commit: The commit sha of the the repository that contains the tests used to generate the XML


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
.. _molecule-config-example.json: zigzag/data/configs/molecule-config-example.json
