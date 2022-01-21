def loop_invariant_statement():
    """Catch basic loop-invariant function call."""
    x = (1,2,3,4)

    for i in range(10_000):
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) * i)


def loop_invariant_statement_more_complex():
    """Catch basic loop-invariant function call."""
    x = [1,2,3,4]
    i = 6

    for j in range(10_000):
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) * i + j)


def loop_invariant_statement_method_side_effect():
    """Catch basic loop-invariant function call."""
    x = [1,2,3,4]
    i = 6

    for j in range(10_000):
        print(len(x) * i + j)
        x.clear()  # x changes as a side-effect
 

def loop_invariant_statement_side_effect_function():
    """Catch basic loop-invariant function call."""
    x = [1,2,3,4]
    i = 6
    _len = len

    def len(x): # now with side effects!
        x.clear()
        return 0

    for j in range(10_000):
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) + j)

    len = _len

