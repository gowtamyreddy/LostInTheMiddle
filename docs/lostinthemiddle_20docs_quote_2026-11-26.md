# Lost in the Middle, quote-first prompt (2026-11-26)

Follow-up to the 20-document run in
`docs/lostinthemiddle_20docs_2026-11-25.md`. Same 12
questions, same 20 documents, same model, one variable
changed: the prompt now asks the model to quote the one
document that answers the question, then give the answer
on a line starting with 'Answer:'.

## Setup

- System prompt: quote the supporting document first, then
  'Answer: ...'. Generation allowance raised to 120 tokens
  so the quote fits.
- Scoring measures the final answer only, the text after
  the 'Answer:' line. Scoring the whole reply would count a
  correct quote as a correct answer even when the final
  answer is wrong. Falls back to the whole reply when no
  Answer: line is present.

## Results (sandbox, 12 questions x 3 positions)

- start: 12/12 (1.000)
- middle: 7/12 (0.583)
- end: 11/12 (0.917)

Reproduced on a MacBook Air, 2026-11-26: identical results,
start 12/12, middle 7/12, end 11/12.

Against the direct prompt at 20 documents (start 12/12,
middle 6/12, end 11/12): the start and end did not move.
The middle went from 6 to 7.

## What changed, question by question

- Fixed at the middle: q07 (sleeplessness) and q08 (cello),
  both missed with the direct prompt.
- Flipped the other way: q10 (bronze), correct with the
  direct prompt, now answers Lead at the middle.
- Still missing at the middle: q01 (plasma cells), q05
  (white sails with an orange stripe), q09 (Stonebridge),
  q11 (1879). q01 still misses at the end too, answering
  solid rocket boosters.
- Format: 35 of 36 replies had an Answer: line. The one
  without was q01 at the middle.

## Honest limits

- n=12 is small. A move of one question is within noise.
  This is not evidence the fix works, and not evidence it
  does not. It is evidence the fix does not fix the middle
  for this model at this size.
- The model is 0.5B. A bigger model may follow the quote
  instruction more reliably.
- The facts are synthetic. Real documents may behave
  differently.

Full per-case log: `runs/results-20docs-quote.jsonl`.
