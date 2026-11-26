# Lost in the Middle, 20 documents (2026-11-25)

Follow-up to the 9-document run in
`docs/lostinthemiddle_2026-11-24.md`. Same 12 questions, same
model, one variable changed: 20 documents instead of 9, about
1,300 tokens instead of 600.

## Setup

- Dataset extended: each question now has 19 distractors
  instead of 8, same topic family, all documents 30-70 words,
  length ratio under 2x in every case.
- Gold document at index 0 (start), 10 (middle), or 19 (end).
- Model: Qwen/Qwen2.5-0.5B-Instruct, local, greedy decoding.
- Scoring: substring match, ignoring a leading article.

## Results (sandbox, 12 questions x 3 positions)

- start: 12/12 (1.000)
- middle: 6/12 (0.500)
- end: 11/12 (0.917)

Reproduced on a MacBook Air, 2026-11-25: identical results,
start 12/12, middle 6/12, end 11/12.

Against the 9-document run (start 12/12, middle 9/12,
end 11/12): the start and end did not move at all. The
middle fell from 9 to 6.

## The misses

All six middle misses picked the wrong document's answer:
q01 answered plasma cells instead of crystallized helium,
q05 answered bright yellow instead of crimson, q07 answered
Migraines instead of sleeplessness, q08 answered bassoon
instead of cello, q09 answered Dunmore instead of Karn,
q11 answered 1879 instead of 1876. q01 also missed at the
end, answering solid rocket boosters, another fleet's fuel.

## Honest limits

- n=12 is small. The direction is consistent with the paper,
  but six misses is a signal, not a proof.
- The model is 0.5B, far smaller than the models in the paper.
- The facts are synthetic. Real documents may behave
  differently.

Full per-case log: `runs/results-20docs.jsonl`.
