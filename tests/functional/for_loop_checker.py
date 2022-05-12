"""Test lists."""


def simple_list_collection():
    items = [1, 2, 3]
    # list is already iterable
    for i in list(items):
        print(i)


def simple_static_tuple():
    """Test warning for casting a tuple to a list."""
    items = (1, 2, 3)
    # tuple is already iterable
    for i in list(items):
        print(i)


def simple_static_set():
    """Test warning for casting a set to a list."""
    items = {1, 2, 3}
    for i in list(items):  # [unnecessary-list-cast]
        print(i)


def simple_dict_keys():
    """Check that dictionary .items() is being used correctly."""
    fruit = {
        "a": "Apple",
        "b": "Banana",
    }

    for _, value in fruit.items():  # [incorrect-dictionary-iterator]
        print(value)

    for key, _ in fruit.items():  # [incorrect-dictionary-iterator]
        print(key)
