import os
from pathlib import Path
from typing import List

import pytest
from click.testing import CliRunner

from sphinx_external_toc import __version__
from sphinx_external_toc.cli import create_toc, main, migrate_toc, parse_toc


@pytest.fixture()
def invoke_cli():
    """Run CLI and do standard checks."""

    def _func(command, args: List[str], assert_exit: bool = True):
        runner = CliRunner()
        result = runner.invoke(command, args)
        if assert_exit:
            assert result.exit_code == 0, result.output
        return result

    yield _func


def test_version(invoke_cli):
    result = invoke_cli(main, ["--version"])
    assert __version__ in result.output


def test_parse_toc(invoke_cli):
    path = os.path.abspath(Path(__file__).parent.joinpath("_toc_files", "basic.yml"))
    result = invoke_cli(parse_toc, [path])
    assert "intro" in result.output


def test_create_toc(tmp_path, invoke_cli, file_regression):
    # create site files
    files = [
        "index.rst",
        "1_a_title.rst",
        "11_another_title.rst",
        ".hidden_file.rst",
        ".hidden_folder/index.rst",
        "1_a_subfolder/index.rst",
        "2_another_subfolder/index.rst",
        "2_another_subfolder/other.rst",
        "3_subfolder/1_no_index.rst",
        "3_subfolder/2_no_index.rst",
        "14_subfolder/index.rst",
        "14_subfolder/subsubfolder/index.rst",
        "14_subfolder/subsubfolder/other.rst",
    ]
    for posix in files:
        path = tmp_path.joinpath(*posix.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    result = invoke_cli(create_toc, [os.path.abspath(tmp_path), "-t"])
    file_regression.check(result.output.rstrip())


def test_migrate_toc(invoke_cli):
    path = os.path.abspath(
        Path(__file__).parent.joinpath("_jb_migrate_toc_files", "simple_list.yml")
    )
    result = invoke_cli(migrate_toc, [path])
    assert "root: index" in result.output
