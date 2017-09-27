import os
import subprocess
import sys

from srs_data import ASAPP_ROOT, ASAPP_MLENG_ROOT
from srs_data import CLIENT_FULL_NAMES
from srs_data.base import BaseTool

import pandas as pd


class ProcessTagsThatClientReturns(BaseTool):

    EXPECTED_INPUT_FILE_COLUMNS = ['text', 'tag', 'notes']

    def __init__(self, config):
        self._config = config['srs_data']['tagging']
        self._client = config['client']
        self._start_date = config['start_date']
        self._start_date = '20170903'
        self._end_date = config['end_date']
        self._input_directory = os.path.join(ASAPP_ROOT, 'data', self._client, self._start_date)

    @property
    def input_file(self):
        return os.path.join(
            self._input_directory,
            f'{CLIENT_FULL_NAMES[self._client]}-tagsource{self._start_date}.csv'
        )

    def _run_steps(self):
        self._overwrite_uniform_sample_currently_in_s3()
        self._locally_update_corpora_tags()
        self._run_corpus_updater()

    def _validate_input(self):
        input_file_header = pd.read_csv(self.input_file, encoding='utf-8-sig')
        input_file_columns = input_file_header.columns.tolist()
        if not input_file_columns == self.EXPECTED_INPUT_FILE_COLUMNS:
            raise Exception('Input does not contain the correct columns')

    def _overwrite_uniform_sample_currently_in_s3(self):
        subprocess.run([
            'corpora', 'push_update',
            '--filepath', self.input_file,
            '--bucket', 'asapp-corpora-tagging',
            f'condorsrssampling:week{self._start_date}uniform450'
        ])

    def _locally_update_corpora_tags(self):
        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_MLENG_ROOT, 'srs_data', 'autotagger.py'),
            'local://' + self.input_file,
            'comcast_training,comcast_baseline,comcast_devtest,ccsrsprodweb',
            '--output-dir', 'retag',
            '--retag'
        ])

    def _run_corpus_updater(self):
        subprocess.run([
            'corpus_updater',
            os.path.join(self._input_directory, 'retag')
        ])
