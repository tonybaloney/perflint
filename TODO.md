# TODO

 * The overhead of short-lived memory allocation and how to avoid it
 * Understanding GC-tracked container types and their impact on performance

- Handling constants

 * The performance of module-level and class attribute constants
 * Constant folding

- Calling functions

 * Does that need to be a function? The overhead of function calls in 3.10
 * Comparing function-call types
 * Static/classmethods v.s. functions
 * Why you should avoid using `**kwargs` for known arguments

- Working with variables

 * Bad, Better, Best. Comparing the speed of globals, locals and fast locals
 * The overhead of instance attributes
 * Copying to a logically-named fast local

- That can probably be a function; when classes can be overkill
