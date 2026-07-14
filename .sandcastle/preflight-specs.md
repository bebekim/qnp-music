# Spec Preflight

You are running spec preflight for this repository.

Read:

1. `AGENTS.md`
2. `AGENT_LOOP.md`
3. `~/repositories/.night-shift/SPEC_PREFLIGHT.md` if available
4. Relevant files under `docs/`
5. All Markdown files in `Specs/`

## Clarification Guard

If implementation would require an unstated requirement, domain assumption,
environment fact, credential, fixture, dependency, or authority decision, do not
infer it silently.

- During interactive work, ask the smallest clarifying question that closes the
  gap.
- During unattended work, mark the spec `needs-clarification` or `blocked`.
- Record exact questions in `Specs/preflight-report.md`.
- Recommend the spec, doc, test, fixture, or guardrail update that would make
  the work executable next time.

## Goal

Find uncertainty before Night Shift runs. Do not implement product code. Do not
opportunistically fix unrelated issues.

## Review Rules

- Review both `draft-*` and non-draft specs.
- Treat `draft-*` specs as not ready unless the content clearly says otherwise.
- Treat non-draft specs as risky if they still need clarification.
- Identify dependencies between specs.
- Identify missing docs, fixtures, environment variables, credentials, external
  services, migrations, or test commands.
- Identify contradictions between specs and existing project docs.
- If a spec is ready, say why.
- If a spec is not ready, list exact questions or edits needed.
- If a spec has no test plan or acceptance checks, mark it
  `needs-clarification`.
- If a non-draft spec has unresolved blocking open questions, mark it
  `needs-clarification` or `blocked`.

## Output

Write or update `Specs/preflight-report.md` with:

- summary
- specs reviewed
- readiness table
- dependency graph
- clarification questions
- recommended doc updates
- recommended filename changes
- specs safe for Night Shift

Use these states:

- `draft`
- `needs-clarification`
- `blocked`
- `ready`
- `done`

Commit only the preflight report and any small spec metadata/doc routing edits
you make. Do not commit product implementation.

When complete, output:

```text
<promise>SPEC_PREFLIGHT_COMPLETE</promise>
```

