# Lost in the Middle harness

Rebuilds the Liu et al. test from scratch: same question, same
documents, the answer document moved from the start to the middle
to the end. Measures accuracy by answer position.

Paper: https://arxiv.org/abs/2307.03172

## Why

Models get long contexts and still miss the answer when it sits
in the middle. This harness measures that on a small local model
instead of taking the paper's word for it.

## How it works

- 12 questions in `data/golden.jsonl`. The facts are invented,
  so the model cannot answer from pretraining. It has to read
  the context.
- Each question has one gold document holding the answer and
  8 distractor documents about similar invented entities.
  All documents are 30-70 words, so length is not a cue.
- Each question runs three times: gold document at the start,
  the middle, and the end of 9 documents.
- Scoring is a plain substring match on the answer. No LLM judge.

## Model

Qwen/Qwen2.5-0.5B-Instruct, local, greedy decoding. No API key,
no paid service. The same model as the AgentOps Workbench brain.

## Run it

```bash
python3 -m venv .venv
.venv/bin/python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -m pip install transformers
.venv/bin/python harness.py            # full run, 12 questions x 3 positions, 9 docs
.venv/bin/python harness.py --num-docs 20   # same, with 20 documents
.venv/bin/python harness.py --num-docs 20 --prompt quote   # quote the supporting doc first
.venv/bin/python harness.py --smoke    # 1 question, checks it runs
```

The `quote` prompt asks the model to quote the document that
answers the question, then give the answer on an `Answer:`
line. Scoring measures the final answer only, not the quote.

On a Mac, install torch without the `--index-url` flag:
`.venv/bin/python -m pip install torch`

Results go to `runs/results.jsonl`, with accuracy by position
printed at the end.

## Results

- 9 documents: start 12/12, middle 9/12, end 11/12.
  See `docs/lostinthemiddle_2026-11-24.md`.
- 20 documents: start 12/12, middle 6/12, end 11/12.
  See `docs/lostinthemiddle_20docs_2026-11-25.md`.
- 20 documents, quote-first prompt: start 12/12, middle 7/12,
  end 11/12. See `docs/lostinthemiddle_20docs_quote_2026-11-26.md`.
