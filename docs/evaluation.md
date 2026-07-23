# Evaluation Guide

The benchmark contains 100 manually labeled Indian legal questions in `evaluation/datasets/legal_queries.jsonl`. Each row includes the question, expected legal issue, expected citation keywords, and unsafe/refusal expectation.

Metrics:

- Citation accuracy: cited sources must appear in retrieved evidence.
- Precision and recall: retrieved chunks versus expected citation keywords.
- Faithfulness: answer claims must be supported by context.
- Latency: end-to-end query duration.
- Hallucination rate: unsupported answer percentage.
- Context recall: percentage of expected legal concepts present in context.

Run:

```bash
cd backend
python -m app.cli.run_evaluation
```

