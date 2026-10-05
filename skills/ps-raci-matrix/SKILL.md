---
name: ps-raci-matrix
description: Export a spreadsheet-ready RACI matrix for process activities and flag missing or multiple accountable owners. Use when a blueprint needs explicit delivery and operational responsibility.
license: MIT
allowed-tools: list_skill_files read_skill_file write_temp_file read_temp_file list_temp_files run_skill_script save_output_file
metadata:
  author: apelsito
  version: "1.0.0"
---

# Process RACI matrix

Turn supplied activity and role assignments into a downloadable UTF-8 CSV.
Read [references/input.md](references/input.md). Extract responsibilities from
the selected blueprint or conversation with a source label per activity.
Keep role names stable. An agent can be responsible; assign accountability only
where the supplied design identifies an owner. Leave uncertain cells blank and
surface them in the output. Never silently add an accountable role to pass a check.

If activities or roles are absent, ask for them and end the question with
`<<<NEEDS_INPUT>>>` in Process Studio. Write the normalized JSON to `input.json`
with `write_temp_file`. Execute `scripts/build_raci.py` using
`run_skill_script` with `script_args=["--input", "input.json", "--output", "raci.csv"]`.
Check success and the counts of activities and ownership warnings, then persist
`raci.csv` with `save_output_file` and provide the download.

Explain any activity with zero or multiple A assignments and any missing R.
These are review findings, not changes to project membership or permissions.
For a demo, use [assets/example.json](assets/example.json); it deliberately
contains an ownership gap and remains visibly synthetic. The script requires
only Python's standard library and does not access external systems.
