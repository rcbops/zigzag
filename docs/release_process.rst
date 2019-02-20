==========================
Production Release Process
==========================

The workflow below is targeted at releasing production ready code to `PyPI`_.
This workflow assumes that the current branch is up-to-date with desired changes
and the code is validated to work for end users who are working with this
project in production.

1. First you will need to know the username and password for the account you
   want to use to release to PyPI shared_accounts_.

2. You will need to make sure that you are on the master branch, your working
   directory is clean and up to date.

3. Decide if you are going to increment the major, minor, or patch version.
   You can refer to semver_ to help you make that decision.

4. Use the `release-major`, `release-minor`, or `release-patch`. ::

    make release-minor

5. The task will stop and prompt you for you `PyPI`_ username and password if
   you dont have these set in your `.pypirc` file.

6. Once the task has successfully completed you need to push the tag and
   commit. ::

    git push origin && git push origin refs/tags/<tagname>

7. Create a release on GitHub. (`GitHub release`_)

=================================
Development Build Release Process
=================================

The workflow below is targeted at releasing 'dev' builds to `PyPI`_.
The purpose of this workflow is to put experimental or release candidate builds
onto `PyPI`_ in order to test other projects that are dependent on this one.

1. First you will need to know the username and password for the account you
   want to use to release to PyPI shared_accounts_.

2. You will need to make sure that you are on your working directory is clean
   and up to date and you're on the correct branch that contains the
   experimental/non-production code.

3. Decide if you are going to increment the major, minor, or patch version.
   You can refer to semver_ to help you make that decision.

4. Use the `bump-major`, `bump-minor`, `bump-patch` or `bump-build` to move the
   version forward. ::

    make bump-minor

5. Build the experimental/non-production package. ::

    make build

6. Publish the experimental/non-production package to `PyPI`_. ::

    make publish

7. If you need to make updates to the experimental build it is suggested to
   bump the build version, build and re-publish. ::

    make bump-build
    make build
    make publish

8. Once you're satisfied that the changes are ready to be released to production
   use the `make release` target. ::

    make release

9. Once the task has successfully completed you need to push the tag and
   commit. ::

    git push origin && git push origin refs/tags/<tagname>

10. Create a release on GitHub. (`GitHub release`_)

.. _semver: https://semver.org
.. _shared_accounts: https://rpc-openstack.atlassian.net/wiki/spaces/ASC/pages/143949893/Useful+Links#UsefulLinks-SharedAccounts
.. _GitHub release: https://help.github.com/articles/creating-releases/
.. _`PyPI`: https://pypi.python.org/pypi