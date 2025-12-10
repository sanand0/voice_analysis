import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"
LABELS_PATH = BASE_DIR / "labels" / "labels.jsonl"

# Allowed values consistent with your prompt/config
DEFAULT_LABELS = {
    "num_speakers": 2,
    "roles_detected": ["agent", "customer"],
    "customer_gender": "unknown",
    "customer_speaking_rate": "normal",
    "customer_volume": "normal",
    "customer_main_emotion": "neutral",
    "customer_emotion_intensity": "medium",
    "customer_sentiment": "neutral",
    "interruptions_by_agent": 0,
    "background_noise": "medium",
    "agent_politeness": "neutral",
    "agent_confidence": "medium",
    "escalation_risk": "medium",
    "call_outcome_signal": "unclear"
}

AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


def load_existing_files():
    existing = set()
    if not LABELS_PATH.exists():
        return existing

    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            existing.add(obj["file"])
    return existing


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LABELS_PATH.parent.mkdir(parents=True, exist_ok=True)

    existing = load_existing_files()

    # Find all audio files directly under data/raw
    audio_files = [
        p for p in DATA_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in AUDIO_EXTS
    ]

    new_lines = []
    for audio_path in audio_files:
        rel_name = audio_path.name  # no subdirs, just filename
        if rel_name in existing:
            continue

        obj = {
            "file": rel_name,
            "labels": DEFAULT_LABELS.copy()
        }
        new_lines.append(obj)

    if not new_lines:
        print("No new audio files to add to labels.jsonl")
        return

    with open(LABELS_PATH, "a", encoding="utf-8") as f:
        for obj in new_lines:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(f"Added {len(new_lines)} new label entries to {LABELS_PATH}")


if __name__ == "__main__":
    main()
