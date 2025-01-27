import click
import tempfile

from collections import namedtuple
from pathlib import Path
from speakerpy.lib_sl_text import SeleroText
from speakerpy.lib_speak import Speaker
from sys import stdin

# Russian: speaker = xenia, model = ru_v3, language = "ru"
# English: speaker = en_0, model = v3_en, language = "en"

LanguageSettings = namedtuple("LanguageSettings", ["model", "speaker"])

LANGUAGES = {
    "en": LanguageSettings("v3_en", "en_5"),
    "ru": LanguageSettings("ru_v3", "xenia"),
}

SAMPLE_RATES = {
    "8000": int(8000),
    "16000": int(16000),
    "24000": int(24000),
    "48000": int(48000),
}


class PathSpeaker(Speaker):

    def save_mp3(
        self,
        text: str,
        sample_rate: int,
        output_file: str,
        cache_dir: str,
    ) -> Path:
        sl_text = SeleroText(text, to_language=self.language)
        filenames = list(
            self._chunks_synthes(sl_text, cache_dir, sample_rate, sample_rate))
        output_file = Path(output_file)

        self._join_mp3(filenames, output_file)

        return filenames


@click.command()
@click.option("-i", "--input", help="Input file (default STDIN)")
@click.option("-o", "--output", help="Output file")
@click.option("-l",
              "--language",
              default="ru",
              help="Speaker language",
              show_default=True,
              type=click.Choice(LANGUAGES, case_sensitive=False))
@click.option("-s",
              "--speaker",
              help="Speaker name (default 'xenia' or 'en_5')")
@click.option("-r",
              "--sample-rate",
              default="48000",
              help="Sample rate",
              show_default=True,
              type=click.Choice(SAMPLE_RATES, case_sensitive=False))
@click.option("-c",
              "--cache-dir",
              default=tempfile.gettempdir(),
              help="Cache directory",
              show_default=True)
def start(input, output, language, speaker, sample_rate, cache_dir):
    if input is None or input == "-":
        source = stdin.read()
    else:
        with open(input, "r") as f:
            source = f.read()

    model = LANGUAGES[language].model
    speaker = speaker or LANGUAGES[language].speaker
    speaker = PathSpeaker(model_id=model,
                          language=language,
                          speaker=speaker,
                          device="cpu")
    speaker.save_mp3(source,
                     output_file=output,
                     cache_dir=cache_dir,
                     sample_rate=SAMPLE_RATES[sample_rate])


if __name__ == '__main__':
    start()
