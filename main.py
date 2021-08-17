import os
import re


from models import Owner, Class, Location, Method, Call, Callable, Argument


class AdriQLParser:
    function_call_regex = r'(\w+)\(([\w ,]+)\)'
    function_definition_regex = r'(\w+)\(([\w ,]+)\)'

    def __init__(self):
        pass

    def parse_file(self, full_path):
        with open(full_path, 'r') as file:
            content = file.read()

        # find all classes
        root_owner = Class('Root', Location(0, os.path.split(full_path)[-1], full_path))
        classes = self.find_all_classes(content, full_path)

        for parsed_class in classes:
            class_methods = self.find_class_methods(parsed_class)
            [parsed_class.add_callable(method) for method in class_methods]

        functions = self.find_all_functions(root_owner, content, full_path)
        [root_owner.add_callable(function) for function in functions]
        for parsed_function in functions:
            calls_in_function = self.find_calls_in_function(parsed_function)
            [parsed_function.add_call(_call) for _call in calls_in_function]

        return root_owner, classes

    def find_all_functions(self, root_owner, content, full_path):
        lines = content.splitlines()
        functions = []
        for line_no, line in enumerate(lines):
            if line.startswith('def '):
                matches = re.search(self.function_call_regex, line)
                function_name = matches.group(1)
                function_parameters = matches.group(2).split(',')
                current_location = Location(line_no + 1, os.path.split(full_path)[-1], full_path)
                functions.append(Method(function_name, location=current_location,
                                        parameters=function_parameters, owner=root_owner))

        return functions

    def find_calls_in_function(self, function):
        calls = []
        if not function.location:
            return calls

        with open(function.location.full_path, 'r') as file:
            content = file.read()

        lines = content.splitlines()[function.location.line:]

        for relative_line_no, line in enumerate(lines):
            if not line.startswith(' ' * 4):
                break

            line = line[4:]

            call_list = self.get_calls_in_line(line)
            for call_data in call_list:
                callee_name = call_data[0]
                call_arguments = call_data[1]
                call_kwargs = call_data[2]

                callee = Callable(callee_name, location=None, parameters=None, owner=None)

                current_location = Location(function.location.line + relative_line_no + 1, function.location.filename,
                                            function.location.full_path)

                argument_list = [Argument(name, callee) for name in call_arguments]

                call_object = Call(function, callee, current_location, argument_list, call_kwargs)

                calls.append(call_object)

                # print(f"Called {callee_name} with {call_arguments} and {call_kwargs}")

                continue

        return calls

    @staticmethod
    def find_all_classes(content, full_path):
        lines = content.splitlines()
        classes = []
        for line_no, line in enumerate(lines):
            if line.startswith('class'):
                class_name = line.split(":")[0].split(' ')[-1]
                classes.append(Class(class_name, Location(line_no + 1, os.path.split(full_path)[-1], full_path)))

        return classes

    @staticmethod
    def parse_method_signature(line, owner_class: Class, location: Location):
        # def __init__(self, arg1):
        line = line[4:]
        method_name = line.split('(')[0]
        first_parenthesis_offset = len(method_name) + 1
        parameter_list = line[first_parenthesis_offset:-2].split(', ')
        # print(method_name)
        # print(parameter_list)

        return Method(method_name, location, parameter_list, owner_class)

    def get_calls_in_line(self, line):
        matches = re.search(self.function_call_regex, line)
        callee_name = matches.group(1)
        callee_arguments = matches.group(2).split(',')
        callee_keyword_arguments = {}
        return [[callee_name, callee_arguments, callee_keyword_arguments]]

    def find_class_methods(self, parsed_class):
        if not parsed_class.location:
            return set()

        with open(parsed_class.location.full_path, 'r') as file:
            content = file.read()

        methods = set()

        lines = content.splitlines()[parsed_class.location.line:]

        in_method = False
        current_method = None

        for relative_line_no, line in enumerate(lines):
            if not line.startswith(' ' * 4):
                break

            line = line[4:]
            if line.startswith('def '):
                method = self.parse_method_signature(
                    line,
                    parsed_class,
                    Location(parsed_class.location.line + relative_line_no + 1, parsed_class.location.filename,
                             parsed_class.location.full_path))

                in_method = True
                current_method = method
                methods.add(method)
                continue

            if line.startswith(' ' * 4):
                # print('This is a method definition')
                call_list = self.get_calls_in_line(line)
                for call_data in call_list:
                    callee_name = call_data[0]
                    call_arguments = call_data[1]
                    call_kwargs = call_data[2]

                    callee = Callable(callee_name, location=None, parameters=None, owner=None)

                    current_location = Location(
                        parsed_class.location.line + relative_line_no + 1, parsed_class.location.filename,
                        parsed_class.location.full_path)

                    argument_list = [Argument(name, callee) for name in call_arguments]

                    call_object = Call(current_method or None, callee, current_location,
                                       argument_list, call_kwargs)

                    current_method.add_call(call_object)

                    # print(f"Called {callee_name} with {call_arguments} and {call_kwargs}")

                continue

            in_method = False
            current_method = None

        return methods


def run_parser():
    full_path = '/home/adri/Documents/code/adriQL/test/script.py'
    aql = AdriQLParser()
    root_class, classes = aql.parse_file(full_path)
    print(root_class)
    for _class in classes:
        print(_class)


if __name__ == '__main__':
    run_parser()
