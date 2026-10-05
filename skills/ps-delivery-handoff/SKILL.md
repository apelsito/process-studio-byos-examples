---
name: ps-delivery-handoff
description: Generate a traceable Markdown delivery handoff from a process blueprint, implementation evidence and open items. Use to separate code, deployment and acceptance status and assign concrete next actions.
license: MIT
allowed-tools: list_skill_files read_skill_file write_temp_file read_temp_file list_temp_files run_skill_script save_output_file
metadata:
  author: apelsito
  version: "1.0.0"
---

# Process delivery handoff

Read [references/input.md](references/input.md). Normalize the supplied project
scope, completed items, evidence and open actions into JSON. Each item must have
one explicit verification layer: implementation, local tests, merged, deployed,
runtime verified or accepted. A merge or healthy pod does not establish runtime
behavior. Preserve blockers and attach evidence to the claim it supports.

Do not mark an item accepted without explicit acceptance evidence. If required
scope or handoff items are missing, ask for them and end the question with
`<<<NEEDS_INPUT>>>` in Process Studio. Unknowns may remain unknown with a
concrete next action. Do not assign people or modify tickets: this skill
generates a document only.

Write `input.json` using `write_temp_file`, then call `run_skill_script` with
`script_rel_path="scripts/build_handoff.py"` and
`script_args=["--input", "input.json", "--output", "handoff.md"]`.
Check script success, read the resulting handoff and persist `handoff.md` with
`save_output_file`. Deliver the file and briefly state unresolved blockers.

The output uses English by default for a copy-ready delivery handoff. Translate
the supplied prose into the user's requested language before normalizing when
requested; preserve evidence references. The script only formats supplied
claims and flags evidence gaps. It does not retrieve live status or send the
handoff. For a demo use [assets/example.json](assets/example.json), retaining
its synthetic-data label. Python standard library only.
