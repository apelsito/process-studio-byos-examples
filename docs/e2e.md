# Reproducible acceptance checks

## Local artifacts

```powershell
python skills/ps-kpi-scorecard/scripts/build_scorecard.py --input skills/ps-kpi-scorecard/assets/example.json --output scorecard.html
python skills/ps-raci-matrix/scripts/build_raci.py --input skills/ps-raci-matrix/assets/example.json --output raci.csv
python skills/ps-control-register/scripts/build_controls.py --input skills/ps-control-register/assets/example.json --output controls.html
python skills/ps-bpmn-export/scripts/build_bpmn.py --input skills/ps-bpmn-export/assets/example.json --output process.bpmn
python skills/ps-delivery-handoff/scripts/build_handoff.py --input skills/ps-delivery-handoff/assets/example.json --output handoff.md
python -m unittest discover -s tests -v
```

Expected observable results:

- Scorecard: 3 metrics; cycle time improves 37.50% but misses target, accuracy
  improves 15.00% and achieves target, unmeasured cost remains Unknown.
- RACI: 2 activities; review exception flags a missing accountable owner.
- Controls: 3 risks; R1 score 20 High, R2 score 6 Medium, R3 unscored Unknown;
  proposed controls and missing evidence/owners remain review gaps.
- BPMN: 5 nodes and 5 flows, 5 DI shapes and 5 edges; decision conditions
  preserved; process is non-executable.
- Handoff: 3 items, evidence retained, no verification layer promoted; the
  unknown item has 2 verification gaps.

## Live Process Studio E2E

Use a fresh synthetic test project in the environment authorized for testing.
Do not alter ArgoCD revisions, image tags, sandbox policy or existing projects
to make an acceptance check pass.

1. Record the environment, relevant deployed image and source repository commit.
2. Import this repository with branch `main` and skills folder `skills` through
   Settings. Observe synchronization and the real security/prerequisite scan.
3. Confirm exactly five usable skills. Persist their assignments to the new
   project and reload to check that assignments survive.
4. For each skill, request the bundled synthetic demo in a separate chat and
   retain the chat/run ID. Confirm the actual bundled script runs through the
   environment's sandbox; model text alone is not execution evidence.
5. Check the observable results above, open/download the generated artifact,
   reload the chat and verify the persisted artifact remains available.
6. Try one missing-input request and one invalid-input request. Expect a clear
   input gate/error and no invented successful deliverable.

Record pass/fail/blocked per step, with observed evidence. ArgoCD Healthy proves
rollout health, not runtime correctness. If an import or runtime dependency fails,
retain that exact failure and stop the dependent steps. Synthetic test artifacts
may remain in the test project for review; do not silently delete user data.
