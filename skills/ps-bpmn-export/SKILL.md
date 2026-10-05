---
name: ps-bpmn-export
description: Export a BPMN 2.0 process diagram from explicit activities, decisions and sequence flows. Use for a portable process-design artifact with task types and conditional branches.
license: MIT
allowed-tools: list_skill_files read_skill_file write_temp_file read_temp_file list_temp_files run_skill_script save_output_file
metadata:
  author: apelsito
  version: "1.0.0"
---

# BPMN process export

Read [references/input.md](references/input.md). Map the selected process's
explicit activities and decisions to the JSON graph; preserve step IDs, names,
flow direction, branch conditions and source labels. Use a user task for a human
activity and a service task for an automated activity only when the blueprint
supports that distinction. Ask for missing decision paths rather than silently
linearizing the process. In Process Studio, end missing-input questions with
`<<<NEEDS_INPUT>>>`.

Write `input.json` using `write_temp_file`, then execute
`scripts/build_bpmn.py` with `run_skill_script` and
`script_args=["--input", "input.json", "--output", "process.bpmn"]`.
Check exit status and node/flow counts, then use `save_output_file` to persist
`process.bpmn` and provide the download. Read any graph-validation error and
correct the input from the actual design before retrying.

The exporter includes BPMN DI positions and edges for diagram viewers. The
layout is a simple grid intended as an editable starting point. This is a
non-executable design export: it does not deploy a workflow, connect tasks to
services or prove absence of deadlocks. For a demo, use
[assets/example.json](assets/example.json) and keep its synthetic label.
The script uses Python's standard library only.
