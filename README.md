# Voice Analysis Evaluation Pipeline

## Overview

This project evaluates **Gemini / OpenRouter audio understanding** by:

1. Generating synthetic audio using **OpenAI TTS**
2. Collecting real call samples (YouTube, TTS, etc.)
3. Labelling audio features manually (emotion, gender, noise…)
4. Running Gemini analysis on each audio file
5. Comparing model predictions vs. ground truth
6. Producing metrics & reports

This allows rapid testing of new attributes such as:

- Singing detection  
- Stutter / stammer  
- Background conversations  
- Coughing  
- Emotion intensity  
- Environment type (coffee shop, classroom, office)

---

## Prerequisites

### Install Python 3.10+
```bash
python --version
```

### Create a Virtual Environment
```bash
python -m venv .venv
```

Activate:

**Windows PowerShell**
```powershell
.\.venv\Scripts\Activate
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

### Install Dependencies
```
pip install openai requests pandas soundfile
```

### Export API Keys

**OpenAI TTS**
```powershell
$env:OPENAI_API_KEY="your-openai-key-here"
```

**OpenRouter**
```powershell
$env:OPENROUTER_API_KEY="your-openrouter-key-here"
```

---

## Project Structure

```
voice_analysis/
├── config/
│   ├── features.json
│   ├── prompt.txt
├── data/
│   └── raw/
├── labels/
│   └── labels.jsonl
├── reports/
│   ├── results_raw.csv
│   └── metrics_summary.csv
└── scripts/
    ├── generate_tts.py
    ├── init_labels_from_raw.py
    ├── run_experiments.py
    ├── compute_metrics.py
```

---

## Generate Synthetic Audio (TTS)

### Basic
```powershell
python scripts/generate_tts.py "Hello, how may I help you today?" greeting_1.mp3
```

### With Voice + Speed
```powershell
python scripts/generate_tts.py "I already called three times—why is this not fixed?" angry_fast_1.mp3 coral 1.4
```

---

## Auto-Generate Label Entries
```powershell
python scripts/init_labels_from_raw.py
```

Edit `labels.jsonl` and manually fill ground-truth labels.

---

## Run Gemini Analysis
```powershell
python scripts/run_experiments.py
```

Outputs → `reports/results_raw.csv`

---

## Compute Metrics
```powershell
python scripts/compute_metrics.py
```

Outputs → `reports/metrics_summary.csv`

---

## Workflow Summary

| Step | Command |
|------|---------|
| Generate TTS audio | `python scripts/generate_tts.py` |
| Detect new files | `python scripts/init_labels_from_raw.py` |
| Label manually | edit `labels.jsonl` |
| Run analysis | `python scripts/run_experiments.py` |
| Compute metrics | `python scripts/compute_metrics.py` |

---

## Future Extensions
To add a new feature:

1. Add to `config/features.json`  
2. Update `prompt.txt`  
3. Generate new TTS samples  
4. Label them  
5. Run pipeline again  

---

