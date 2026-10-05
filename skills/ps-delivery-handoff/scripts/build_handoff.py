"""Format supplied readiness claims and expose gaps. Python stdlib only."""
import argparse
import json
from pathlib import Path

LAYERS = {'unknown', 'implemented', 'locally_verified', 'merged', 'deployed', 'runtime_verified', 'accepted'}


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a nonempty string')
    return value.strip()


def cell(value):
    # Escape markup from supplied labels while preserving readable references.
    value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    for character in ('\\', '|', '`', '*', '_', '[', ']'):
        value = value.replace(character, '\\' + character)
    return value.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br>')


def build(data):
    project, scope, as_of = [text(data.get(k), k) for k in ('project', 'scope', 'as_of')]
    if type(data.get('synthetic', False)) is not bool:
        raise ValueError('synthetic must be boolean')
    items = data.get('items')
    if not isinstance(items, list) or not items:
        raise ValueError('items must be a nonempty array')
    ids, rows, gaps = set(), [], []
    for item in items:
        ident, deliverable, owner, next_action = [text(item.get(k), k) for k in ('id', 'deliverable', 'owner', 'next_action')]
        if ident in ids:
            raise ValueError('item ids must be unique')
        ids.add(ident)
        layer = item.get('layer')
        if layer not in LAYERS:
            raise ValueError('unsupported verification layer')
        evidence = item.get('evidence')
        if not isinstance(evidence, list):
            raise ValueError('evidence must be an array')
        evidence = [text(value, 'evidence') for value in evidence]
        blocker = item.get('blocker')
        if blocker is not None and not isinstance(blocker, str):
            raise ValueError('blocker must be a string or null')
        if not evidence:
            gaps.append(f'{ident}: no evidence supplied for the claimed {layer} layer')
        if layer == 'unknown':
            gaps.append(f'{ident}: verification layer unknown')
        rows.append('| ' + ' | '.join(cell(value) for value in [ident + ': ' + deliverable, layer, owner,
                    '; '.join(evidence) or 'No evidence supplied', blocker or 'None supplied', next_action]) + ' |')
    label = 'SYNTHETIC DEMONSTRATION DATA' if data.get('synthetic', False) else 'Supplied delivery evidence'
    report = f'# {cell(project)}: delivery handoff\n\n{label}\n\nAs of: {cell(as_of)}\n\nScope: {cell(scope)}\n\n'
    report += '| Deliverable | Supplied layer | Owner | Evidence | Blocker | Next action |\n|---|---|---|---|---|---|\n' + '\n'.join(rows)
    report += '\n\n## Verification gaps\n\n' + ('\n'.join('- ' + cell(gap) for gap in gaps) if gaps else 'No missing-evidence or unknown-layer gaps flagged.')
    report += '\n\nThis document formats supplied claims. Evidence references have not been checked live; no acceptance, ticket or deployment state has been changed.\n'
    return report, len(gaps)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='handoff.md')
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding='utf-8'))
        report, gaps = build(data)
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        parser.exit(2, f'Invalid input: {exc}\n')
    Path(args.output).write_text(report, encoding='utf-8')
    print(json.dumps({'artifact': args.output, 'items': len(data['items']), 'verification_gaps': gaps}))


if __name__ == '__main__':
    main()
