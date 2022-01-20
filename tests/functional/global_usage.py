MY_GLOBAL_CONSTANT_C = 1234
MY_GLOBAL_CONSTANT_A = 3.14


def global_constant_in_loop():
    """Do a quick sum."""

    total = MY_GLOBAL_CONSTANT_A
    for i in range(10_000):
        total += i * MY_GLOBAL_CONSTANT_C # [loop-invariant-global-usage]
