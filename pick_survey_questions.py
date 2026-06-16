# Pick the best survey questions to judge
# Results saved to survey_questions.json

import json
from pathlib import Path
from collections import defaultdict

# ── How we define "best" questions ───────────────────────────────────────────
# 1. One question per category (balanced representation)
# 2. Pick the question where models disagreed most (highest variance in composite score)
# 3. Prefer questions where all 3 models responded (no errors/refusals)

MODELS = [
    "openai/gpt-5.4-mini",
    "anthropic/claude-haiku-4.5",
    "google/gemini-3.1-flash-lite-preview",
]

TARGET = 5  # number of questions to pick


def main():
    base = Path(__file__).parent
    scored = json.loads((base / "scored2.json").read_text())

    # ── Group by topic ────────────────────────────────────────────────────────
    by_topic = defaultdict(list)
    for entry in scored:
        if entry.get("scores") and not entry.get("refusal") and "error" not in entry:
            by_topic[entry["topic"]].append(entry)

    # ── Filter to topics where all 3 models responded ─────────────────────────
    complete_topics = {
        topic: entries
        for topic, entries in by_topic.items()
        if len(entries) == 3
    }

    print(f"Found {len(complete_topics)} topics with all 3 model responses\n")

    # ── Score each topic by variance in composite scores ──────────────────────
    # High variance = models disagreed = more interesting for humans to judge
    topic_stats = []
    for topic, entries in complete_topics.items():
        scores = [e["scores"]["composite"] for e in entries]
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        category = entries[0]["category"]
        topic_stats.append({
            "topic": topic,
            "category": category,
            "entries": entries,
            "mean_score": round(mean, 2),
            "variance": round(variance, 4),
            "scores": scores,
        })

    # ── Pick best 5: one per category first, then fill by variance ────────────
    picked = []
    used_categories = set()

    # Pass 1: pick highest-variance topic from each category
    for category in ["silly", "niche", "proven_false", "bad_life_advice"]:
        category_topics = [t for t in topic_stats if t["category"] == category]
        if not category_topics:
            continue
        best = max(category_topics, key=lambda t: t["variance"])
        picked.append(best)
        used_categories.add(category)
        if len(picked) == TARGET:
            break

    # Pass 2: fill remaining slots with highest variance overall
    if len(picked) < TARGET:
        remaining = [t for t in topic_stats if t not in picked]
        remaining.sort(key=lambda t: t["variance"], reverse=True)
        for t in remaining:
            if len(picked) == TARGET:
                break
            picked.append(t)

    # ── Print summary ─────────────────────────────────────────────────────────
    print(f"{'='*70}")
    print(f"TOP {TARGET} QUESTIONS FOR HUMAN SURVEY")
    print(f"{'='*70}\n")

    survey_data = []
    for i, t in enumerate(picked, 1):
        print(f"Q{i} [{t['category']}] {t['topic']}")
        print(f"     variance: {t['variance']}  |  scores: {t['scores']}\n")

        question_entry = {
            "question_number": i,
            "topic": t["topic"],
            "category": t["category"],
            "variance": t["variance"],
            "responses": []
        }

        for entry in sorted(t["entries"], key=lambda e: e["model"]):
            print(f"  [{entry['model']}]")
            print(f"  score: {entry['scores']['composite']}/10")
            print(f"  {entry['argument'][:120]}...")
            print()
            question_entry["responses"].append({
                "model": entry["model"],
                "argument": entry["argument"],
                "composite_score": entry["scores"]["composite"],
            })

        survey_data.append(question_entry)

    # ── Save to survey_questions.json ─────────────────────────────────────────
    out_path = base / "survey_questions.json"
    out_path.write_text(json.dumps(survey_data, indent=2))
    print(f"\nSaved survey questions to {out_path}")


if __name__ == "__main__":
    main()