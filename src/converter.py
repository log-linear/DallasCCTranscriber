#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path

from pydub import AudioSegment


def mp3_to_wav(audio_file: str, frame_rate: int, n_channels: int):
    """
    Convert .mp3 file to .wav

    audio_file : str
        Path to the audio file to be converted
    frame_rate : int
        Audio sampling rate for the converted file
    n_channels : int
        Number of audio channels: 1 for mono, 2 for stereo
    """
    audio_path = Path(audio_file).resolve()
    aud = (
        AudioSegment.from_mp3(audio_path)
            .set_frame_rate(frame_rate)
            .set_channels(n_channels)
    )
    aud.export(audio_path.with_suffix('.wav'), format='wav')


if __name__ == '__main__':
    """
    Logic for running as a standalone script
    """
    parser = argparse.ArgumentParser(description='Convert .mp3 files to .wav')
    parser.add_argument('audio_file', type=str)
    parser.add_argument(
        '--frame_rate', '-f',
        type=int, 
        default=16000,
        help='Audio sampling rate for the converted file',
        required=False
    )
    parser.add_argument(
        '--channels', '-c',
        type=int, 
        default=1,
        help='Number of audio channels: 1 for mono, 2 for stereo',
        required=False
    )
    args = parser.parse_args()
    
    mp3_to_wav(args.audio_file, args.frame_rate, args.channels)

