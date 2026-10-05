# Input contract

`id`: XML-safe ID (`[A-Za-z_][A-Za-z0-9_-]*`); `process`: nonempty string;
`synthetic`: boolean (default false); `source`: nonempty string;
`nodes`: nonempty array of unique `id`, `name`, `type`. Types:
`startEvent`, `endEvent`, `task`, `userTask`, `serviceTask`, `exclusiveGateway`.
`flows`: nonempty array of unique `id`, `source`, `target`, optional `name`
(string), optional `condition` (nonempty string).

Node and flow IDs must be distinct and must not equal the process ID. Exactly
one start event and at least one end event are required. Every node must be
reachable from start and able to reach an end. Start has no incoming flow;
end has no outgoing flow. Flows must reference existing nodes. Conditions are
allowed only on outgoing exclusive-gateway flows. A gateway with multiple
outgoing flows requires a condition on every branch (no implicit default).
Conditions are design text, not executable expressions.

Output XML has BPMN 2.0 namespaces, `isExecutable=false`, documentation,
sequence-flow references and BPMN DI shapes/edges. Graph connectivity and these
structural checks are not a full BPMN engine or formal soundness validation.
