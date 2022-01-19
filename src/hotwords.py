#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
from collections import Counter
import csv

import pdftotext 
import spacy
from spacy.tokens import Doc
from spacy.language import Language


def _load_model(name) -> Language:
    try:
        return spacy.load(name)
    except OSError:
        print('''spacy model `len_core_web_lg` not found, please install using 
                 `python -m spacy download en_core_web_lg`''')
        exit(1)


def _pdf_to_text(pdf_path: Path) -> str:
    """
    Parse minutes files into a single string
    """
    with open(pdf_path, 'rb') as f:
        pdf = pdftotext.PDF(f)

    return ''.join([page for page in pdf])


def _get_proper_nouns(doc: Doc) -> list:
    return [token.text for token in doc 
            if (
                token.pos_ == 'PROPN' 
                and token.text.isupper() == False
                and not token.is_stop
                and not token.is_punct
            )]


def _normalize_words(words: list) -> list:
    return [word.lower() for word in words if word.isalpha()]


def _normalize_freqs(word_freqs: Counter, range_min: int, 
                     range_max: int) -> Counter:
    word_counts = word_freqs.values()
    max_word_count = max(word_counts)
    min_word_count = min(word_counts)

    for item in word_freqs.items():
        current_word = item[0]
        current_word_count = item[1]
        word_freqs[current_word] = (
            (current_word_count - min_word_count) / 
            (max_word_count - min_word_count) *
            (range_max - range_min) + range_min
        )

    return word_freqs


def _write_hotwords_csv(hotwords: Counter, output_path: Path):
    with open(output_path, 'w', newline='') as csv_file:
        headers = ['word', 'boost_value']
        csv_writer = csv.DictWriter(csv_file, delimiter = ',', quotechar='"',
                                    fieldnames=headers)
        csv_writer.writeheader()

        for item in hotwords.items():
            csv_writer.writerow({headers[0]: item[0], headers[1]: item[1]})


def generate_hotword_list(minutes_file: str, range_min: int, range_max: int):
    minutes_path = Path(minutes_file).resolve()
    minutes = _pdf_to_text(minutes_path)
    nlp = _load_model('en_core_web_lg')
    doc = nlp(minutes)
    propns = _get_proper_nouns(doc)
    normalized_propns = _normalize_words(propns)
    propn_freqs = Counter(normalized_propns)
    normalized_freqs = _normalize_freqs(propn_freqs, range_min, range_max)
    _write_hotwords_csv(normalized_freqs, minutes_path.with_suffix('.csv'))


if __name__ == "__main__":  
    argparser = argparse.ArgumentParser(
        description='Generate phrase list for GCP transcriber'
    )
    argparser.add_argument(
        'minutes_file', 
        type=str,
        help='PDF file containing City Council meeting minutes'
    )
    argparser.add_argument(
        '--range_min', 
        default=1,
        type=int,
        help='Minimum boost value to assign to a given word.'
    )
    argparser.add_argument(
        '--range_max',
        default=20,
        type=int,
        help='Maximum boost value to assign to a given word.'
    )

    args = argparser.parse_args()
    generate_hotword_list(args.minutes_file, args.range_min, args.range_max)

