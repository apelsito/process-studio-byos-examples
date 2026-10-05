"""Render traceable risk/control triage without asserting compliance."""
import argparse
import html
import json
from pathlib import Path


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a nonempty string')
    return value.strip()


def optional(value, field):
    if value is not None and not isinstance(value, str):
        raise ValueError(f'{field} must be a string or null')
    return (value or '').strip()


def rating(value, field):
    if value is not None and (type(value) is not int or not 1 <= value <= 5):
        raise ValueError(f'{field} must be an integer 1..5 or null')
    return value


def render(data):
    process = text(data.get('process'), 'process')
    if type(data.get('synthetic', False)) is not bool:
        raise ValueError('synthetic must be boolean')
    risks = data.get('risks')
    if not isinstance(risks, list) or not risks:
        raise ValueError('risks must be a nonempty array')
    ids, entries = set(), []
    for risk in risks:
        ident, step, name, source = [text(risk.get(k), k) for k in ('id', 'step', 'risk', 'source')]
        if ident in ids:
            raise ValueError('risk ids must be unique')
        ids.add(ident)
        likelihood, impact = [rating(risk.get(k), k) for k in ('likelihood', 'impact')]
        score = likelihood * impact if likelihood is not None and impact is not None else None
        priority = 'Unknown' if score is None else 'High' if score >= 15 else 'Medium' if score >= 6 else 'Low'
        owner = optional(risk.get('owner'), 'owner')
        controls = risk.get('controls')
        if not isinstance(controls, list):
            raise ValueError('controls must be an array')
        gaps, control_text = [], []
        if not owner:
            gaps.append('Missing owner')
        if not controls:
            gaps.append('Missing controls')
        if score is None:
            gaps.append('Unscored risk')
        for control in controls:
            control_name = text(control.get('name'), 'control.name')
            status = control.get('status')
            if status not in ('proposed', 'implemented', 'verified'):
                raise ValueError('control.status must be proposed, implemented or verified')
            evidence = optional(control.get('evidence'), 'control.evidence')
            if status == 'proposed':
                gaps.append('Proposed control: ' + control_name)
            elif not evidence:
                gaps.append('Missing evidence: ' + control_name)
            control_text.append(f'{control_name} [{status}] — {evidence or "No evidence supplied"}')
        values = [ident, step, name, 'Unknown' if score is None else str(score), priority,
                  owner or 'Unknown', '\n'.join(control_text) or 'None supplied', '; '.join(gaps) or 'No gaps flagged', source]
        entries.append((score, ident, values, bool(gaps)))
    entries.sort(key=lambda e: (e[0] is None, -(e[0] or 0), e[1]))
    rows = ''.join('<tr>' + ''.join('<td>' + html.escape(v) + '</td>' for v in row[2]) + '</tr>' for row in entries)
    headers = ['ID', 'Step', 'Risk', 'Score', 'Priority', 'Owner', 'Controls / supplied evidence', 'Review gaps', 'Source']
    title, label = html.escape(process), 'SYNTHETIC DEMONSTRATION DATA' if data.get('synthetic', False) else 'Supplied risk assessment'
    report = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} control register</title><style>body{{font:16px system-ui;margin:2rem;color:#182b3a}}table{{border-collapse:collapse}}th,td{{padding:.8rem;border-bottom:1px solid #ccd6df;text-align:left;white-space:pre-line}}th{{background:#eaf2f8}}.table{{overflow:auto}}</style>
<h1>{title}: control register</h1><p>{label}</p><p>Score = likelihood × impact (each 1–5); High ≥15, Medium ≥6, otherwise Low. Unknown ratings remain unknown.</p>
<div class="table"><table><thead><tr>{''.join('<th>'+h+'</th>' for h in headers)}</tr></thead><tbody>{rows}</tbody></table></div>
<p>Status and evidence are supplied assertions. This report does not verify operating effectiveness or certify compliance.</p></html>'''
    return report, sum(entry[3] for entry in entries)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='controls.html')
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding='utf-8'))
        report, gaps = render(data)
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        parser.exit(2, f'Invalid input: {exc}\n')
    Path(args.output).write_text(report, encoding='utf-8')
    print(json.dumps({'artifact': args.output, 'risks': len(data['risks']), 'risks_with_gaps': gaps}))


if __name__ == '__main__':
    main()
