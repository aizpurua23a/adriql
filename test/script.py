

class MyClass:
    def __init__(self, arg1):
        print(arg1)


class AnotherClass:
    def __init__(self, arg1):
        print(arg1)

    def my_method(self, my_arg):
        print(my_arg)


def attack(password):
    print(password)


def attack2(password):
    print(password)


if __name__ == "__main__":
    attack("mypass")
