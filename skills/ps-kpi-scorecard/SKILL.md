---
name: ps-kpi-scorecard
description: Build an offline HTML KPI scorecard from a process blueprint and supplied baseline, current and target measurements. Use for a process performance review with explicit units and direction.
license: MIT
allowed-tools: list_skill_files read_skill_file write_temp_file read_temp_file list_temp_files run_skill_script save_output_file
metadata:
  author: apelsito
  version: "1.0.0"
---

# Process KPI scorecard

Produce a downloadable HTML scorecard for the selected process. Calculations
run in the bundled Python script using the standard library; no package
installation, shell, external service or live telemetry is needed.

Read [references/input.md](references/input.md) for the JSON contract. Use
measurements supplied in the conversation or explicitly identified project
documents. Preserve their source labels, units and reporting period. Ask for
the missing metric name/unit/direction when needed; in Process Studio end a
missing-input question with `<<<NEEDS_INPUT>>>`. Do not invent measured values
or turn a benchmark into the project's current result. Use `null` for unknown
baseline, current or target values.

Write the normalized JSON with `write_temp_file` as `input.json`, then call
`run_skill_script` with `script_rel_path="scripts/build_scorecard.py"` and
`script_args=["--input", "input.json", "--output", "scorecard.html"]`.
Read the generated file or script result, check exit code and the metric count,
then use `save_output_file` to persist `scorecard.html` and deliver the download.
If execution fails, report the error; no scorecard has been delivered.

The report marks missing values as unknown. Improvement is direction-aware;
baseline zero makes percentage change unavailable. Target status compares
current to target and does not assert statistical significance or causality.
For a demonstration only, load [assets/example.json](assets/example.json) and
keep the synthetic-data label visible.
