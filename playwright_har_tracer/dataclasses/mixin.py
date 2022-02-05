from dataclasses_json import LetterCase, Undefined
from dataclasses_json.api import DataClassJsonMixin
from dataclasses_json.cfg import config


class CustomizedDataClassJsonMixin(DataClassJsonMixin):
    dataclass_json_config = config(
        letter_case=LetterCase.CAMEL,
        undefined=Undefined.EXCLUDE,
        exclude=lambda f: f is None,
    )["dataclasses_json"]
