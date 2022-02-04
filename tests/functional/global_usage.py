MY_GLOBAL_CONSTANT_C = 1234
MY_GLOBAL_CONSTANT_A = 3.14
MY_GLOBAL_VARIABLE = 1234

def global_constant_in_loop():
    """Do a quick sum."""

    total = MY_GLOBAL_CONSTANT_A
    for i in range(10_000):
        total += i * MY_GLOBAL_CONSTANT_C # [loop-invariant-global-usage]


def global_variable_in_loop():
    """Use the module global as a global."""
    global MY_GLOBAL_VARIABLE # [global-statement]

    total = MY_GLOBAL_CONSTANT_A
    for i in range(10_000):
        MY_GLOBAL_VARIABLE += total
        total += i

def recursive_example(x):
    for i in range(100):
        recursive_example(i)

    for i in range(100):
        global_constant_in_loop()
