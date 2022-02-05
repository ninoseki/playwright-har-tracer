from dataclasses import dataclass, field
from typing import Optional

import pytest

from playwright_har_tracer.dataclasses.mixin import CustomizedDataClassJsonMixin


@dataclass
class Child(CustomizedDataClassJsonMixin):
    key: Optional[str] = field(default=None)
    snake_key: Optional[str] = field(default=None)


@dataclass
class Parent(CustomizedDataClassJsonMixin):
    key: Optional[str] = field(default=None)
    snake_key: Optional[str] = field(default=None)
    child: Optional[Child] = field(default=None)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({}, {}),
        ({"child": {}}, {"child": {}}),
        ({"child": {"key": None}}, {"child": {}}),
        ({"child": {"key": "a"}}, {"child": {"key": "a"}}),
        ({"key": "a", "snake_key": None}, {"key": "a"}),
    ],
)
def test_customized_dataclass_json_mixin_to_dict(test_input: dict, expected: dict):
    parent = Parent.from_dict(test_input)
    assert parent.to_dict() == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            {"key": "a", "snake_key": "b", "child": {"key": "a", "snake_key": "b"}},
            '{"key": "a", "snakeKey": "b", "child": {"key": "a", "snakeKey": "b"}}',
        ),
    ],
)
def test_customized_dataclass_json_mixin_to_json(test_input: dict, expected: str):
    parent = Parent.from_dict(test_input)
    assert parent.to_json() == expected
