from playwright_har_tracer import __version__


def test_version():
    assert isinstance(__version__, str)
