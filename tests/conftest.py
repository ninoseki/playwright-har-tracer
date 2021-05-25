import pathlib

import pytest


@pytest.fixture
def test_html():
    path = pathlib.Path(__file__).parent / "./fixtures/test.html"
    with open(path) as f:
        return f.read()
