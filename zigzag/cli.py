# -*- coding: utf-8 -*-

"""Console script for zigzag."""
# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import os
import sys
import click
from zigzag.zigzag import ZigZag


# ======================================================================================================================
# Main
# ======================================================================================================================
@click.command()
@click.option('--pprint-on-fail', '-p',
              is_flag=True,
              default=False,
              help='Pretty print XML on schema violations to stdout')
@click.option('--qtest-test-cycle', '-t',
              type=click.STRING,
              default=None,
              help='Specify a test cycle to use as a parent for results.')
@click.argument('junit_input_file', type=click.Path(exists=True))
@click.argument('qtest_project_id', type=click.INT)
def main(junit_input_file, qtest_project_id, qtest_test_cycle, pprint_on_fail):
    """Upload JUnitXML results to qTest manager.

    \b
    Required Arguments:
        JUNIT_INPUT_FILE        A valid JUnit XML results file.
        QTEST_PROJECT_ID        The the target qTest Project ID for results
    \b
    Required Environment Variables:
        QTEST_API_TOKEN         The qTest API token to use for authorization
    """

    api_token_env_var = 'QTEST_API_TOKEN'

    try:
        if not os.environ.get(api_token_env_var):
            raise RuntimeError('The "{}" environment variable is not defined! '
                               'See help for more details.'.format(api_token_env_var))

        zz = ZigZag(junit_input_file,
                    os.environ[api_token_env_var],
                    qtest_project_id,
                    qtest_test_cycle,
                    pprint_on_fail)

        zz.parse()
        job_id = zz.upload_test_results()
        click.echo(click.style("\nQueue Job ID: {}".format(str(job_id))))
        click.echo(click.style("\nSuccess!", fg='green'))
    except RuntimeError as e:
        click.echo(click.style(str(e), fg='red'))
        click.echo(click.style("\nFailed!", fg='red'))

        sys.exit(1)


if __name__ == "__main__":
    main()  # pragma: no cover
