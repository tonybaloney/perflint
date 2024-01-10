# Changes

## 0.8.0 (10th January 2024)

* fix: pre-commit configuration filename by @adamantike in https://github.com/tonybaloney/perflint/pull/32
* Test other versions of Python in CI by @tonybaloney in https://github.com/tonybaloney/perflint/pull/33
* Migrate to pylint v3 by @jenstroeger in https://github.com/tonybaloney/perflint/pull/46
* Drop support for Python 3.7
* Add support for Python 3.12

## 0.7.3 (16th May 2022)

* Fixes a regression bug in the loop invariant name

## 0.7.2 (12th May 2022)

* Renamed the global usage in loop to `loop-global-usage`
* Added support for invariant f-strings
* Bugfix: Doesn't highlight list, tuple or dict with only constant values as being invariant

## 0.7.1 (1st April 2022)

* Bugfix: No longer suggests list comprehensions when the if statement has an elif/else clause
* Bugfix: Pylint enable/disable arguments are allowed on the `perflint` CLI entry point

## 0.7.0 (28th March 2022)

* Added a standalone entry point (`perflint`)

## 0.6.0 (25th March 2022)

* Added checks for list and dictionary comprehensions as faster alternatives to loops

## 0.5.1 (25th March 2022)

* Marks global lists which are mutated in local scopes

## 0.5.0 (25th March 2022)

* Added a check for non-mutated lists where a tuple would be more efficient (W8301)

## 0.4.1 (21st March 2022)

* (BUG) No longer raises unary operators against const values
* (BUG) No longer raises slices as invariant expressions
* (BUG) raise, return, yield and yield from are considered variant expressions because they impact control-flow

## 0.4.0 (21st March 2022)

* `print()` is considering as having a side-effect and variant.
* Constant values explored in loop-invariance
* Assignment statements have been corrected for constant values
