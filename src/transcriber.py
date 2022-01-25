#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import wave
import argparse
import csv
import logging
from pathlib import Path
from timeit import default_timer as timer

import numpy as np
from stt import Model, CandidateTranscript


def transcribe_audio(audio_path: Path, model_path: Path, scorer_path: Path=None, 
                     hotwords_path: Path=None, beam_width: int=None):
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler(Path.cwd().parent / 'transcriber.log'),
            logging.StreamHandler()
        ]
    )

    transcriber = Model(str(model_path))

    if scorer_path is not None:
        transcriber.enableExternalScorer(str(scorer_path))

    if hotwords_path is not None:
        transcriber = _add_hotwords(transcriber, hotwords_path)
    
    if beam_width is not None:
        transcriber.setBeamWidth(str(beam_width))

    audio = _wav_to_array(str(audio_path))

    logging.info(f'Running inference on {str(audio_path)}')
    start_time = timer()
    transcription = transcriber.sttWithMetadata(audio)
    end_time = timer() - start_time
    transcript = transcription.transcripts[0]
    logging.info(f'Transcription completed in {end_time} seconds')

    with open(audio_path.with_suffix('.csv'), 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow([
            'confidence',
            'text',
            'timestep',
            'start_time'
        ])
        for token in transcript.tokens:
            csv_writer.writerow([
                transcript.confidence,
                token.text,
                token.timestep,
                token.start_time
            ])


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

    transcribe_audio(audio_path, model_path, scorer_path, hotwords_path)

