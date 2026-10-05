"""Export a RACI matrix without inventing ownership. Python stdlib only."""
import argparse
import csv
import io
import json
from pathlib import Path


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a nonempty string')
    return value.strip()


def safe_cell(value):
    value = str(value)
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else value


def build(data):
    process = text(data.get('process'), 'process')
    if type(data.get('synthetic', False)) is not bool:
        raise ValueError('synthetic must be boolean')
    roles = data.get('roles')
    if not isinstance(roles, list) or not roles:
        raise ValueError('roles must be a nonempty array')
    roles = [text(r, 'role') for r in roles]
    if len(set(roles)) != len(roles):
        raise ValueError('roles must be unique')
    activities = data.get('activities')
    if not isinstance(activities, list) or not activities:
        raise ValueError('activities must be a nonempty array')
    rows, ids, warnings = [], set(), 0
    for activity in activities:
        ident, name, source = [text(activity.get(k), k) for k in ('id', 'name', 'source')]
        if ident in ids:
            raise ValueError('activity ids must be unique')
        ids.add(ident)
        assignments = activity.get('assignments')
        if not isinstance(assignments, dict) or set(assignments) - set(roles):
            raise ValueError('assignments must map only declared roles')
        if any(v not in ('R', 'A', 'C', 'I', '') for v in assignments.values()):
            raise ValueError('assignments must use R, A, C, I or empty string')
        codes = [assignments.get(role, '') for role in roles]
        findings = []
        if codes.count('A') != 1:
            findings.append(f'Expected one accountable owner; found {codes.count("A")}')
        if 'R' not in codes:
            findings.append('Missing responsible role')
        warnings += bool(findings)
        rows.append([process, 'SYNTHETIC' if data.get('synthetic', False) else 'Supplied assignments',
                     ident, name, *codes, '; '.join(findings) or 'OK', source])
    stream = io.StringIO(newline='')
    writer = csv.writer(stream)
    writer.writerow(['Process', 'Data kind', 'Activity ID', 'Activity', *['Role: ' + r for r in roles], 'Ownership review', 'Source'])
    writer.writerows([[safe_cell(cell) for cell in row] for row in rows])
    return stream.getvalue(), warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='raci.csv')
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding='utf-8'))
        report, warnings = build(data)
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        parser.exit(2, f'Invalid input: {exc}\n')
    Path(args.output).write_text(report, encoding='utf-8-sig', newline='')
    print(json.dumps({'artifact': args.output, 'activities': len(data['activities']), 'ownership_warnings': warnings}))


if __name__ == '__main__':
    main()
