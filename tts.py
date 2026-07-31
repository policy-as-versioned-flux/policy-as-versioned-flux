#!/usr/bin/env python3
import sys
import requests
import subprocess
import os
import tempfile

def show_help():
    print("""TTS CLI - Generate speech from text using Qwen3 voice clone

Usage:
  tts.py "text to speak"           Speak text as arguments
  echo "text" | tts.py              Speak text from stdin
  tts.py "text" > output.wav        Save audio to file (pipes output)

Options:
  -h, --help                        Show this help message

The script uses voice cloning with the 'andy3' voice preset and connects to
the local Qwen3 TTS backend at http://localhost:7693

Examples:
  tts.py "hello there i am going to talk to you about policy"
  echo "Policy as versioned flux" | tts.py > policy.wav
  tts.py "intro text" | cat - other.wav > combined.wav
""")

def get_text():
    if '--help' in sys.argv or '-h' in sys.argv:
        show_help()
        sys.exit(0)

    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    elif len(sys.argv) > 1:
        return ' '.join(sys.argv[1:])
    else:
        print("Usage: tts.py 'text' or echo 'text' | tts.py", file=sys.stderr)
        print("Use --help for full documentation", file=sys.stderr)
        sys.exit(1)

def main():
    text = get_text()
    response = requests.post(
        'http://localhost:7693/api/qwen3/generate',
        json={"text": text, "mode": "clone", "voice_name": "andy3"}
    )
    response.raise_for_status()

    audio_url = response.json()['audio_url']
    audio = requests.get(f'http://localhost:7693{audio_url}').content

    if sys.stdout.isatty():
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio)
            temp = f.name
        try:
            subprocess.run(['afplay', temp], check=True)
        finally:
            os.unlink(temp)
    else:
        sys.stdout.buffer.write(audio)

if __name__ == '__main__':
    main()
