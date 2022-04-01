"""Test ComprehensionChecker"""


def should_be_a_list_copy():
    """Using the copy() method would be more efficient."""
    original = range(10_000)
    filtered = []
    for i in original:
        filtered.append(i)


def should_be_a_list_comprehension_filtered():
    """A List comprehension would be more efficient."""
    original = range(10_000)
    filtered = []
    for i in original:
        if i % 2:
            filtered.append(i)


def should_be_a_dict_comprehension():
    pairs = (("a", 1), ("b", 2))
    result = {}
    for x, y in pairs:
        result[x] = y


def should_be_a_dict_comprehension_filtered():
    pairs = (("a", 1), ("b", 2))
    result = {}
    for x, y in pairs:
        if y % 2:
            result[x] = y


def should_not_be_a_list_comprehension(args):
    """Internal helper for get_args."""
    res = []
    for arg in args:
        if not isinstance(arg, tuple):
            res.append(arg)
        elif is_callable_type(arg[0]):
            if len(arg) == 2:
                res.append(Callable[[], arg[1]])
            elif arg[1] is Ellipsis:
                res.append(Callable[..., arg[2]])
            else:
                res.append(Callable[list(arg[1:-1]), arg[-1]])
        else:
            res.append(type(arg[0]).__getitem__(arg[0], _eval_args(arg[1:])))
    return tuple(res)
