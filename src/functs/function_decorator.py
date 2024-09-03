from functools import wraps
from inspect import signature
from typing import (
    get_args,
    get_origin,
    List,
    Union,
    Dict
)

def function_type_checker(func):
    """
    Function that will be used as a decorator to wrap the function to check that the input
    parameters are the proper type based on the developers type hint. If no type hints,
    this decorator should still "in theory" work by letting anything go

    Example usage:
    --------------

    import function_type_checker

    @function_type_checker
    def your_function_name(x: int, y: int)
        ...

    your_function_name(x="hello", y=5)
        will return a TypeError("your_function_name was expecting an int type for x, instead got str type hello")

    your_function_name(x=1, y=2)
        will work properly
    """
    hints = func.__annotations__

    @wraps(func)
    def checker(*args, **kwargs):
        sig = signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

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
        
        errs = []

        for name, val in bound_args.arguments.items():
            if name in hints:
                theory = hints[name]
                if not _check_types(val, theory):
                    errs.append(f"--> For function {func.__name__}(), the needed type for {name} should have been of type {theory} but you inputted {val} which is not of that type or has elements of an incorrect type")

        if errs:
            raise TypeError("You have one or more parameters in this function that don't match what is expected:\n\t"+"\n\t".join(errs))
        
        return func(*args, **kwargs)
    return checker
