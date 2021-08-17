from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Location:
    line: int
    filename: str
    full_path: str


class Parameter:
    def __init__(self, parameter_name, method, parameter_type=None, has_default=False, default_value=None):
        self.method = method
        self.name = parameter_name
        self.type = parameter_type
        self.has_default = has_default
        self.default_value = default_value


class Owner:
    def __init__(self, name, location: Location, parents=None, metaclass=None):
        if parents is None:
            parents = []

        self.name = name
        self.location = location
        self.parents = parents
        self.metaclass = metaclass
        self.callables = set()
        self.members = set()

    def __repr__(self):
        callables_print = []
        for _callable in self.callables:
            callable_string = f" |--{_callable.name} ({_callable.location.filename}:{_callable.location.line}): " \
                           f"params {_callable.parameters}"
            calls_string = [f"     |--call to {_call.callee.name} ({_call.location.filename}:{_call.location.line}): "\
                            f"args {_call.arguments}, {_call.keyword_arguments}" for _call in _callable.calls]

            callables_print.append(callable_string)
            callables_print.extend(calls_string)

        return f"Class {self.name} ({self.location.filename}:{self.location.line}):" + '\n' + '\n'.join(callables_print)


class Callable:
    def __init__(self, name, location: Location, parameters: List[Parameter] = None, owner: Owner = None):
        self.name = name
        self.location = location
        self.parameters = parameters
        self.owner = owner

    def __repr__(self):
        return f"(Callable {self.name} at {self.location.filename if self.location else '<builtin>'}:" \
               f"{self.location.line if self.location else '<builtin>'})"


class Argument:
    def __init__(self, argument_name, callable: Callable):
        self.callable = callable
        self.name = argument_name

    def __repr__(self):
        return str(self.name)


class Call:
    def __init__(self, caller: Callable, callee: Callable, location: Location,
                 arguments: List[Argument] = None, keyword_arguments: Dict[str, Argument] = None):
        if arguments is None:
            arguments = []

        if keyword_arguments is None:
            keyword_arguments = {}

        self.callee = callee
        self.caller = caller
        self.location = location
        self.arguments = arguments
        self.keyword_arguments = keyword_arguments

    def __repr__(self):
        return f"Call of Callable {self.callee} with arguments {self.arguments} and keyword arguments {self.keyword_arguments} at {self.location.filename}:{self.location.line}"


class Method(Callable):
    def __init__(self, name, location: Location, parameters: list = None, owner: Owner = None):
        if parameters is None:
            parameters = list()
        super().__init__(name, location, parameters, owner)
        self.calls = []

    def add_call(self, new_call: Call):
        self.calls.append(new_call)

    def __repr__(self):
        return f"Method {self.name} at {self.location.filename}:{self.location.line} has calls {self.calls}"


class Class(Owner):
    def __init__(self, name, location: Location, parents=None, metaclass=None):
        super().__init__(name, location, parents, metaclass)
        self.name = name
        self.location = location
        self.parents = parents
        self.metaclass = metaclass
        self.callables = set()
        self.members = set()

    def add_callable(self, method: Method):
        self.callables.add(method)
