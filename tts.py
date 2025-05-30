import click
import collections
import os
import re
import sys
import tempfile
import torch

from num2words import num2words
from pydub import AudioSegment
from torch.package.package_importer import PackageImporter
from transliterate import translit

Speaker = collections.namedtuple("Speaker", ["language", "voice"])
TtsModel = collections.namedtuple("TtsModel",
                                  ["path", "speaker", "sample_rate"])

PATTERN_NUMBER = re.compile("\\d+")

LANGUAGE_MODELS = {
    Speaker("ru", "male"): TtsModel("models/ru_v3.pt", "aidar", 48000),
    Speaker("ru", "female"): TtsModel("models/ru_v3.pt", "xenia", 48000),
    Speaker("en", "male"): TtsModel("models/v3_en.pt", "en_2", 48000),
    Speaker("en", "female"): TtsModel("models/v3_en.pt", "en_5", 48000),
}

DELIMITER_GROUPS = [["\n"], [".", "!", "?"], [",", ":", ";"], [" "]]
CHUNK_PREFIX = "chunk-"
CHUNK_POSTFIX = ".wav"


def chunk_generator(text, chunk_length, delimiter_groups=DELIMITER_GROUPS):
    offset = 0
    text_length = len(text)

    def find_bound(left, right):
        for group in delimiter_groups:
            result = -1

            for delimiter in group:
                delimiter_len = len(delimiter)

                if left + delimiter_len > right:
                    continue

                position = text.rfind(delimiter, left, right)

                if position != -1:
                    result = max(result, position + delimiter_len)

            if result != -1:
                return result

        return -1

    while offset < text_length:
        remaining = text_length - offset

        if remaining <= chunk_length:
            chunk = text[offset:].strip()

            if chunk != "":
                yield chunk

            offset = text_length

            break

        right_bound = offset + chunk_length
        current_bound = find_bound(offset, right_bound)

        if current_bound != -1:
            chunk = text[offset:current_bound].strip()

            if chunk != "":
                yield chunk

            offset = current_bound
        else:
            chunk = text[offset:right_bound].strip()

            if chunk != "":
                yield chunk

            offset = right_bound


def remove_unicode(text):
    """
    Removes all characters from the input text that are not spaces, digits, alphabetic characters,
    or specific punctuation marks (., !, ?, ,, :, ;, -, ', \").

    Args:
        text (str): The input text from which to remove unwanted characters.

    Returns:
        str: The cleaned text with only allowed characters.
    """
    return "".join((c for c in text
                    if c.isspace() or c.isdigit() or c.isalpha()
                    or c in {".", "!", "?", ",", ":", ";", "-", "'", "\""}))


def convert_numbers(text, language):
    """
    Converts all numbers in the input text to their word representation in the specified language.

    Args:
        text (str): The input text containing numbers to be converted.
        language (str): The language code for the word representation of numbers (e.g., 'en' for English, 'ru' for Russian).

    Returns:
        str: The text with numbers replaced by their word representation.
    """
    return PATTERN_NUMBER.sub(
        lambda match: num2words(int(match.group(0)), lang=language), text)


def text_to_speech(text, output, cache_dir, speaker, tts_model, device_name):
    device = torch.device(device_name)
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              tts_model.path)
    model = PackageImporter(model_path).load_pickle("tts_models", "model")
    model.to(device)

    text = convert_numbers(text, speaker.language)
    text = translit(text, speaker.language)
    text = remove_unicode(text)
    speech = AudioSegment.empty()

    for index, chunk in enumerate(chunk_generator(text, 500)):
        audio_path = os.path.join(
            cache_dir, "{}{:04d}{}".format(CHUNK_PREFIX, index, CHUNK_POSTFIX))
        model.save_wav(text=chunk,
                       audio_path=audio_path,
                       speaker=tts_model.speaker,
                       sample_rate=tts_model.sample_rate)
        speech += AudioSegment.from_file(audio_path)

    speech.export(output, format="mp3")


def clear_cache(cache_dir):
    """
    Clears the specified cache directory by removing all files that match the chunk pattern.

    Args:
        cache_dir (str): The path to the directory to be cleared.
    """
    if not os.path.exists(cache_dir):
        return

    for item in os.listdir(cache_dir):
        if item.startswith(CHUNK_PREFIX) and item.endswith(CHUNK_POSTFIX):
            item_path = os.path.join(cache_dir, item)
            os.unlink(item_path)


@click.command()
@click.option("--input",
              "-i",
              "input_file",
              type=click.Path(exists=True, dir_okay=False),
              help="Input file path")
@click.option("--output",
              "-o",
              required=True,
              type=click.Path(dir_okay=False),
              help="Output file path")
@click.option("--cache-dir",
              "-c",
              default=tempfile.gettempdir(),
              show_default=True,
              type=click.Path(file_okay=False),
              help="Temporary files directory")
@click.option("--language",
              "-l",
              default="ru",
              show_default=True,
              type=click.Choice(["ru", "en"], case_sensitive=False),
              help="Language (ru or en)")
@click.option("--speaker",
              "-s",
              default="female",
              show_default=True,
              type=click.Choice(["male", "female"], case_sensitive=False),
              help="Speaker (male or female)")
@click.option("--device",
              "-d",
              default="cuda",
              show_default=True,
              help="PyTorch device name")
def tts(input_file, output, cache_dir, language, speaker, device):
    if input_file:
        with open(input_file, "r") as f:
            input_text = f.read()
    else:
        input_text = sys.stdin.read()

    cache_dir = os.path.abspath(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)
    speaker = Speaker(language, speaker)
    model = LANGUAGE_MODELS[speaker]

    try:
        text_to_speech(input_text, output, cache_dir, speaker, model, device)
    except Exception as e:
        print(e)
    finally:
        clear_cache(cache_dir)


if __name__ == "__main__":
    tts()
