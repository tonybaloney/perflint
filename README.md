# perflint
![PyPI](https://img.shields.io/pypi/v/perflint)

pylint extension for performance anti patterns

very much a work-in-progress!

## Installation

```
pip install perflint
```

## Usage

```
pylint your_code/ --load-plugins=perflint
```

## Rules

### W8101 : Unnessecary `list()` on already iterable type

Using a `list()` call to eagerly iterate over an already iterable type is inefficient as a second list iterator is created, after first iterating the value:

```python
def simple_static_tuple():
    """Test warning for casting a tuple to a list."""
    items = (1, 2, 3)
    for i in list(items): # [unnecessary-list-cast]
        print(i)
```

### W8102: Incorrect iterator method for dictionary

Python dictionaries store keys and values in two separate tables. They can be individually iterated. Using `.items()` and discarding either the key or the value using `_` is inefficient, when `.keys()` or `.values()` can be used instead:

```python
def simple_dict_keys():
    """Check that dictionary .items() is being used correctly. """
    fruit = {
        'a': 'Apple',
        'b': 'Banana',
    }

    for _, value in fruit.items(): # [incorrect-dictionary-iterator]
        print(value)

    for key, _ in fruit.items(): # [incorrect-dictionary-iterator]
        print(key)
```

### W8201: Loop invariant statement (`loop-invariant-statement`)

The body of loops will be inspected to determine statements, or expressions where the result is constant (invariant) for each iteration of a loop. This is based on named variables which are not modified during each iteration. 

For example:

```python
def loop_invariant_statement():
    """Catch basic loop-invariant function call."""
    x = (1,2,3,4)

    for i in range(10_000):
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) * i)  # [loop-invariant-statement]
        #     ^^^^^^ 
```

`len(x)` should be evaluated outside the loop since `x` is not modified within the loop.

```python
def loop_invariant_statement():
    """Catch basic loop-invariant function call."""
    x = (1,2,3,4)
    n = len(x)
    for i in range(10_000):
        print(n * i)  # [loop-invariant-statement]
```


The loop-invariance checker will underline expressions and subexpressions within the body using the same rules:

```python
def loop_invariant_statement_more_complex():
    """Catch basic loop-invariant function call."""
    x = [1,2,3,4]
    i = 6

    for j in range(10_000):
        # x is never changed in this loop scope,
        # so this expression should be evaluated outside
        print(len(x) * i + j)
#             ^^^^^^^^^^    [loop-invariant-statement]
```

Methods are blindly considered side-effects, so if a method is called on a variable, it is assumed to have possibly changed in value and therefore not loop-invariant:

```python
def loop_invariant_statement_method_side_effect():
    """Catch basic loop-invariant function call."""
    x = [1,2,3,4] 
    i = 6

    for j in range(10_000):
        print(len(x) * i + j)
        x.clear()  # x changes as a side-effect
```

The loop-invariant analysis will walk up the AST until it gets to the whole loop body, so an entire branch could be marked.
For example, the expression `len(x) > 2` is invariant and therefore should be outside the loop. Also, because `x * i` is invariant, that statement should also be outside the loop, therefore the entire branch will be marked:

```python
def loop_invariant_branching():
    """Ensure node is walked up to find a loop-invariant branch"""
    x = [1,2,3,4]
    i = 6

    for j in range(10_000):
        # Marks entire branch
        if len(x) > 2:
            print(x * i)
```

#### Notes on loop invariance

Functions can have side-effects (print is a good example), so the loop-invariant scanner may give some false-positives.

It will also highlight dotted expresions, e.g. attribute lookups. This may seem noisy, but in some cases this is valid, e.g. 

```python
from os.path import exists
import os

def dotted_import():
    for _ in range(100_000):
        return os.path.exists('/')

def direct_import():
    for _ in range(100_000):
        return exists('/')
```

`direct_import()` is 10-15% faster than `dotted_import()` because it doesn't need to load the `os` global, the `path` attribute and the `exists` method for each iteration.

### W8202: Global name usage in a loop (`loop-invariant-global-usage`)

Loading globals is slower than loading "fast" local variables. The difference is marginal, but when propagated in a loop, there can be a noticable speed improvement, e.g.:

```python
d = {
    "x": 1234,
    "y": 5678,
}

def dont_copy_dict_key_to_fast():
    for _ in range(100000):
        d["x"] + d["y"]
        d["x"] + d["y"]
        d["x"] + d["y"]
        d["x"] + d["y"]
        d["x"] + d["y"]

def copy_dict_key_to_fast():
    i = d["x"]
    j = d["y"]

    for _ in range(100000):
        i + j
        i + j
        i + j
        i + j
        i + j
```

`copy_dict_key_to_fast()` executes 65% faster than `dont_copy_dict_key_to_fast()`


### R8203 : Try..except blocks have a significant overhead. Avoid using them inside a loop (`loop-try-except-usage`).

Up to Python 3.10, `try...except` blocks are computationally expensive compared with `if` statements. 

Avoid using them in a loop as they can cause significant overheads. Refactor your code to not require iteration specific details and put the entire loop in the body of a `try` block.

### W8204 : Looped slicing of bytes objects is inefficient. Use a memoryview() instead (`memoryview-over-bytes`)

Slicing of `bytes` is slow as it creates a copy of the data within the requested window. Python has a builtin type, `memoryview` for [zero-copy interactions](https://effectivepython.com/2019/10/22/memoryview-bytearray-zero-copy-interactions):

```python
def bytes_slice():
    """Slice using normal bytes"""
    word = b'A' * 1000
    for i in range(1000):
        n = word[0:i]
        #   ^^^^^^^^^ memoryview-over-bytes

def memoryview_slice():
    """Convert to a memoryview first."""
    word = memoryview(b'A' * 1000)
    for i in range(1000):
        n = word[0:i]

```

`memoryview_slice()` is 30-40% faster than `bytes_slice()`