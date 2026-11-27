"""Lost in the Middle harness, v1.

Rebuilds the Liu et al. test from scratch: same question, same
documents, the answer document moved from the start to the middle
to the end. Measures accuracy by answer position.

The facts are invented, so the model cannot answer from
pretraining. It has to read the context. Scoring is a plain
substring match on the answer, no LLM judge.

Model: Qwen/Qwen2.5-0.5B-Instruct, local, greedy decoding.
No API key, no paid service.

Run: .venv/bin/python harness.py [--smoke] [--questions N]
Writes runs/results.jsonl.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parent
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
POSITIONS = ["start", "middle", "end"]


def load_data(path: Path = ROOT / "data" / "golden.jsonl"):
    return [json.loads(line) for line in open(path)]


def order_docs(case, position, n_docs=9):
    """Gold doc at the start, middle, or end of the document list."""
    docs = list(case["distractors"][: n_docs - 1])
    idx = {"start": 0, "middle": len(docs) // 2, "end": len(docs)}[position]
    docs.insert(idx, case["gold_doc"])
    return docs


def build_messages(question, docs, prompt="direct"):
    numbered = "\n\n".join(
        f"Document {i + 1}:\n{d}" for i, d in enumerate(docs)
    )
    if prompt == "quote":
        system = (
            "Answer the question using only the documents "
            "below. First, quote the one document that answers "
            "the question. Then give the answer on a line "
            "starting with 'Answer:'."
        )
    else:
        system = (
            "Answer the question using only the documents "
            "below. Reply with the answer only."
        )
    return [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": f"{numbered}\n\nQuestion: {question}",
        },
    ]


def load_model(model_id=MODEL_ID):
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, dtype=torch.float32
    )
    model.eval()
    return tok, model


def run_case(tok, model, question, docs, max_new_tokens=40, prompt="direct"):
    messages = build_messages(question, docs, prompt)
    text = tok.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tok(text, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tok.eos_token_id,
        )
    reply = tok.decode(
        out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
    )
    return reply.strip()


def final_answer(reply):
    """Text after the 'Answer:' line, if the model gave one.

    The quote prompt asks the model to quote a document first.
    Scoring the whole reply would count a correct quote as a
    correct answer even if the final answer is wrong, so the
    scorer measures the final answer only. Falls back to the
    whole reply when no Answer: line is present.
    """
    idx = reply.lower().find("answer:")
    if idx == -1:
        return reply
    return reply[idx + len("answer:"):]


def score(reply, answer):
    """Case-insensitive substring match, ignoring a leading article.

    The model often answers "cello" when the gold answer is
    "the cello". That is correct, and the first scorer marked it
    wrong. Strip one leading article from the answer before
    matching.
    """
    core = answer.lower()
    for article in ("the ", "a ", "an "):
        if core.startswith(article):
            core = core[len(article) :]
            break
    return core in final_answer(reply).lower()


def evaluate(tok, model, cases, out_path, n_docs=9, prompt="direct"):
    max_tokens = 120 if prompt == "quote" else 40
    results = []
    for case in cases:
        for position in POSITIONS:
            docs = order_docs(case, position, n_docs)
            reply = run_case(
                tok, model, case["question"], docs,
                max_new_tokens=max_tokens, prompt=prompt,
            )
            correct = score(reply, case["answer"])
            results.append(
                {
                    "id": case["id"],
                    "position": position,
                    "prompt": prompt,
                    "question": case["question"],
                    "answer": case["answer"],
                    "reply": reply,
                    "correct": correct,
                }
            )
            print(
                f"{case['id']} {position:6s} "
                f"{'OK ' if correct else 'MISS'} {reply!r}"
            )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"\nwrote {out_path}")
    for position in POSITIONS:
        subset = [r for r in results if r["position"] == position]
        acc = sum(r["correct"] for r in subset) / len(subset)
        print(f"{position:6s} accuracy {acc:.3f} "
              f"({sum(r['correct'] for r in subset)}/{len(subset)})")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL_ID)
    parser.add_argument("--questions", type=int, default=None)
    parser.add_argument("--num-docs", type=int, default=9)
    parser.add_argument("--prompt", choices=["direct", "quote"],
                        default="direct")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--out", default=None)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()

    torch.set_num_threads(args.threads)
    cases = load_data()
    if args.smoke:
        cases = cases[:1]
    elif args.questions:
        cases = cases[: args.questions]
    print(f"loaded {len(cases)} questions, model {args.model}, "
          f"{args.num_docs} docs, prompt {args.prompt}")
    tok, model = load_model(args.model)
    out = args.out
    if out is None:
        base = (f"results-{args.num_docs}docs"
                if args.num_docs != 9 else "results")
        if args.prompt != "direct":
            base += f"-{args.prompt}"
        out = f"runs/{base}.jsonl"
    evaluate(tok, model, cases, ROOT / out, args.num_docs, args.prompt)


if __name__ == "__main__":
    main()
