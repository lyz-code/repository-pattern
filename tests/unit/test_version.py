"""Test the version_info function."""

import re

from repository_pattern.version import __version__, version_info


def test_version() -> None:
    """Prints program version."""
    result = version_info()  # act

    assert re.match(
        fr" *repository_pattern version: {__version__}\n"
        r" *python version: .*\n *platform: .*",
        result,
    )
