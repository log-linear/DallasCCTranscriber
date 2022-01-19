#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path

import pdftotext 
import spacy


def load_model(name) -> spacy.language.Language:
    try:
        model = spacy.load(name)
    except OSError:
        print('''spacy model `len_core_web_lg` not found, please install using 
                 `python -m spacy download en_core_web_lg`''')
        exit(1)

    return model


def pdf_to_text(pdf_path: Path) -> str:
    """
    Parse minutes files into a single string
    """
    with open(pdf_path, 'rb') as f:
        pdf = pdftotext.PDF(f)

    txt = ''.join([page for page in pdf])
                    
    return txt

 
def main(minutes_file: str):
    minutes = pdf_to_text(Path(minutes_file).resolve())
    nlp = load_model('en_core_web_lg')
    doc = nlp(minutes)
    phrases = [
        tkn.text for tkn in doc 
        if tkn.pos_ == 'PROPN' 
        and tkn.text.isupper() == False
        and tkn.text
    ]

    return phrases


if __name__ == "__main__":  
    argparser = argparse.ArgumentParser(
        description='Generate phrase list for GCP transcriber'
    )
    argparser.add_argument(
        'minutes_file', 
        type=str,
        help='PDF file containing City Council meeting minutes'
    )
    args = argparser.parse_args()
    print(main(args.minutes_file))

