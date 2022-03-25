def should_be_a_list_copy():
    original = range(10_000)
    filtered = []
    for i in original:
        filtered.append(i)


def should_be_a_list_comprehension_filtered():
    original = range(10_000)
    filtered = []
    for i in original:
        if i % 2:
            filtered.append(i)
