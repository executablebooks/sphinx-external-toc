import os
from pathlib import Path

from click.testing import CliRunner

from sphinx_external_toc.cli import main, parse_toc
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


def test_version(invoke_cli):
    result = invoke_cli(main, "--version")
    assert __version__ in result.output


def test_parse_toc(invoke_cli):
    path = os.path.abspath(Path(__file__).parent.joinpath("_toc_files", "basic.yml"))
    result = invoke_cli(parse_toc, path)
    assert "intro" in result.output
