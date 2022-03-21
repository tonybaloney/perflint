# Changes

## 0.4.1 (21st March 2022)

* (BUG) No longer raises unary operators against const values
* (BUG) No longer raises slices as invariant expressions
* (BUG) raise, return, yield and yield from are considered variant expressions because they impact control-flow

## 0.4.0 (21st March 2022)

* `print()` is considering as having a side-effect and variant.
* Constant values explored in loop-invariance
* Assignment statements have been corrected for constant values
