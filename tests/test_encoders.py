import pytest

from playwright_har_tracer.dataclasses.har import reject_none_encoder


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({"foo": "bar", "bar": None}, {"foo": "bar"}),
        ({"foo": {"bar": None, "foo": [{"bar": None}]}}, {"foo": {"foo": [{}]}}),
    ],
)
def test_reject_none_encoder(test_input: dict, expected: dict):
    assert reject_none_encoder(test_input) == expected
