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
        print(len(x) * i + j) # [loop-invariant-statement]


def loop_invariant_statement_method_side_effect():
    """Catch basic loop-invariant function call."""
    x = [1,2,3,4] 
    i = 6

    for j in range(10_000):
        print(len(x) * i + j)
        x.clear()  # x changes as a side-effect


def loop_invariant_branching():
    """Ensure node is walked up to find a loop-invariant branch"""
    x = [1,2,3,4] 
    i = 6

    for j in range(10_000):
        # Marks entire branch
        if len(x) > 2:    # [loop-invariant-statement]
            print(x * i)  # [loop-invariant-statement]

    # Marks comparator, but not print
    for j in range(10_000):
        if len(x) > 2:   # [loop-invariant-statement]
            print(x * j) # [loop-invariant-statement]



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

def loop_invariant_statement_but_name():
    """Catch basic loop-invariant function call."""
    i = 6

    for _ in range(10_000):
        i


def loop_invariant_statement_while():
    """Catch basic loop-invariant function call."""
    x = (1,2,3,4)
    i = 0
    while i < 100:
        i += 1
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) * i)


def loop_invariant_statement_more_complex_while():
    """Catch basic loop-invariant function call."""
    x = [1,2,3,4]
    i = 6
    j = 0
    while j < 100:
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) * i + j) # [loop-invariant-statement]


def loop_invariant_statement_method_side_effect_while():
    """Catch basic loop-invariant function call."""
    x = [1,2,3,4] 
    i = 6
    j = 0
    while j < 10_000:
        j += 1
        print(len(x) * i + j)
        x.clear()  # x changes as a side-effect


def loop_invariant_branching_while():
    """Ensure node is walked up to find a loop-invariant branch"""
    x = [1,2,3,4] 
    i = 6
    j = 0
    while j < 10_000:
        j += 1
        # Marks entire branch
        if len(x) > 2:    # [loop-invariant-statement]
            print(x * i)  # [loop-invariant-statement]

    # Marks comparator, but not print
    j = 0
    while j < 10_000:
        j += 1
        if len(x) > 2:   # [loop-invariant-statement]
            print(x * j) # [loop-invariant-statement]



def loop_invariant_statement_side_effect_function_while():
    """Catch basic loop-invariant function call."""
    x = [1,2,3,4]
    i = 6
    _len = len

    def len(x): # now with side effects!
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
