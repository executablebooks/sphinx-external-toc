import click
import yaml

from sphinx_external_toc import __version__
from sphinx_external_toc.api import parse_toc_yaml
from sphinx_external_toc.tools import create_site_from_toc


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__)
def main():
    """Command-line for ``sphinx-external-toc``."""


@main.command("parse-toc")
@click.argument("toc_file", type=click.Path(exists=True, file_okay=True))
def parse_toc(toc_file):
    """Parse a ToC file to a site-map YAML."""
    site_map = parse_toc_yaml(toc_file)
    click.echo(yaml.dump(site_map.as_json()))


@main.command("create-site")
@click.argument("toc_file", type=click.Path(exists=True, file_okay=True))
@click.option(
    "-p",
    "--path",
    default=None,
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help="The root directory [default: ToC file directory].",
)
@click.option(
    "-e",
    "--extension",
    type=click.Choice(["rst", "md"]),
    default="rst",
    show_default=True,
    help="The default file extension to use.",
)
@click.option("-o", "--overwrite", is_flag=True, help="Overwrite existing files.")
def create_site(toc_file, path, extension, overwrite):
    """Create a site from a ToC file."""
    create_site_from_toc(
        toc_file, root_path=path, default_ext="." + extension, overwrite=overwrite
    )
    # TODO option to add basic conf.py?
