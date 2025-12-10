import json
import os
import requests
from pathlib import Path
import pandas as pd
import base64

# Configuration
MODEL_NAME = "openai/gpt-5.1"  # or your preferred OpenRouter model
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"
LABELS_PATH = BASE_DIR / "labels" / "labels.jsonl"
PROMPT_PATH = BASE_DIR / "config" / "prompt.txt"
RESULTS_CSV = BASE_DIR / "reports" / "results_raw.csv"
JSON_OUTPUT_DIR = BASE_DIR / "reports" / "json"

# OpenRouter configuration
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://llmfoundry.straive.com/openrouter/v1/chat/completions"

def get_openrouter_headers():
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Environment variable OPENROUTER_API_KEY is not set.")
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",  # Optional: Your app's URL
        "X-Title": "Audio Analysis App"  # Optional: Your app's name
    }

def load_labels():
    labels = {}
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            labels[obj["file"]] = obj["labels"]
    return labels

def encode_audio_to_base64(audio_path: Path) -> str:
    """
    Encode audio file to base64 string for API transmission.
    """
    with open(audio_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode('utf-8')

def analyze_clip(audio_path: Path, prompt: str) -> dict:
    """
    Send audio file to OpenRouter API and return the parsed JSON prediction.
    """
    # Encode audio to base64
    audio_base64 = encode_audio_to_base64(audio_path)
    
    # Get file extension for MIME type
    file_ext = audio_path.suffix.lower()
    mime_type = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4',
        '.flac': 'audio/flac',
        '.ogg': 'audio/ogg'
    }.get(file_ext, 'audio/mpeg')
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "audio",
                        "audio": {
                            "data": audio_base64,
                            "format": mime_type
                        }
                    }
                ]
            }
        ]
    }
    
    headers = get_openrouter_headers()
    
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")
    
    response_data = response.json()
    
    if 'choices' not in response_data or not response_data['choices']:
        raise Exception(f"Invalid response format: {response_data}")
    
    raw_text = response_data['choices'][0]['message']['content']
    
    # Parse the JSON response
    try:
        parsed = json.loads(raw_text)
        return parsed
    except json.JSONDecodeError:
        # If response isn't valid JSON, try to extract JSON from the text
        import re
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            raise Exception(f"Could not parse JSON from response: {raw_text}")

def main():
    labels = load_labels()
    
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        prompt = f.read()
    
    rows = []
    
    # Create folder for JSON outputs
    JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for rel_path, truth in labels.items():
        audio_path = DATA_DIR / rel_path
        
        if not audio_path.exists():
            print(f"Missing audio file: {audio_path}")
            continue
        
        print(f"Processing {audio_path} ...")
        
        try:
            pred = analyze_clip(audio_path, prompt)
        except Exception as e:
            print(f"Error processing {audio_path}: {e}")
            continue
        
        # Save Gemini output JSON
        json_filename = rel_path.rsplit(".", 1)[0] + ".json"
        json_path = JSON_OUTPUT_DIR / json_filename
        
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(pred, jf, indent=2, ensure_ascii=False)
        
        print(f"Saved JSON → {json_path}")
        
        # Add row to CSV
        row = {
            "file": rel_path,
            "truth": json.dumps(truth, ensure_ascii=False),
            "pred": json.dumps(pred, ensure_ascii=False),
        }
        rows.append(row)
    
    # Save CSV
    df = pd.DataFrame(rows)
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_CSV, index=False)
    
    print(f"\nAll results saved to:")
    print(f"- CSV:  {RESULTS_CSV}")
    print(f"- JSON: {JSON_OUTPUT_DIR}")

if __name__ == "__main__":
    main()