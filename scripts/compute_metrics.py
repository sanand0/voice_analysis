import json
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_CSV = BASE_DIR / "reports" / "results_raw.csv"
METRICS_MD = BASE_DIR / "reports" / "metrics_summary.md"

FEATURES = [
    "num_speakers",
    "customer_gender",
    "customer_speaking_rate",
    "customer_volume",
    "customer_main_emotion",
    "customer_emotion_intensity",
    "customer_sentiment",
    "background_noise",
    "agent_politeness",
    "agent_confidence",
    "escalation_risk",
    "call_outcome_signal"
]

def create_markdown_table(metrics):
    """
    Create a markdown table from metrics data.
    """
    if not metrics:
        return "No metrics data available."
    
    # Header
    markdown = "# Audio Analysis Metrics Summary\n\n"
    markdown += "| Feature | Total Samples | Correct | Accuracy |\n"
    markdown += "|---------|---------------|---------|----------|\n"
    
    # Rows
    for metric in metrics:
        feature = metric["feature"]
        total = metric["total_samples"]
        correct = metric["correct"]
        accuracy = f"{metric['accuracy']:.3f}"
        
        markdown += f"| {feature} | {total} | {correct} | {accuracy} |\n"
    
    # Summary statistics
    total_samples = sum(m["total_samples"] for m in metrics)
    total_correct = sum(m["correct"] for m in metrics)
    overall_accuracy = total_correct / total_samples if total_samples > 0 else 0
    
    markdown += "\n## Summary\n\n"
    markdown += f"- **Total Samples**: {total_samples}\n"
    markdown += f"- **Total Correct**: {total_correct}\n"
    markdown += f"- **Overall Accuracy**: {overall_accuracy:.3f}\n"
    markdown += f"- **Features Analyzed**: {len(metrics)}\n"
    
    return markdown

def main():
    if not RESULTS_CSV.exists():
        raise FileNotFoundError(f"{RESULTS_CSV} not found. Run run_experiments.py first.")

    df = pd.read_csv(RESULTS_CSV)

    metrics = []

    for feat in FEATURES:
        correct = 0
        total = 0

        for _, row in df.iterrows():
            truth = json.loads(row["truth"])
            pred = json.loads(row["pred"])

            if feat not in truth or feat not in pred:
                continue

            if truth[feat] == pred[feat]:
                correct += 1
            total += 1

        if total == 0:
            continue

        accuracy = correct / total
        metrics.append({
            "feature": feat,
            "total_samples": total,
            "correct": correct,
            "accuracy": accuracy
        })

    # Create markdown content
    markdown_content = create_markdown_table(metrics)
    
    # Ensure the directory exists
    METRICS_MD.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to markdown file
    with open(METRICS_MD, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    # Print to console (optional - you can remove this if you don't want console output)
    mdf = pd.DataFrame(metrics)
    print(mdf)
    print(f"\nSaved metrics to {METRICS_MD}")

if __name__ == "__main__":
    main()