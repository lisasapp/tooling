import os
import subprocess
import sys

from constants import ASAPP_ROOT, ASAPP_MLENG_ROOT
from base import BaseTool

import pandas as pd


class SplitProcessedTagsIntoDataCorpora(BaseTool):

    EXPECTED_INPUT_FILE_COLUMNS = [
        'tag',
        'related_intent',
        'observed',
        'weight',
        'text',
        'history',
        'notes',
        'cust_guid',
        'md5',
        'model',
        'platform',
        'requesttype',
        'routed',
        'subtags',
        'tagsource',
        'timestamp',
        '_source',
    ]
    CORPORA_SPEC_SUFFIXES_FOR_SPLITS = ['a', 'b', 'c']

    def __init__(self, config):
        self._config = config['splitting']
        self._client = config['client']
        self._start_date = config['start_date']
        self._data_corpus_name = self._config['data_corpus_name']
        self._data_corpus_bucket = self._config['data_corpus_bucket']
        self._input_directory = os.path.join(ASAPP_ROOT, 'data', self._client, self._start_date)

    @property
    def input_file(self):
        return os.path.join(
            self._input_directory,
            # "_auto" is intentionally there twice. we should change
            # these paths soon, because they are confusing.
            f'ccsrsprod-week{self._start_date}uniform-450_auto_auto.csv'
        )

    @property
    def split_paths(self):
        root, extension = os.path.splitext(self.input_file)
        for suffix in ['_0', '_1', '_2']:
            yield root + suffix + extension

    def _run_steps(self):
        self._run_corpus_splitter()
        self._push_splits_to_s3()

    def _validate_input(self):
        input_file_header = pd.read_csv(self.input_file, encoding='utf-8-sig')
        input_file_columns = input_file_header.columns.tolist()
        if not input_file_columns == self.EXPECTED_INPUT_FILE_COLUMNS:
            raise Exception('Input does not contain the correct columns')

    def _run_corpus_splitter(self):
        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_MLENG_ROOT, 'tools', 'corpus_split.py'),
            '--n-splits', '3',
            '--stratified', 'tag',
            '--output-dir', self._input_directory,
            'local://' + self.input_file
        ])

    def _push_splits_to_s3(self):
        corpora_base_spec = f'ccsrsprod:week{self.start_date}'
        for path, suffix in zip(self.split_paths, self.CORPORA_SPEC_SUFFIXES_FOR_SPLITS):
            subprocess.run([
                'corpora', 'push',
                '--filepath', path,
                '--bucket', self._data_corpus_bucket,
                corpora_base_spec + suffix
            ])
