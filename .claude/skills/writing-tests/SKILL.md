---
name: writing-tests
description: Testing policy for backend and frontend: API-first tiering, assertion depth, and test-quality rules. Load before writing or reviewing tests.
---

# Testing policy

## Backend: default to an API test

The verification weight of the suite is carried by API-level tests that run the
real stack (HTTP client → router → use case → repository → in-memory SQLite).
New behaviour means a new or extended API test in `backend/tests/test_*.py`,
exercised through the endpoint, not the internals. Use the `client` fixture from
`tests/conftest.py`.

## Unit tests must be earned

Write a unit test (`backend/tests/unit/`) only for pure domain logic with real
branching: value objects, aggregates' invariants, parsers, domain services.
Litmus test: can you enumerate meaningful input classes without mocking
anything? If the setup needs a mock, the behaviour belongs in an API test.

Do NOT write mock-based tests for thin orchestration (application use cases). A
test asserting "the repository was called" mirrors the implementation: it breaks
on refactors and survives logic bugs.

```python
# ✗ WRONG: verifies the mock you just configured
use_case = CreateNoteUseCase(note_repository=mock_repo)
await use_case.create_note("t", "b")
mock_repo.save.assert_called_once()

# ✓ CORRECT: the API test covers the same wiring with real behaviour
response = await client.post("/api/v1/notes", json={"title": "t"})
assert response.status_code == 201
assert response.json()["title"] == "t"
```

## No mocks outside `tests/unit/infrastructure/`

Ruff's `TID251` bans `unittest.mock` everywhere else. Stub external boundaries
(HTTP APIs, queues, storage) with hand-written fakes plus pytest's `monkeypatch`.

## Assertion depth

- Assert the meaningful fields of the response body, never just the status code.
- For mutating endpoints, verify persistence with a follow-up read.
- Once resources belong to users: every endpoint gets a user-isolation case
  (user B gets 404 on user A's resource). A dropped ownership filter is the
  worst realistic bug class, and only a deliberate test catches it.

## Frontend

- `.test.ts` is pure logic, run in node. `.test.tsx` renders, in real Chromium.
- A rendering test drives a real route with `renderApp` from
  `@tests/harness/renderApp`, against MSW handlers in `tests/msw/`. Rendering a
  component on its own is allowed only in the component tier: the directories
  in the last `overrides` entry of `.oxlintrc.json` (`src/hooks/` by default).
- Query by role and accessible name (`getByRole('button', { name: 'Add note' })`).
  If an element has no accessible name, give it one in `src/`.
- Never sleep. Wait for a state with `expect.element` or `expect.poll`.

## Prove the test can fail

After writing a test, temporarily break the code under test (invert the
condition, short-circuit the function), confirm the test fails, then revert. A
test that cannot fail is worse than no test. Include at least one input where
the expected output differs from the input.

## What not to test

Do not test framework behaviour, exception-message wiring, or anything fully
shadowed by a stronger API test. Delete weak tests when you find them.

## Mechanics

- Keep test cases short; share setup through fixtures, reusing existing ones.
- Run the full suites before declaring work done: `make test`.
