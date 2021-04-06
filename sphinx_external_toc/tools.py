from itertools import chain
from pathlib import Path, PurePosixPath
from os import linesep
import shutil
from typing import Mapping, Optional, Sequence, Union

from .api import parse_toc_file, SiteMap


def create_site_from_toc(
    toc_path: Union[str, Path],
    *,
    root_path: Union[None, str, Path] = None,
    default_ext: str = ".rst",
    encoding: str = "utf8",
    overwrite: bool = False,
    toc_name: Optional[str] = "_toc.yml",
) -> SiteMap:
    """Create the files defined in the external toc file.

    Additional files can also be created by defining them in
    `meta`/`create_files` of the toc.
    Text can also be appended to files, by defining them in `meta`/`create_append`
    (ass a mapping of files -> text)

    :param toc_path: Path to ToC.
    :param root_path: The root directory , or use ToC file directory.
    :param default_ext: The default file extension to use.
    :param encoding: Encoding for writing files
    :param overwrite: Overwrite existing files (otherwise raise ``IOError``).
    :param toc_name: Copy toc file to root with this name

    """
    assert default_ext in {".rst", ".md"}
    site_map = parse_toc_file(toc_path)

    root_path = Path(toc_path).parent if root_path is None else Path(root_path)
    root_path.mkdir(parents=True, exist_ok=True)

    # retrieve and validate meta variables
    additional_files = site_map.meta.get("create_files", [])
    assert isinstance(additional_files, Sequence), "'create_files' should be a list"
    append_text = site_map.meta.get("create_append", {})
    assert isinstance(append_text, Mapping), "'create_append' should be a mapping"

    # copy toc file to root
    if toc_name and not root_path.joinpath(toc_name).exists():
        shutil.copyfile(toc_path, root_path.joinpath(toc_name))

    # create files
    for docname in chain(site_map, additional_files):

        # create document
        filename = docname
        if not any(docname.endswith(ext) for ext in {".rst", ".md"}):
            filename += default_ext
        docpath = root_path.joinpath(PurePosixPath(filename))
        if docpath.exists() and not overwrite:
            raise IOError(f"Path already exists: {docpath}")
        docpath.parent.mkdir(parents=True, exist_ok=True)

        content = []

        # add heading based on file type
        heading = f"Heading: {filename}"
        if filename.endswith(".rst"):
            content = [heading, "=" * len(heading), ""]
        elif filename.endswith(".md"):
            content = ["# " + heading, ""]

        # append extra text
        extra_lines = append_text.get(docname, "").splitlines()
        if extra_lines:
            content.extend(extra_lines + [""])

        print(linesep.join(content))
        print()

        docpath.write_text(linesep.join(content), encoding=encoding)

    return site_map
