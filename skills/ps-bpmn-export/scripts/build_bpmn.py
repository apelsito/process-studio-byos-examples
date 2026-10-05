"""Export a connected BPMN design and simple DI layout. Python stdlib only."""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
      'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
      'dc': 'http://www.omg.org/spec/DD/20100524/DC',
      'di': 'http://www.omg.org/spec/DD/20100524/DI'}
TYPES = {'startEvent', 'endEvent', 'task', 'userTask', 'serviceTask', 'exclusiveGateway'}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


def tag(prefix, name):
    return '{' + NS[prefix] + '}' + name


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a nonempty string')
    return value.strip()


def ident(value):
    value = text(value, 'id')
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_-]*', value):
        raise ValueError('id must be XML-safe')
    return value


def reachable(seed, adjacency):
    seen, todo = set(), list(seed)
    while todo:
        node = todo.pop()
        if node not in seen:
            seen.add(node)
            todo.extend(adjacency[node])
    return seen


def build(data):
    process_id, name, source = ident(data.get('id')), text(data.get('process'), 'process'), text(data.get('source'), 'source')
    if type(data.get('synthetic', False)) is not bool:
        raise ValueError('synthetic must be boolean')
    nodes, flows = data.get('nodes'), data.get('flows')
    if not isinstance(nodes, list) or not nodes or not isinstance(flows, list) or not flows:
        raise ValueError('nodes and flows must be nonempty arrays')
    by_id, ids = {}, {process_id}
    for node in nodes:
        node_id = ident(node.get('id'))
        if node_id in ids:
            raise ValueError('all process/node/flow ids must be unique')
        ids.add(node_id)
        text(node.get('name'), 'node.name')
        if node.get('type') not in TYPES:
            raise ValueError('unsupported node type')
        by_id[node_id] = node
    starts = [n['id'] for n in nodes if n['type'] == 'startEvent']
    ends = [n['id'] for n in nodes if n['type'] == 'endEvent']
    if len(starts) != 1 or not ends:
        raise ValueError('exactly one start and at least one end required')
    outgoing, incoming = {n: [] for n in by_id}, {n: [] for n in by_id}
    for flow in flows:
        flow_id = ident(flow.get('id'))
        if flow_id in ids:
            raise ValueError('all process/node/flow ids must be unique')
        ids.add(flow_id)
        if flow.get('source') not in by_id or flow.get('target') not in by_id:
            raise ValueError('flow references an unknown node')
        if not isinstance(flow.get('name', ''), str):
            raise ValueError('flow.name must be a string')
        if 'condition' in flow:
            text(flow['condition'], 'condition')
            if by_id[flow['source']]['type'] != 'exclusiveGateway':
                raise ValueError('conditions require an exclusive gateway source')
        outgoing[flow['source']].append(flow['target'])
        incoming[flow['target']].append(flow['source'])
    if incoming[starts[0]] or any(outgoing[end] for end in ends):
        raise ValueError('start cannot have incoming and end cannot have outgoing flows')
    if reachable(starts, outgoing) != set(by_id) or reachable(ends, incoming) != set(by_id):
        raise ValueError('every node must be reachable from start and able to reach an end')
    for node in nodes:
        branches = [f for f in flows if f['source'] == node['id']]
        if node['type'] == 'exclusiveGateway' and len(branches) > 1 and any(not f.get('condition') for f in branches):
            raise ValueError('all outgoing decision branches need explicit conditions')
    # Generate DI IDs from a disjoint pool, even if a user supplied similar IDs.
    def new_id(label):
        candidate = 'di_' + label
        while candidate in ids:
            candidate += '_'
        ids.add(candidate)
        return candidate
    definitions = ET.Element(tag('bpmn', 'definitions'), {'id': new_id('definitions'), 'targetNamespace': 'https://example.org/process-design'})
    process = ET.SubElement(definitions, tag('bpmn', 'process'), {'id': process_id, 'name': name, 'isExecutable': 'false'})
    ET.SubElement(process, tag('bpmn', 'documentation')).text = ('SYNTHETIC DEMONSTRATION DATA. ' if data.get('synthetic', False) else '') + source
    diagram = ET.SubElement(definitions, tag('bpmndi', 'BPMNDiagram'), {'id': new_id('diagram')})
    plane = ET.SubElement(diagram, tag('bpmndi', 'BPMNPlane'), {'id': new_id('plane'), 'bpmnElement': process_id})
    bounds = {}
    for index, node in enumerate(nodes):
        element = ET.SubElement(process, tag('bpmn', node['type']), {'id': node['id'], 'name': node['name']})
        for flow in flows:
            if flow['target'] == node['id']:
                ET.SubElement(element, tag('bpmn', 'incoming')).text = flow['id']
            if flow['source'] == node['id']:
                ET.SubElement(element, tag('bpmn', 'outgoing')).text = flow['id']
        w, h = (36, 36) if node['type'] in ('startEvent', 'endEvent') else (50, 50) if node['type'] == 'exclusiveGateway' else (140, 80)
        x, y = 70 + index % 4 * 220, 100 + index // 4 * 180
        bounds[node['id']] = (x, y, w, h)
        shape = ET.SubElement(plane, tag('bpmndi', 'BPMNShape'), {'id': new_id(node['id'] + '_shape'), 'bpmnElement': node['id']})
        ET.SubElement(shape, tag('dc', 'Bounds'), dict(zip(('x', 'y', 'width', 'height'), map(str, (x, y, w, h)))))
    for flow in flows:
        attrs = {'id': flow['id'], 'sourceRef': flow['source'], 'targetRef': flow['target']}
        if flow.get('name'):
            attrs['name'] = flow['name']
        element = ET.SubElement(process, tag('bpmn', 'sequenceFlow'), attrs)
        if flow.get('condition'):
            ET.SubElement(element, tag('bpmn', 'conditionExpression')).text = flow['condition']
        edge = ET.SubElement(plane, tag('bpmndi', 'BPMNEdge'), {'id': new_id(flow['id'] + '_edge'), 'bpmnElement': flow['id']})
        a, b = bounds[flow['source']], bounds[flow['target']]
        for x, y in [(a[0] + a[2], a[1] + a[3] / 2), (b[0], b[1] + b[3] / 2)]:
            ET.SubElement(edge, tag('di', 'waypoint'), {'x': str(x), 'y': str(y)})
    ET.indent(definitions)
    return ET.tostring(definitions, encoding='utf-8', xml_declaration=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='process.bpmn')
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding='utf-8'))
        report = build(data)
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        parser.exit(2, f'Invalid input: {exc}\n')
    Path(args.output).write_bytes(report)
    print(json.dumps({'artifact': args.output, 'nodes': len(data['nodes']), 'flows': len(data['flows'])}))


if __name__ == '__main__':
    main()
