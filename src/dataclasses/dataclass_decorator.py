from dataclasses import fields
from typing import (
    get_type_hints,
    get_args,
    get_origin,
    Union,
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
    original_init = cls.__init__

    def _check_types(real, theory):
            origin = get_origin(theory)
            if origin:
                if origin is list:
                    if not isinstance(real, list):
                        return False
                    types_in_list = get_args(theory)[0]
                    return all(_check_types(types, types_in_list) for types in real)
                elif origin is dict:
                    if not isinstance(real, dict):
                        return False
                    key_t, val_t = get_args(theory)
                    return all(isinstance(key, key_t) and _check_types(val, val_t) for key, val in real.items())
                elif origin is Union:
                    return any(_check_types(real, arg_type) for arg_type in get_args(theory))
            else:
                return isinstance(real, theory)
            return False
    
    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        mismatches = []
        type_hints = get_type_hints(cls)
        for field in fields(self):
            field_name = field.name
            expected = type_hints.get(field_name)
            actual = getattr(self, field_name)
            if expected and not _check_types(actual, expected):
                mismatches.append(f"Parameter '{field_name}': expected {expected}, got something different")
        
        if mismatches:
            mismatched_fields_str = "\n\t".join(mismatches)
            raise TypeError(f"The following parameters have type mismatches:\n\t{mismatched_fields_str}\n")
            
    cls.__post_init__ = __init__
    return cls