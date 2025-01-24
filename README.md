# Text-to-Speech (TTS) Converter

This program is a command-line tool for converting text into speech and saving the output as an MP3 file. It supports
English and Russian languages and allows customization of voice and sample rate. The program is built using Python and
leverages the `speakerpy` library for speech synthesis.

## How It Works

The program reads text from a file or standard input (STDIN), synthesizes speech using a pre-configured model and
voice, and saves the result as an MP3 file. It supports the following features:

* *Language Support*: Currently supports Russian (ru) and English (en).

* *Voice Selection*: Allows choosing a specific voice for synthesis (e.g., xenia for Russian, en_5 for English).

* *Sample Rate Customization*: Supports multiple sample rates (8000, 16000, 24000, 48000 Hz) for the output audio.

* *Caching*: Uses a cache directory to store intermediate files, improving performance for repeated runs.

## Installation

To use this program, follow these steps:

```sh
# clone repository
git clone https://github.com/your-repository/text-to-speech-converter.git
cd python-tts-converter

# set up virtual environment
python -m venv venv
source venv/bin/activate # On Windows, use `venv\Scripts\activate`

# install dependencies
pip install -r requirements.txt
```

## Usage

To run the program, use the following command:

```sh
python tts.py --input source-text.txt --output output.mp3
```

The program accepts the following options:

* `-i`, `--input`: Path to the input text file. If not provided, text is read from STDIN.
* `-o`, `--output`: Path to the output MP3 file.
* `-l`, `--language`: Language for speech synthesis (ru for Russian, en for English).
* `-s`, `--speaker`: Voice for speech synthesis (e.g., xenia for Russian, en_5 for English).
* `-r`, `--sample-rate`: Sample rate for the output audio (8000, 16000, 24000, 48000 Hz).
* `-c`, `--cache-dir`: Directory for caching intermediate files.

## Examples

Convert Text from a File:

```sh
python tts.py -i input.txt -o output.mp3 -l ru -s xenia -r 24000
```

Convert Text from STDIN:

```sh
echo "Привет, мир!" | python tts.py -o output.mp3
```

## Notes

* Ensure the speakerpy library is properly configured and the required models are available.
* The program uses the system's temporary directory for caching by default. You can specify a custom cache directory using the -c option.
* Supported sample rates are 8000, 16000, 24000, and 48000 Hz. Higher sample rates result in better audio quality but larger file sizes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
