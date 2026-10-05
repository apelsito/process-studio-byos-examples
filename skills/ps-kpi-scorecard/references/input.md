# Input contract

UTF-8 JSON object with `process` (nonempty string), `period` (nonempty string),
`synthetic` (boolean, default false), and nonempty `metrics` array.
Each metric has unique `id`, `name`, `unit`, `source` (nonempty strings),
`direction` (`lower` or `higher`), and `baseline`, `current`, `target` (finite
JSON numbers or null). Do not mix units or periods in one metric.

Improvement = `(current - baseline) / abs(baseline) * 100`, multiplied by -1
when lower is better. It is unknown if either value is null or baseline is zero.
Target is achieved for `current <= target` (lower), or `current >= target`
(higher). A missing current or target produces unknown target status.

The output is a self-contained HTML file. Values and sources are escaped as
text. It does not query or modify a Process Studio project.
