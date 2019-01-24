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
@click.option('--test-runner', '-tr',
              type=click.Choice(['pytest-zigzag', 'tempest']),
              default='pytest-zigzag',
              help='Specify the tool that generated the xml to be processed')
@click.argument('zigzag_config_file', type=click.Path(exists=True))
@click.argument('junit_input_file', type=click.Path(exists=True))
def main(junit_input_file, zigzag_config_file, pprint_on_fail, test_runner):
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
                    zigzag_config_file,
                    os.environ[api_token_env_var],
                    pprint_on_fail)
        zz.test_runner = test_runner
        zz.parse()
        zz.load_config()

        job_id = zz.upload_test_results()

        click.echo(click.style("\nQueue Job ID: {}".format(str(job_id))))
        click.echo(click.style("\nSuccess!", fg='green'))
    except RuntimeError as e:
        click.echo(click.style(str(e), fg='red'))
        click.echo(click.style("\nFailed!", fg='red'))

        sys.exit(1)


if __name__ == "__main__":
    main()  # pragma: no cover
