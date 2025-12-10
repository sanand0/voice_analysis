from pathlib import Path
import sys
import os
import requests

# Project paths
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"

def generate_tts(
    text: str,
    out_name: str,
    voice: str = "coral",
    model: str = "gpt-4o-mini-tts",
    speed: float = 1.0,
) -> Path:
    """
    Generate speech audio from text using OpenAI TTS API and save it under data/raw.
    :param text: The text to speak.
    :param out_name: Output filename (e.g. 'rude_3.mp3'). If no extension, '.mp3' is added.
    :param voice: Supported voices: alloy, ash, ballad, coral, echo,
                  fable, nova, onyx, sage, shimmer, verse.
    :param model: TTS model name, typically 'gpt-4o-mini-tts'.
    :param speed: Playback speed multiplier (0.25 to 4.0, default 1.0).
    :return: Path to the saved audio file.
    """
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Environment variable OPENAI_API_KEY is not set.")
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / out_name
    if out_path.suffix == "":
        out_path = out_path.with_suffix(".mp3")
    
    print(f"[TTS] Generating audio for: {text!r}")
    print(f"[TTS] Model={model}, Voice={voice}, Speed={speed}")
    print(f"[TTS] Saving to: {out_path}")
    
    # Prepare the API request
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "speed": speed
    }
    
    # Make the request
    response = requests.post(url, headers=headers, json=payload)
    
    # Check if request was successful
    if response.status_code != 200:
        raise Exception(f"TTS API request failed: {response.status_code} - {response.text}")
    
    # Save the audio content to file
    with open(out_path, "wb") as f:
        f.write(response.content)
    
    print("[TTS] Done.")
    return out_path

def main():
    # Usage:
    #   python scripts/generate_tts.py "Some text" rude_3.mp3 coral 1.3
    # Or: python scripts/generate_tts.py (interactive)
    if len(sys.argv) >= 3:
        text = sys.argv[1]
        out_name = sys.argv[2]
        voice = sys.argv[3] if len(sys.argv) >= 4 else "coral"
        speed_str = sys.argv[4] if len(sys.argv) >= 5 else "1.0"
        try:
            speed = float(speed_str)
        except ValueError:
            print(f"Invalid speed '{speed_str}', defaulting to 1.0")
            speed = 1.0
    else:
        print('Usage: python scripts/generate_tts.py "text to speak" output_filename.mp3 [voice] [speed]')
        print("No/insufficient arguments provided; switching to interactive mode.\n")
        text = input("Enter the text to synthesize: ").strip()
        if not text:
            print("No text provided. Exiting.")
            return
        out_name = input("Enter output file name (e.g. rude_3.mp3): ").strip()
        if not out_name:
            out_name = "tts_sample_01.mp3"
        voice = input("Enter voice name (default 'coral'): ").strip() or "coral"
        speed_input = input("Enter speed (0.25–4.0, default 1.0): ").strip()
        speed = float(speed_input) if speed_input else 1.0
    
    generate_tts(text=text, out_name=out_name, voice=voice, speed=speed)

if __name__ == "__main__":
    main()