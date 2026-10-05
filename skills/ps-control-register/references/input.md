# Input contract

`process`: nonempty string; `synthetic`: boolean (default false);
`risks`: nonempty array. Each risk has unique nonempty `id`, `step`, `risk`,
`source`; `likelihood` and `impact`: integers 1..5 or null; `owner`: string or
null; `controls`: array, possibly empty. Each control has nonempty `name`,
`status`: `proposed`, `implemented` or `verified`, and `evidence`: string or
null. Status is supplied by the user and is not checked against a live system.
Missing evidence is flagged for implemented/verified controls; proposed
controls remain gaps even if a design document is supplied.

Score = likelihood * impact. Review priority: 15..25 High, 6..14 Medium, 1..5
Low, null Unknown. This is a simple ordinal triage scale, not a residual-risk
model, certification or quantitative probability estimate.
