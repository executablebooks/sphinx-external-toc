import re

import pytest

pytest_plugins = "sphinx.testing.fixtures"


# comparison files will need updating
# alternatively the resolution of https://github.com/ESSS/pytest-regressions/issues/32
@pytest.fixture()
def file_regression(file_regression):
    return FileRegression(file_regression)


class FileRegression:
    ignores = (
        # TODO: Remove when support for Sphinx<=6 is dropped,
        re.escape(" translation_progress=\"{'total': 0, 'translated': 0}\""),
        # TODO: Remove when support for Sphinx<7.2 is dropped,
        r"original_uri=\"[^\"]*\"\s",
    )

    def __init__(self, file_regression):
        self.file_regression = file_regression

    def check(self, data, **kwargs):
        return self.file_regression.check(self._strip_ignores(data), **kwargs)

    def _strip_ignores(self, data):
        for ig in self.ignores:
            data = re.sub(ig, "", data)
        return data
