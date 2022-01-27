#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module to generate hotword lists from PDF files of City Council meeting minutes.
Hotwords are optional parameters for speech-to-text models that can increase the 
chances of correctly transcribing certain words or phrases. This module 
generates hotword lists from proper nouns extracted from a meeting 
minutes file. 

This module can also be run as a standalone script, e.g.:

    python hotwords.py 12012Min.pdf
"""

import argparse
import csv
from pathlib import Path
from collections import Counter

import pdftotext 
import spacy
import spacy.cli.download
from spacy.tokens import Doc
from spacy.language import Language


def generate_hotwords(minutes_path: Path, model: str='en_core_web_lg'):
    """
    Generate a hotword list from City Council meeting minutes. List will be 
    saved as a csv file in the same directory as the input PDF file.

    minutes_path : Path
        Path to the City Council meeting minutes PDF
    range_min : int
        Minimum boost value to assign to a given word.
    range_max : int
        Maximum boost value to assign to a given word.
    """
    minutes = _pdf_to_str(minutes_path)
    nlp = _load_model(model)
    doc = nlp(minutes)
    propns = _get_proper_nouns(doc)
    normalized_propns = _normalize_words(propns)
    propn_freqs = Counter(normalized_propns)

    # Write word list to file
    output_path = minutes_path.with_suffix('.csv')
    with open(output_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter = ',', quotechar='"')
        csv_writer.writerow(['word', 'frequency'])  # header row

        for item in propn_freqs.items():
            csv_writer.writerow([item[0], item[1]])


def _load_model(name: str) -> Language:
    """
    Helper function to load spacy language model

    name : str
        Name of the language model to load
    """
    try:
        model = spacy.load(name)
    except OSError:
        spacy.cli.download.download(name)
        model = spacy.load(name)
    
    return model


def _pdf_to_str(pdf_path: Path) -> str:
    """
    Helper function parse PDF files into a single string

    pdf_path : Path
        Path to the PDF file
    """
    with open(pdf_path, 'rb') as f:
        pdf = pdftotext.PDF(f)

    return ''.join([page for page in pdf])


def _get_proper_nouns(doc: Doc) -> list:
    """
    Helper function to extract all proper nouns from a spacy-tokenized Doc

    doc : Doc
        Doc object from which to extract proper nouns
    """
    return [token.text for token in doc 
            if (
                token.pos_ == 'PROPN' 
                and token.text.isupper() == False
                and not token.is_stop
                and not token.is_punct
            )]


def _normalize_words(words: list) -> list:
    """
    Helper function to decapitalize and remove non-alphabetical characters from
    a list of strings

    words : list
        Array of strings to normalize
    """
    return [word.lower() for word in words if word.isalpha()]


if __name__ == "__main__":  
    """
    Logic for running as a standalone script.
    """
    argparser = argparse.ArgumentParser(
        description='''Generate a hotword list for improving Council Meeting 
                       transcriptions'''
    )
    argparser.add_argument(
        'minutes_file', 
        type=str,
        help='PDF file containing City Council meeting minutes'
    )
    argparser.add_argument(
        '--model', 
        type=str,
        default='en_core_web_lg',
        help='spacy model to use for parsing'
    )

    args = argparser.parse_args()
    minutes_path = Path(args.minutes_file).resolve()

    generate_hotwords(minutes_path, args.model)

