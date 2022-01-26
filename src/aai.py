#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module and CLI interface for AssemblyAI's API
"""

import os
import argparse
from pathlib import Path

import requests


def submit_transcript(token: str, url: str, custom_vocab: list=None,
                      boost_value: str=None):
    endpoint = 'https://api.assemblyai.com/v2/transcript'
    json = {
        'audio_url': url,
        'word_boost': custom_vocab,
        'boost_param': boost_value
    }
    headers = {'authorization': token, 'content-type': 'application/json'}
    response = requests.post(endpoint, json=json, headers=headers)

    return response.json()


def get_transcript(token: str, transcript_id: str):
    endpoint = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'
    headers = {
        'authorization': token,
    }
    response = requests.get(endpoint, headers=headers)

    return response.json()


def upload_transcript(token: str, audio_file: Path):
    headers = {'authorization': token} 
    response = requests.post('https://api.assemblyai.com/v2/upload',
                             headers=headers,
                             data=_read_file(audio_file))

    return response.json()


def _read_file(filename: Path, chunk_size=5242880):
    with open(filename, 'rb') as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data
            

if __name__ == '__main__':
    """
    Logic for running as a standalone script.
    """
    argparser = argparse.ArgumentParser(
        description='CLI interface for AssemblyAI\'s API'
    )
    subparser = argparser.add_subparsers(
        dest='action', 
        required=True,
        help='API action to execute'
    )

    submit = subparser.add_parser(
        'submit', 
        help='Submit a file for transcription'
    )
    submit.add_argument(
        'url',
        type=str,
        help='URL for the audio file to submit'
    )

    get = subparser.add_parser(
        'get',
        help='Retrieve a completed transcript'
    )
    get.add_argument(
        'transcript_id',
        type=str,
        help='ID of the transcript to be retrieved'
    )

    upload = subparser.add_parser(
        'upload',
        help='Upload a file to AssemblyAI'
    )
    upload.add_argument(
        'audio_file',
        type=str,
        help='Audio file to upload'
    )

    argparser.add_argument(
        '--token',
        type=str,
        help='AssemblyAI API token'
    )

    args = argparser.parse_args()
    if args.token is not None: 
        token = args.token
    else:
        token = os.environ['AAI_TOKEN']

    if args.action == 'submit':
        submit_transcript(token, args.url)
    elif args.action == 'get':
        get_transcript(token, args.transcript_id)
    elif args.action == 'upload':
        audio_path = Path(args.audio_file).resolve()
        upload_transcript(token, audio_path)

