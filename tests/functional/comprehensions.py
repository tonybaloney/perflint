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
