from pathlib import Path, PurePosixPath
from os import linesep
from typing import Union

from .api import parse_toc_file


def create_site_from_toc(
    toc_path: Union[str, Path],
    *,
    root_path: Union[None, str, Path] = None,
    default_ext: str = ".rst",
    encoding: str = "utf8",
    overwrite: bool = False,
) -> Path:
    """Create the files defined in the external toc file.

    :param toc_path: Path to ToC.
    :param root_path: The root directory , or use ToC file directory.
    :param default_ext: The default file extension to use.
    :param encoding: Encoding for writing files
    :param overwrite: Overwrite existing files (otherwise raise ``IOError``).

    :returns: Root path.
    """
    assert default_ext in {".rst", ".md"}
    site_map = parse_toc_file(toc_path)

    root_path = Path(toc_path).parent if root_path is None else Path(root_path)

    for docname in site_map:
        if not any(docname.endswith(ext) for ext in {".rst", ".md"}):
            docname += default_ext
        docpath = root_path.joinpath(PurePosixPath(docname))
        if docpath.exists() and not overwrite:
            raise IOError(f"Path already exists: {docpath}")
        docpath.parent.mkdir(parents=True, exist_ok=True)
        heading = f"Heading: {docname}"
        content = []
        if docname.endswith(".rst"):
            content = [heading, "=" * len(heading), ""]
        elif docname.endswith(".md"):
            content = ["# " + heading, ""]
        docpath.write_text(linesep.join(content), encoding=encoding)

    return root_path
