# Text-to-Speech Converter

A Python script for converting text to speech using Silero TTS models. Supports English (`en`) and Russian (`ru`) with
male and female voices. Generates MP3 output from text input via file or STDIN.

## Features

- Multi-language support (English, Russian)
- GPU acceleration (CUDA/ROCm) with fallback to CPU
- Text preprocessing (number conversion, transliteration)
- Chunked processing for long texts
- Temporary file cleanup

## Prerequisites

- Python 3.12+
- `uv` package manager (`pip install uv`)
- FFmpeg (for audio processing)
- NVIDIA or AMD GPU drivers (optional, for GPU acceleration)

## Installation

1. **Install dependencies**:
   ```bash
   # Clone repository
   git clone https://github.com/your-repository/text-to-speech-converter.git
   cd python-tts-converter
   # Sync base dependencies
   uv sync
   ```

2. **Install PyTorch** (choose appropriate command for your hardware):

   ```bash
   # For NVIDIA GPUs
   uv pip install torch
   # or
   # For AMD GPUs
   uv pip install torch --index-url https://download.pytorch.org/whl/rocm6.3
   # or
   # For CPU only
   uv pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Download Silero Models**:
   ```bash
   mkdir -p models
   # Russian model
   wget https://models.silero.ai/models/tts/ru/ru_v3.pt -O models/ru_v3.pt
   # English model
   wget https://models.silero.ai/models/tts/en/v3_en.pt -O models/v3_en.pt
   ```

## Usage

### Basic Command

```bash
source .venv/bin/activate
python tts.py --input input.txt --output speech.mp3
```

### Options

| Option            | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `-i, --input`     | Input text file (optional - uses STDIN if not specified)                    |
| `-o, --output`    | Output MP3 file path (required)                                             |
| `-c, --cache-dir` | Temporary directory for processing (default: system temp)                   |
| `-l, --language`  | Language: `ru` (Russian) or `en` (English) [default: ru]                    |
| `-s, --speaker`   | Speaker gender: `male` or `female` [default: female]                        |
| `-d, --device`    | PyTorch device: `cuda`, `cpu`, or specific device [default: cuda]           |

### Examples

1. **Text file to speech**:
   ```bash
   python tts.py -i novel.txt -o audiobook.mp3 -l en -s male
   ```

2. **Pipe text from STDIN**:
   ```bash
   echo "Привет мир! 12345" | python tts.py -o greeting.mp3 -l ru
   ```

3. **CPU processing**:
   ```bash
   python tts.py -i input.txt -o output.mp3 --device cpu
   ```

## Notes

- First run may take longer due to model initialization
- Temporary files are automatically cleaned up after processing
- Numbers are converted to words
- Input text is automatically transliterated to appropriate script (Cyrillic/Latin)
- Requires FFmpeg in system PATH for MP3 support

## Troubleshooting

**No GPU Acceleration**:
- Use `--device cpu` for CPU-only processing
- Verify PyTorch installation with `python -c "import torch; print(torch.cuda.is_available())"`

**Audio Quality Issues**:
- Ensure text contains only supported characters: letters, numbers, and basic punctuation
- Check for proper text encoding in input files (UTF-8 recommended)

**Model Loading Errors**:
- Verify model files are in `models/` directory
- Check file permissions for model files

## License

Source code is primarily distributed under the terms of the MIT license. See LICENSE for details.
