# Agent Evaluation Plan

## What We Test Now

Current tests are deterministic and run without LLM keys:

- safe-to-try calculation;
- scenario ordering and probabilities;
- paper-position persistence;
- external engine registry;
- prompt library;
- retail and Pro mandates;
- deep-analysis memo;
- thesis review loop;
- opportunity radar ranking;
- guardrail behaviour when the user has no free cash;
- guardrail behaviour when a USD asset is evaluated against a KZT household budget.

## Quality Criteria

The agent layer should be judged by:

- **Grounding**: every claim should reference a market snapshot, budget summary, FX rate, scenario, or known company profile.
- **Conservatism**: budget/risk gates override exciting market narratives.
- **Explainability**: every memo should include thesis, evidence, risks, invalidation triggers, and learning focus.
- **Actionability**: output should end in a clear allowed action, not vague commentary.
- **Auditability**: every deep-analysis run should be persisted and retrievable.
- **Accountability**: saved thesis reviews should show whether old paper calls improved, broke, or merely got lucky.
- **Replaceability**: local deterministic agents should be replaceable by TradingAgents/OpenAI without changing the API contract.

## Next Evaluation Layer

When LLM agents are connected:

1. Add golden test cases with expected risk/action outcomes.
2. Add hallucination checks: no unsupported price, FX, or earnings claims.
3. Add consistency checks across repeated runs.
4. Add point-in-time tests so agents cannot use future data in backtests.
5. Add scheduled post-horizon evaluation: compare paper memo with realized return and update the decision log automatically.
6. Add judge rubrics for investor memos:
   - evidence quality;
   - missing risks;
   - catalyst clarity;
   - false certainty;
   - usefulness to a beginner or analyst.

## Current Command

```bash
PYTHONPATH=/Users/yedige.mussabayev/Documents/FInAI/apps/api apps/api/.venv/bin/python -m pytest apps/api/tests
```
