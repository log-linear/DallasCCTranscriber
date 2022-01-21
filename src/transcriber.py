#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wave
import argparse
import csv
from pathlib import Path

import numpy as np
from stt import Model


def transcribe_file(audio_path: Path, model_path: Path, scorer_path: Path=None, 
                    hotwords_path: Path=None, beam_width: int=None,
                    n_transcripts: int=1):
    transcriber = Model(str(model_path))

    if scorer_path is not None:
        transcriber.enableExternalScorer(str(scorer_path))

    if hotwords_path is not None:
        transcriber = _add_hotwords(transcriber, hotwords_path)
    
    if beam_width is not None:
        transcriber.setBeamWidth(str(beam_width))

    audio = _wav_to_array(str(audio_path))

    transcription = transcriber.sttWithMetadata(audio, n_transcripts)

    return transcription


def _wav_to_array(audio_path: str):
    audio_file = wave.open(audio_path)
    samples = audio_file.getnframes()
    audio = audio_file.readframes(samples)
    audio_as_np_int16 = np.frombuffer(audio, dtype=np.int16)

    return audio_as_np_int16


def _add_hotwords(model: Model, hotwords_path: Path) -> Model:
    with open(hotwords_path, 'r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        for row in csv_reader:
            model.addHotWord(row['word'], float(row['boost_value']))

    return model


if __name__ == '__main__':
    """
    Logic for running as a standalone script.
    """
    argparser = argparse.ArgumentParser(
        description='Create a speech transcription of an audio file'
    )
    argparser.add_argument(
        'audio_file',
        type=str,
        help='Audio file to transcribe'
    )
    argparser.add_argument(
        'model',
        type=str,
        help='coqui model to use for transcribing'
    )
    argparser.add_argument(
        '--scorer',
        type=str,
        help='scorer to use'
    )
    argparser.add_argument(
        '--hotwords_file', 
        type=str,
        help='''CSV file containing hot words and boost values for improved 
                transcription'''
    )
    args = argparser.parse_args()
    audio_path = Path(args.audio_file).resolve()
    model_path = Path(args.model).resolve()

    try:
        scorer_path = Path(args.scorer).resolve()
    except TypeError:
        scorer_path = None

    try:
        hotwords_path = Path(args.hotwords_file).resolve()
    except TypeError:
        hotwords_path = None

    transcription = transcribe_file(audio_path, model_path, scorer_path, 
                                    hotwords_path)

    print(transcription)

