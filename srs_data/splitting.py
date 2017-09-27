import os
import subprocess
import sys

from constants import ASAPP_ROOT, ASAPP_MLENG_ROOT
from constants import CLIENT_FULL_NAMES
from base import BaseTool

import pandas as pd


class SplitProcessedTagsIntoDataCorpora(BaseTool):

    EXPECTED_INPUT_FILE_COLUMNS = ['text', 'tag', 'notes']
    SUFFIX_REPLACEMENT_LOOKUP = {
        '_0': 'a',
        '_1': 'b',
        '_2': 'c'
    }

    def __init__(self, config):
        self._config = config['srs_data']['splitting']
        self._client = config['client']
        self._client_full_name = f'{CLIENT_FULL_NAMES[self._client]}'
        self._start_date = config['start_date']
        self._data_corpus_name = self._config['data_corpus_name']
        self._data_corpus_bucket = self._config['data_corpus_bucket']
        self._input_directory = os.path.join(ASAPP_ROOT, 'data', self._client, self._start_date)

    @property
    def input_file(self):
        return os.path.join(
            self._input_directory,
            f'{CLIENT_FULL_NAMES[self._client]}-tagsource{self._start_date}.csv'
        )

    def _run_steps(self):
        self._run_corpus_splitter()
        self._rename_local_datasets()

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

    def _rename_local_datasets(self):
        root, extension = os.path.splitext(self.input_file)
        for suffix in ['_0', '_1', '_2']:
            path = root + suffix + extension
            suffix_replacement = self.SUFFIX_REPLACEMENT_LOOKUP[suffix]
            new_path = path\
                         .replace(suffix, suffix_replacement)\
                         .replace(self._client_full_name, self._data_corpus_name)\
                         .replace('tagsource', 'week')
            os.rename(path, new_path)
