---
name: ps-control-register
description: Produce an offline HTML register of process risks, controls, owners and evidence gaps, with explicit likelihood-impact scoring. Use to review blueprint guardrails and human approval gates.
license: MIT
allowed-tools: list_skill_files read_skill_file write_temp_file read_temp_file list_temp_files run_skill_script save_output_file
metadata:
  author: apelsito
  version: "1.0.0"
---

# Process control register

Read [references/input.md](references/input.md) and normalize the supplied risks,
controls, owners and evidence into JSON. Preserve links to process steps and
source labels. Proposed controls must remain proposals; supplied evidence is
not verified operating effectiveness. Do not score unknown likelihood or impact
by guessing, or claim regulatory compliance from the presence of a control.

If no process or risks are available, request them and end the question with
`<<<NEEDS_INPUT>>>` in Process Studio. Write `input.json` via `write_temp_file`,
then call `run_skill_script` with `script_rel_path="scripts/build_controls.py"`
and `script_args=["--input", "input.json", "--output", "controls.html"]`.
Verify the script's success and review-gap count, read the report, then persist
`controls.html` with `save_output_file` and deliver the download.

The output sorts known scores highest first and places unscored risks last.
Highlight missing owners, missing controls, proposed controls and missing evidence.
For a demonstration use [assets/example.json](assets/example.json) and preserve
the synthetic label. This is a standard-library Python report generator; it
neither queries external systems nor changes approvals or configuration.

