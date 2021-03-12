# History

## v0.2.8

- Mostly meta adjustments.

## v0.2.7

- Adding exception for duplicate node annotations

## v0.2.6

- Minor fixes regarding investigation file names and comments.

## v0.2.5

- Minor fixes of validation and warnings.
- Fixes optional parameter `filename` of `AssayReader`.

## v0.2.4

- Ensuring that input order is output order.
  This is true except for the corner case where materials are not located in "blocks".
  Such corner cases would require storing the tabular representation (and keeping it in sync) at all times and does not yield to a robustly usable implementation.
  NB: the input is also not sorted the test adjusted with this patch shows.
- Adding optional parameter `filename` to the various readers.
- Exposing `RefTableBuilder` class with slightly changed interface.

## v0.2.3

- Minor fixes and additions with focus on improving the export.

## v0.2.2

- Updating documentation for JOSS.

## v0.2.1

- Adding JOSS paper draft.
- Fixing problem with writing empty lines on Windows (#52).
- Update documentation with examples for manual model creation.
- Fixing authorship documentation.
- Fixing package (#58).

## v0.2.0

- Switching to `attrs` instead of using `Namedtuple`.
  This gets rid of some warts regarding constructor overriding but should offer the same functionality otherwise.
- Various updates to the documentation.

## v0.1.0

First public release.

- Started out with ISA-TAB parser and `NamedTuple`-based data model.
