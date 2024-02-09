import logging
import time


class Foo:
    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        print(f"Calling Foo expensive __str__ on Foo with value {self.value}")
        time.sleep(0.25)
        return f"My value is: {self.value}"


def example_eager_formatting():
    foo = Foo(1)
    # Expensive Foo.__str__ will be called even though logging.DEBUG level is not enabled.
    logging.debug("The value of `foo` is %s" % foo)
