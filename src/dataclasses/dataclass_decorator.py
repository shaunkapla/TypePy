from dataclasses import fields
from types import UnionType
from typing import (
    get_type_hints,
    get_args,
    get_origin
)

def dataclass_type_check(cls):
    """
    This will be the decorator that you will be importing into your module to enforce
    type checks for python dataclasses

    Example:
    -------
    from dataclasses import dataclass

    @dataclass
    @dataclass_type_check
    class YourClass:
        ...
    """
    