# Process Studio BYOS examples

Five useful, self-contained Agent Skills for process-design work. Created with
the `skill-creator` workflow: focused routing descriptions, concise instructions,
linked input contracts, bundled resources and behavioral validation.
All examples and fixtures are synthetic. No internal source code, credentials,
client data or proprietary method documents are included.

| Skill | Useful result | Output |
|---|---|---|
| `ps-kpi-scorecard` | Direction-aware KPI improvement and target comparison, with unknowns preserved | HTML |
| `ps-raci-matrix` | Activity/role assignments with accountability and responsibility gaps | CSV |
| `ps-control-register` | Risk prioritization, proposed controls and missing owner/evidence findings | HTML |
| `ps-bpmn-export` | Connected BPMN 2.0 process graph with diagram layout and conditional branches | BPMN XML |
| `ps-delivery-handoff` | Evidence-linked deliverables, blockers and next actions with explicit verification layers | Markdown |

## Import into Process Studio

In your authorized test environment, open **Settings → Skills** and add a source:

- Repository: `https://github.com/apelsito/process-studio-byos-examples`
- Branch: `main`
- Skills folder: `skills`
- Public repository: use the product's public-source option; no token is needed
  by this repository. If the running version requires one, that is an application
  requirement, not a secret shipped with these examples.

Wait for synchronization and security/dependency checks. Confirm that all five
skills are visible, enabled and eligible for execution. Assign them to a test
project owned by your account. Keep an existing QA project's assignments intact.

Example prompt:

> Use ps-kpi-scorecard. This is a synthetic demo: read the bundled
> assets/example.json, generate the scorecard with the bundled script, save it
> as an output and provide the downloadable HTML. Keep the synthetic label.

Replace the skill name for the other four. For real project use, provide the
inputs described in each skill's `references/input.md` or identify the blueprint
and evidence to extract. Missing inputs should prompt a question; unknown
measurements must stay unknown.

## Runtime contract

Each skill is a direct child of `skills/` and contains `SKILL.md` with standard
Agent Skills frontmatter, an explicit `allowed-tools` declaration, a JSON input
contract, a synthetic input and one Python script. `scripts/manifest.json`
declares the permitted script and typed `--input` / `--output` arguments for
Process Studio. Paths are relative to the skill's execution workspace.

The agent normalizes input via `write_temp_file`, calls `run_skill_script`,
checks success, then persists the artifact with `save_output_file`. This
separation makes scripts deterministic while the agent interprets the process.
The scripts do not call APIs, read environment credentials, install dependencies
or require Bash, Node, network access or third-party Python packages. They are
compatible candidates for the Python Lambda script contract, subject to the
running environment's policy, scanner, model and deployment compatibility.
Tool names are Process Studio-specific; another Agent Skills host must map its
own file/execution tools.

## Run locally

Python 3.12+; the five scripts and their tests use the standard library only.

```powershell
python skills/ps-kpi-scorecard/scripts/build_scorecard.py --input skills/ps-kpi-scorecard/assets/example.json --output scorecard.html
python -m unittest discover -s tests -v
```

Run all five example commands listed in [docs/e2e.md](docs/e2e.md).
Local validation proves script behavior and package structure. It does not
establish successful source scan, project assignment, live Lambda execution,
chat persistence, downloads or QA acceptance in any Process Studio environment.

MIT licensed. Example reports support human review; supplied evidence is not
independently verified and no workflow or approval is executed.
