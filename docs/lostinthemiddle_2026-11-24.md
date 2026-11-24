# Lost in the Middle harness, first run (2026-11-24)

Rebuilds the Liu et al. test from scratch. Paper:
https://arxiv.org/abs/2307.03172

## Setup

- 12 questions, invented facts, in `data/golden.jsonl`. The
  model cannot answer from pretraining; it has to read the
  context.
- Each question: 1 gold document holding the answer, 8
  distractor documents about similar invented entities.
  All documents 30-70 words, length ratio under 2x in every
  case, so length is not a cue.
- Each question runs three times: gold document at the start,
  the middle, and the end of 9 documents.
- Model: Qwen/Qwen2.5-0.5B-Instruct, local, greedy decoding.
- Scoring: case-insensitive substring match on the answer.

## Results (sandbox, 12 questions x 3 positions)

- start: 12/12 (1.000)
- middle: 9/12 (0.750)
- end: 11/12 (0.917)

Reproduced on a MacBook Air, 2026-11-24: identical results,
start 12/12, middle 9/12, end 11/12.

The middle loses. All three middle misses picked the wrong
document's answer: q04 answered Petra Lindqvist instead of
Elena Voss, q06 answered Mount Brannock instead of Mount
Soren, q07 answered Migraines instead of sleeplessness. q07
also missed at the end with the same wrong answer.

## The scorer bug, plainly

The first scoring pass reported start 9/12, middle 9/12,
end 10/12. That was wrong. The scorer required the full
answer string including the article "the", so four correct
replies were marked wrong: "Voss River" for "the Voss river"
(twice), "cello" for "the cello", "White tern" for "the white
tern". The fix strips one leading article from the answer
before matching. The same 36 replies were re-scored with
the fixed scorer; no new model runs. Corrected numbers are
the ones above.

## Honest limits

- n=12 is small. Three misses is a real signal, not a proof.
- The model is 0.5B, far smaller than the models in the paper.
- The context is 9 documents, about 600 tokens, much shorter
  than the paper's long contexts. The effect may grow with
  longer contexts.
- The facts are synthetic. Real documents may behave
  differently.

Full per-case log: `runs/results.jsonl`.
