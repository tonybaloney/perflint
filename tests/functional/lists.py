def mutated_list():
    fruit = ["banana", "pear", "orange"]
    fruit.clear()


def non_mutated_list():
    fruit = ["banana", "pear", "orange"]  # [use-tuple-over-list]
    len(fruit)
    for i in fruit:
        print(i)


def index_mutated_list():
    fruit = ["banana", "pear", "orange"]
    fruit[2] = "mandarin"
    len(fruit)
    for i in fruit:
        print(i)


def index_non_mutated_list():
    fruit = ["banana", "pear", "orange"]  # [use-tuple-over-list]
    print(fruit[2])
    len(fruit)
    for i in fruit:
        print(i)


def slice_mutated_list():
    fruit = ["banana", "pear", "orange"]
    fruit[0:1] = ("grapes", "plum")
    len(fruit)
    for i in fruit:
        print(i)
