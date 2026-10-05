"""Render a KPI scorecard with direction-aware calculations. Python stdlib only."""
import argparse
import html
import json
import math
from pathlib import Path


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a nonempty string')
    return value.strip()


def number(value, field):
    if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
        raise ValueError(f'{field} must be a finite number or null')
    return value


def render(data):
    process = text(data.get('process'), 'process')
    period = text(data.get('period'), 'period')
    if type(data.get('synthetic', False)) is not bool:
        raise ValueError('synthetic must be boolean')
    metrics = data.get('metrics')
    if not isinstance(metrics, list) or not metrics:
        raise ValueError('metrics must be a nonempty array')
    ids, rows = set(), []
    for metric in metrics:
        ident = text(metric.get('id'), 'metric.id')
        if ident in ids:
            raise ValueError('metric ids must be unique')
        ids.add(ident)
        name, unit, source = [text(metric.get(k), k) for k in ('name', 'unit', 'source')]
        direction = metric.get('direction')
        if direction not in ('lower', 'higher'):
            raise ValueError('direction must be lower or higher')
        baseline, current, target = [number(metric.get(k), k) for k in ('baseline', 'current', 'target')]
        improvement = None
        if baseline not in (None, 0) and current is not None:
            improvement = (current - baseline) / abs(baseline) * 100 * (-1 if direction == 'lower' else 1)
        status = 'Unknown'
        if current is not None and target is not None:
            achieved = current <= target if direction == 'lower' else current >= target
            status = 'Achieved' if achieved else 'Not achieved'
        display = lambda v: 'Unknown' if v is None else f'{v:g}'
        values = [name, unit, direction, display(baseline), display(current), display(target),
                  'Unknown' if improvement is None else f'{improvement:+.2f}%', status, source]
        rows.append('<tr>' + ''.join('<td>' + html.escape(v) + '</td>' for v in values) + '</tr>')
    title = html.escape(process)
    label = 'SYNTHETIC DEMONSTRATION DATA' if data.get('synthetic', False) else 'Supplied measurements'
    headers = ['Metric', 'Unit', 'Better', 'Baseline', 'Current', 'Target', 'Improvement', 'Target status', 'Source']
    return f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} KPI scorecard</title>
<style>body{{font:16px system-ui;margin:2rem;color:#182b3a}}table{{border-collapse:collapse;width:100%}}th,td{{padding:.8rem;border-bottom:1px solid #ccd6df;text-align:left}}th{{background:#eaf2f8}}.table{{overflow:auto}}</style>
<h1>{title}: KPI scorecard</h1><p>{html.escape(period)} · {label}</p>
<p>{len(metrics)} metrics. Positive improvement means movement in the preferred direction.</p>
<div class="table"><table><thead><tr>{''.join('<th>'+h+'</th>' for h in headers)}</tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p>Unknown values are not imputed. Percentage improvement is unavailable for a zero baseline.
Target status is a point comparison, not proof of causality or statistical significance.</p></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='scorecard.html')
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding='utf-8'))
        report = render(data)
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        parser.exit(2, f'Invalid input: {exc}\n')
    Path(args.output).write_text(report, encoding='utf-8')
    print(json.dumps({'artifact': args.output, 'metrics': len(data['metrics'])}))


if __name__ == '__main__':
    main()
