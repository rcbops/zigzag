===============
Release Process
===============

The easiest way to release a new version of zigzag is to use make.

1. First you will need to know the username and password for the account you want to use to release to PyPI by referring to the ASC `shared accounts`_ page.

2. You will need to make sure that you are on the master branch, your working directory is clean and up to date.

3. Decide if you are going to increment the major, minor, or patch version.  You can refer to semver_ to help you make that decision.

4. Verify that the pre-requisites for running `integration tests`_ are satisfied. (See the "Executing Integration Tests" section)

5. Use the `release-major`, `release-minor`, or `release-patch`.

    **make release** ::

        make release-minor

6. The task will stop and prompt you for you PyPI username and password if you don't have these set in your `.pypirc` file.

7. Once the task has successfully completed you need to push the tag and commit.

    **push tag** ::

        git push origin && git push origin refs/tags/<tagname>

8. Create a `GitHub release`_.

.. _integration tests: integration_testing.rst
.. _semver: https://semver.org
.. _shared accounts: https://rpc-openstack.atlassian.net/wiki/spaces/ASC/pages/143949893/Useful+Links#UsefulLinks-SharedAccounts
.. _GitHub release: https://help.github.com/articles/creating-releases/
