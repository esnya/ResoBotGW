# Global Workspace — Boundary Mock v0.1

A minimal external boundary mock to exercise parallel agent orchestration in tests.

## Purpose

- Isolate Global Workspace logic from Resonite while validating agent collaboration.
- Provide repeatable smoke tests without external dependencies.

## Scope

- Represent world interaction through simple queues for intents and commits.
- Track resource tokens (`speech`, `locomotion`, `head`, `handsL`, `handsR`, `ui`, `sensors`).
- Expose async hooks for agents and test harnesses.

## Components

- **MockWorld**: maintains resource state and applies commits.
- **MockAgentLink**: async channel simulating agent ↔ workspace messaging.
- **Test Harness**: spawns multiple mock agents and verifies arbitration.

## Next Steps

1. Implement `MockWorld` with resource locking semantics.
1. Wire `MockAgentLink` for concurrent proposals.
1. Add smoke tests for `say + look_at + move_to` parallel execution.
