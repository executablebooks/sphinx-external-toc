from click.testing import CliRunner

from sphinx_external_toc.cli import main
from sphinx_external_toc import __version__

import pytest


@pytest.fixture()
def invoke_cli():
    """Run CLI and do standard checks."""

    def _func(command, args, assert_exit: bool = True):
        runner = CliRunner()
        result = runner.invoke(command, args)
        if assert_exit:
            assert result.exit_code == 0, result.output
        return result

    yield _func


def test_cli_version(invoke_cli):
    result = invoke_cli(main, "--version")
    assert __version__ in result.output
