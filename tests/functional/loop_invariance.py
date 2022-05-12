""" Test loop invariance """
import os


def cook(item):
    ...


def cook_pies():
    pies = ("🥧", "🥧", "🥧", "🥧", "🥧", "🥧", "🥧")

    for i, pie in enumerate(pies):
        print("Cooking", i, "of", len(pies))
        cook(pie)


def foo(x):
    pass


def loop_invariant_statement():
    """Catch basic loop-invariant function call."""
    x = (1, 2, 3, 4)

    for i in range(10_000):
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) * i)


def loop_invariant_statement_more_complex():
    """Catch basic loop-invariant function call."""
    x = (1, 2, 3, 4)
    i = 6

    for j in range(10_000):
        # x and i are never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) * i + j)


def loop_invariant_statement_method_side_effect():
    """Catch basic loop-invariant function call."""
    x = [1, 2, 3, 4]
    i = 6

    for j in range(10_000):
        print(len(x) * i + j)
        x.clear()  # x changes as a side-effect


def loop_invariant_branching():
    """Ensure node is walked up to find a loop-invariant branch"""
    x = [1, 2, 3, 4]
    i = 6

    for j in range(10_000):
        # Marks entire branch
        if len(x) > 2:
            print(x * i)

    # Marks comparator, but not print
    for j in range(10_000):
        if len(x) > 2:
            print(x * j)


def loop_invariant_statement_side_effect_function():
    """Catch basic loop-invariant function call."""
    x = [1, 2, 3, 4]
    i = 6
    _len = len

    def len(x):  # now with side effects!
        x.clear()
        return 0

    for j in range(10_000):
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) + j)

    len = _len


def loop_invariant_statement_but_name():
    """Catch basic loop-invariant function call."""
    i = 6

    for _ in range(10_000):
        i


def loop_invariant_statement_while():
    """Catch basic loop-invariant function call."""
    x = (1, 2, 3, 4)
    i = 0
    while i < 100:
        i += 1
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) * i)
        y = x[0] + x[1]
        foo(x=y)


def loop_invariant_statement_more_complex_while():
    """Catch basic loop-invariant function call."""
    x = [1, 2, 3, 4]
    i = 6
    j = 0
    while j < 100:
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) * i + j)


def loop_invariant_statement_method_side_effect_while():
    """Catch basic loop-invariant function call."""
    x = [1, 2, 3, 4]
    i = 6
    j = 0
    while j < 10_000:
        j += 1
        print(len(x) * i + j)
        x.clear()  # x changes as a side-effect


def loop_invariant_branching_while():
    """Ensure node is walked up to find a loop-invariant branch"""
    x = [1, 2, 3, 4]
    i = 6
    j = 0
    while j < 10_000:
        j += 1
        # Marks entire branch
        if len(x) > 2:
            print(x * i)

    # Marks comparator, but not print
    j = 0
    while j < 10_000:
        j += 1
        if len(x) > 2:
            print(x * j)


def loop_invariant_statement_side_effect_function_while():
    """Catch basic loop-invariant function call."""
    x = [1, 2, 3, 4]
    i = 6
    _len = len

    def len(x):  # now with side effects!
        x.clear()
        return 0

    j = 0
    while j < 10_000:
        j += 1
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) + j)

    len = _len


def loop_invariant_statement_but_name_while():
    """Catch basic loop-invariant function call."""
    i = 6

    for _ in range(10_000):
        i


def test_dotted_import(items):
    for item in items:
        val = os.environ[item]


def even_worse_dotted_import(items):
    for item in items:
        val = os.path.exists(item)


def loop_invariance_in_self_assignment():
    class Foo:
        n = 1

        def loop(self):
            i = 4
            for self.n in range(4):
                print(self.n)
                len(i)

    def test():  # @
        f = Foo()
        f.loop()

    test()


def invariant_fstrings():
    i = 1
    for n in range(2):
        print(f"{i}")
        print(f"{n}")
        print(f"{i} + {n}")
        print(f"{n} + {i}")


def invariant_literals():
    i = 1
    for n in range(2):
        d = {"x": i}
        d2 = {"x": i, "j": n}
        d3 = {"j": n}

    for n in range(2):
        print("x" * n)

    for n in range(2):
        print("x" * i)


def invariant_iteration_sub():  # @
    items = (1, 2, 3, 4)

    for _ in items:
        x = print("There are ", len(items), "items")


def invariant_consts():
    for _ in range(4):
        len("BANANANANANAN")
        len((1, 2, 3, 4))
        max((1, 2, 3, 4))
        type(None)


def invariant_slices():  # @
    l = (1, 2, 3, 4)
    for n in range(1):
        _ = l[1:2]
        _ = l[n:3]
        _ = l[1]


def variant_slices():  # @
    fruits = ["apple", "banana", "pear"]
    for fruit in fruits:
        print(fruit)
        _ = fruit[1:]
        _ = fruit[-1]
        _ = fruit[::-1]


def constant_expressions():
    for i in range(10):
        _ = (0, 1, 2)
        _ = [0, 1, 2]
        _ = {"a": 1, "b": 2}


def variant_f_string():
    x = 1

    for n in range(10):
        result = len(f"I'm not sure about {x} {n}")


def invariant_f_string():
    x = 1

    for _ in range(10):
        result = len(f"I'm not sure about {x}")
