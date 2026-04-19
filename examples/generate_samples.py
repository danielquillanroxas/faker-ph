"""Generate 20 deterministically-seeded sample documents with gold PII spans.

Outputs (both committed to the repo so reviewers can inspect without installing):
    examples/rendered_samples.jsonl
    examples/gold_spans.jsonl

Run from repo root:
    python examples/generate_samples.py
"""
import json
from pathlib import Path

from faker_ph import ALL_TEMPLATES, FakerPH, render

OUT_DIR = Path(__file__).resolve().parent
N_DOCS = 20
BASE_SEED = 42


def main():
    rendered_path = OUT_DIR / "rendered_samples.jsonl"
    spans_path = OUT_DIR / "gold_spans.jsonl"

    with open(rendered_path, "w", encoding="utf-8") as rf, \
         open(spans_path, "w", encoding="utf-8") as sf:

        for i in range(N_DOCS):
            template = ALL_TEMPLATES[i % len(ALL_TEMPLATES)]
            # Per-doc reseed so each doc is deterministic and reproducible in isolation
            fake = FakerPH(seed=BASE_SEED + i * 7919)

            text, spans = render(template, fake, doc_id=f"example_{i:03d}")

            rf.write(json.dumps({
                "doc_id": f"example_{i:03d}",
                "doc_type": template["doc_type"],
                "seed": BASE_SEED + i * 7919,
                "text": text,
            }, ensure_ascii=False) + "\n")

            sf.write(json.dumps({
                "doc_id": f"example_{i:03d}",
                "spans": spans,
            }, ensure_ascii=False) + "\n")

    print(f"Wrote {N_DOCS} docs to:")
    print(f"  {rendered_path}")
    print(f"  {spans_path}")


if __name__ == "__main__":
    main()
