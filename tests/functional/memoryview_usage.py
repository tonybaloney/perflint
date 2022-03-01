def example_bytes_slice():
    word = b'the lazy brown dog jumped'
    for i in range(10):
        # Memoryview slicing is 10x faster than bytes slicing
        if word[0:i] == 'the':
            return True

def example_bytes_slice_as_arg(word: bytes):
    for i in range(10):
        # Memoryview slicing is 10x faster than bytes slicing
        if word[0:i] == 'the':
            return True
