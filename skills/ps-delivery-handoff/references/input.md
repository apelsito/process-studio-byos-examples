# Input contract

`project`, `scope`, `as_of`: nonempty strings; `synthetic`: boolean (default
false); `items`: nonempty array with unique nonempty `id`, `deliverable`,
`owner`, `next_action`; `layer`: `unknown`, `implemented`, `locally_verified`,
`merged`, `deployed`, `runtime_verified`, `accepted`; `evidence`: array of
strings (may be empty); `blocker`: string or null. Evidence strings must be
nonempty. An empty evidence array adds a verification-gap finding even when
the claimed layer is accepted. A nonempty evidence list is a supplied
assertion; the script does not validate URLs or inspect external systems.

Output Markdown table: deliverable, supplied verification layer, owner,
evidence, blocker, next action. The table escapes pipe characters and line
breaks. An additional verification-gaps section flags missing evidence and
unknown layers without promoting the claim. No item is automatically advanced
to another layer. Names must describe roles when publishing synthetic examples.
