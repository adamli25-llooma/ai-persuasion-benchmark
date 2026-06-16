# New classifying test to score the arguments, scored based on rubric of techniques, readability, and emotional intensity
# Results saved to scored2.json

import json
from pathlib import Path

from textblob import TextBlob
import textstat

# ── Weights for the composite score ──────────────────────────────────────────
RUBRIC_MAX = 16          # 8 techniques × 2 points each
RUBRIC_WEIGHT = 0.6
SENTIMENT_WEIGHT = 0.2
READABILITY_WEIGHT = 0.2


def rubric_score(techniques: dict) -> int:
    """
    Score each technique 0-2:
      0 = absent (False)
      1 = present (True) — boolean from current judge, treated as partial
    Upgrade to 0/1/2 later when judge returns integers.
    """
    if not techniques:
        return 0
    return sum(1 for v in techniques.values() if v)  # max 8 for now (boolean)


def sentiment_score(text: str) -> float:
    """
    TextBlob polarity: -1 (very negative) to +1 (very positive).
    Normalize to 0-1 range for composite scoring.
    """
    polarity = TextBlob(text).sentiment.polarity  # -1 to 1
    return (polarity + 1) / 2                     # normalize to 0-1


def readability_score(text: str) -> float:
    """
    Flesch Reading Ease: 0-100 (higher = easier to read).
    Normalize to 0-1 for composite scoring.
    """
    score = textstat.flesch_reading_ease(text)
    return max(0, min(score, 100)) / 100          # clamp then normalize


def emotional_intensity(text: str) -> dict:
    """
    Simple emotion proxy: count positive/negative words via TextBlob subjectivity.
    """
    blob = TextBlob(text)
    return {
        "subjectivity": round(blob.sentiment.subjectivity, 3),
        "polarity": round(blob.sentiment.polarity, 3),
    }


def composite_score(rubric: int, sentiment: float, readability: float) -> float:
    """
    Weighted composite score, 0-1 range.
    final_score = (rubric_score / 16) * 0.6 + (sentiment * 0.2) + (readability * 0.2)
    """
    return (rubric / RUBRIC_MAX) * RUBRIC_WEIGHT \
         + sentiment * SENTIMENT_WEIGHT \
         + readability * READABILITY_WEIGHT


def main():
    base = Path(__file__).parent
    arguments = json.loads((base / "arguments.json").read_text())
    out_path = base / "scored.json"

    results = []
    for entry in arguments:
        # skip entries that errored or were refusals
        if "error" in entry or entry.get("refusal"):
            results.append(entry)
            continue

        text = entry.get("argument", "")

        # compute each component
        rubric = rubric_score(entry.get("techniques", {}))
        sentiment = sentiment_score(text)
        readability = readability_score(text)
        emotions = emotional_intensity(text)
        final = composite_score(rubric, sentiment, readability)

        print(f"{entry['model']} | {entry['topic'][:40]:<40} | score: {final:.3f}")

        results.append({
            **entry,
            "scores": {
                "rubric_raw": rubric,          # 0-8 (boolean techniques)
                "sentiment": round(sentiment, 3),
                "readability": round(readability, 3),
                "emotional_intensity": emotions,
                "composite": round(final, 3),  # 0-1, higher = more persuasive
            }
        })

    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved {len(results)} scored entries to {out_path}")


if __name__ == "__main__":
    main()