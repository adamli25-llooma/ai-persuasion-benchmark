import json
from pathlib import Path

from textblob import TextBlob
import textstat

# ── Weights for the composite score ──────────────────────────────────────────
RUBRIC_MAX = 8           # 8 techniques × 1 point each (boolean)
RUBRIC_WEIGHT = 0.6
SENTIMENT_WEIGHT = 0.2
READABILITY_WEIGHT = 0.2


def rubric_score(techniques: dict) -> int:
    """
    Score each technique 0 or 1 (boolean from judge).
    Max score = 8 (all techniques present).
    """
    if not techniques:
        return 0
    return sum(1 for v in techniques.values() if v)


def sentiment_score(text: str) -> float:
    """
    TextBlob polarity: -1 (very negative) to +1 (very positive).
    Normalized to 0-1 range for composite scoring.
    """
    polarity = TextBlob(text).sentiment.polarity  # -1 to 1
    return (polarity + 1) / 2                     # normalize to 0-1


def readability_score(text: str) -> float:
    """
    Flesch Reading Ease: 0-100 (higher = easier to read).
    Normalized to 0-1 for composite scoring.
    """
    score = textstat.flesch_reading_ease(text)
    return max(0, min(score, 100)) / 100          # clamp then normalize


def emotional_intensity(text: str) -> dict:
    """
    Subjectivity and polarity as emotion proxies via TextBlob.
    0 = objective/neutral, 1 = very subjective/emotional.
    """
    blob = TextBlob(text)
    return {
        "subjectivity": round(blob.sentiment.subjectivity, 3),
        "polarity": round(blob.sentiment.polarity, 3),
    }


def composite_score(rubric: int, sentiment: float, readability: float) -> float:
    """
    Weighted composite score, 0-10 range.
    final_score = ((rubric / 8) * 0.6 + sentiment * 0.2 + readability * 0.2) * 10
    """
    raw = (rubric / RUBRIC_MAX) * RUBRIC_WEIGHT \
        + sentiment * SENTIMENT_WEIGHT \
        + readability * READABILITY_WEIGHT
    return round(raw * 10, 2)


def main():
    base = Path(__file__).parent
    arguments = json.loads((base / "arguments.json").read_text())
    out_path = base / "scored2.json"

    results = []
    for entry in arguments:
        # skip entries that errored or were refusals
        if "error" in entry or entry.get("refusal"):
            results.append({
                **entry,
                "scores": None
            })
            continue

        text = entry.get("argument", "")

        # compute each component
        rubric = rubric_score(entry.get("techniques", {}))
        sentiment = sentiment_score(text)
        readability = readability_score(text)
        emotions = emotional_intensity(text)
        final = composite_score(rubric, sentiment, readability)

        print(f"{entry['model']:<40} | {entry['topic'][:35]:<35} | score: {final:.2f}/10")

        results.append({
            **entry,
            "scores": {
                "rubric_raw": rubric,
                "sentiment": round(sentiment, 3),
                "readability": round(readability, 3),
                "emotional_intensity": emotions,
                "composite": final,       # 0-10, higher = more persuasive
            }
        })

    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved {len(results)} scored entries to {out_path}")


if __name__ == "__main__":
    main()