# Input contract

`process`: nonempty string; `synthetic`: boolean (default false);
`roles`: nonempty array of unique nonempty strings;
`activities`: nonempty array with unique `id`, `name`, `source` strings and
`assignments`: object mapping role names to `R`, `A`, `C`, `I` or empty string.
Unspecified roles become empty cells. Unknown roles and other codes are errors.
The process, IDs, activity names and sources must be nonempty strings.

Output CSV columns: Process, Data kind, Activity ID, Activity, one column per
role, Ownership review, Source. An activity should have exactly one A and at
least one R; the report flags violations without changing assignments. Role
columns have a `Role: ` prefix to avoid ambiguous header names.

CSV cells beginning with a spreadsheet formula prefix are prefixed with an
apostrophe so opening a supplied name as a spreadsheet does not execute it.

