import json
from pathlib import Path
from collections import defaultdict

def main():
    base = Path(__file__).parent
    survey = json.loads((base / "survey_questions.json").read_text())
    arguments = json.loads((base / "arguments.json").read_text())

    # ── Build lookup: (model, topic) -> techniques + scores ──────────────────
    technique_lookup = {}
    for entry in arguments:
        if entry.get("techniques"):
            key = (entry["model"], entry["topic"])
            technique_lookup[key] = entry["techniques"]

    TECHNIQUES = [
        "ethos", "logos", "pathos", "reciprocity",
        "commitment_and_consistency", "social_proof",
        "authority", "liking", "scarcity"
    ]

    # ── Flatten survey responses ──────────────────────────────────────────────
    all_responses = []
    for question in survey:
        for response in question["responses"]:
            topic = response.get("topic", question["topic"])
            all_responses.append({
                "question_number": question["question_number"],
                "question_topic": question["topic"],
                "topic": topic,
                "category": question["category"],
                "model": response["model"],
                "composite_score": response["composite_score"],
            })

    print(f"Analyzing {len(all_responses)} responses across {len(survey)} survey questions\n")

    # ── Per-model technique frequency ─────────────────────────────────────────
    model_techniques = defaultdict(lambda: defaultdict(int))
    model_counts = defaultdict(int)
    model_scores = defaultdict(list)

    for r in all_responses:
        key = (r["model"], r["topic"])
        techniques = technique_lookup.get(key, {})
        model_counts[r["model"]] += 1
        model_scores[r["model"]].append(r["composite_score"])
        for t in TECHNIQUES:
            if techniques.get(t):
                model_techniques[r["model"]][t] += 1

    print("=" * 70)
    print("TECHNIQUE USAGE BY MODEL")
    print("=" * 70)
    for model, counts in model_techniques.items():
        short_name = model.split("/")[-1]
        avg_score = sum(model_scores[model]) / len(model_scores[model])
        total = model_counts[model]
        print(f"\n{short_name} (avg score: {avg_score:.2f}, n={total})")
        print("-" * 50)
        for t in TECHNIQUES:
            count = counts[t]
            pct = (count / total) * 100 if total else 0
            bar = "█" * int(pct / 5)
            print(f"  {t:<30} {bar:<20} {count}/{total} ({pct:.0f}%)")

    # ── Per-category technique usage ──────────────────────────────────────────
    print("\n" + "=" * 70)
    print("TECHNIQUE USAGE BY CATEGORY")
    print("=" * 70)
    category_techniques = defaultdict(lambda: defaultdict(int))
    category_counts = defaultdict(int)
    category_scores = defaultdict(list)

    for r in all_responses:
        key = (r["model"], r["topic"])
        techniques = technique_lookup.get(key, {})
        category_counts[r["category"]] += 1
        category_scores[r["category"]].append(r["composite_score"])
        for t in TECHNIQUES:
            if techniques.get(t):
                category_techniques[r["category"]][t] += 1

    for category, counts in category_techniques.items():
        avg_score = sum(category_scores[category]) / len(category_scores[category])
        total = category_counts[category]
        print(f"\n{category} (avg score: {avg_score:.2f}, n={total})")
        print("-" * 50)
        for t in TECHNIQUES:
            count = counts[t]
            pct = (count / total) * 100 if total else 0
            bar = "█" * int(pct / 5)
            print(f"  {t:<30} {bar:<20} {count}/{total} ({pct:.0f}%)")

    # ── Technique correlation with score ──────────────────────────────────────
    print("\n" + "=" * 70)
    print("TECHNIQUE CORRELATION WITH COMPOSITE SCORE")
    print("=" * 70)
    technique_scores_with = defaultdict(list)
    technique_scores_without = defaultdict(list)

    for r in all_responses:
        key = (r["model"], r["topic"])
        techniques = technique_lookup.get(key, {})
        for t in TECHNIQUES:
            if techniques.get(t):
                technique_scores_with[t].append(r["composite_score"])
            else:
                technique_scores_without[t].append(r["composite_score"])

    print(f"\n{'Technique':<30} {'With':>8} {'Without':>10} {'Diff':>8}")
    print("-" * 60)
    diffs = []
    for t in TECHNIQUES:
        with_scores = technique_scores_with[t]
        without_scores = technique_scores_without[t]
        avg_with = sum(with_scores) / len(with_scores) if with_scores else 0
        avg_without = sum(without_scores) / len(without_scores) if without_scores else 0
        diff = avg_with - avg_without
        diffs.append((t, avg_with, avg_without, diff))

    for t, avg_with, avg_without, diff in sorted(diffs, key=lambda x: x[3], reverse=True):
        sign = "+" if diff > 0 else ""
        print(f"  {t:<28} {avg_with:>8.2f} {avg_without:>10.2f} {sign}{diff:>7.2f}")

     # ── Save full analysis with arguments included ─────────────────────────────
    full_out = {
        "summary": {
            "total_responses": len(all_responses),
            "total_questions": len(survey),
        },
        "model_technique_usage": {m: dict(c) for m, c in model_techniques.items()},
        "model_avg_scores": {m: round(sum(s)/len(s), 2) for m, s in model_scores.items()},
        "category_technique_usage": {c: dict(t) for c, t in category_techniques.items()},
        "technique_score_correlation": {
            t: {"avg_with": round(aw, 2), "avg_without": round(awo, 2), "diff": round(d, 2)}
            for t, aw, awo, d in diffs
        },
        "per_response_breakdown": [
            {
                "question_number": r["question_number"],
                "topic": r["topic"],
                "category": r["category"],
                "model": r["model"],
                "composite_score": r["composite_score"],
                "techniques_used": {
                    t: technique_lookup.get((r["model"], r["topic"]), {}).get(t, False)
                    for t in TECHNIQUES
                }
            }
            for r in all_responses
        ]
    }

    out_path = base / "analysis.json"
    out_path.write_text(json.dumps(full_out, indent=2))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()