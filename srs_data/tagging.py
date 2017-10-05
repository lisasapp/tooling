import os
import subprocess
import sys

from srs_data.constants import ASAPP_ROOT, ASAPP_MLENG_ROOT
from srs_data.constants import CLIENT_FULL_NAMES
from srs_data.base import BaseTool
from srs_data.sampling import GenerateBaselineReport

import pandas as pd


class ProcessTagsThatClientReturns(BaseTool):

    EXPECTED_INPUT_FILE_COLUMNS = ['text', 'tag', 'notes']

    def __init__(self, config):
        self._config = config['tagging']
        self._client = config['client']
        self._start_date = config['start_date']
        self._start_date = '20170903'
        self._end_date = config['end_date']
        self._input_directory = os.path.join(ASAPP_ROOT, 'data', self._client, self._start_date)
        # this is bad. this will become more natural when we start making
        # dependencies between classes explicit.
        self._autotagged_uniform_sample_file = GenerateBaselineReport(config).autotagged_uniform_sample_file

    @property
    def input_file(self):
        return os.path.join(
            self._input_directory,
            f'{CLIENT_FULL_NAMES[self._client]}-tagsource{self._start_date}.csv'
        )

    @property
    def uniform_sample_file(self):
        return self._autotagged_uniform_sample_file

    @property
    def uniform_sample_file_updated_with_client_tags(self):
        return self.uniform_sample_file.replace('.csv', '_auto.csv')

    def _run_steps(self):
        self._update_the_original_uniform_sample()
        self._overwrite_uniform_sample_currently_in_s3()
        self._locally_update_corpora_tags()
        self._run_corpus_updater()

    def _validate_input(self):
        input_file_header = pd.read_csv(self.input_file, encoding='utf-8-sig')
        input_file_columns = input_file_header.columns.tolist()
        if not input_file_columns == self.EXPECTED_INPUT_FILE_COLUMNS:
            raise Exception('Input does not contain the correct columns')

    def _update_the_original_uniform_sample(self):
        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_MLENG_ROOT, 'srs_data', 'autotagger.py'),
            'local://' + self.input_file,
            'local://' + self.uniform_sample_file,
            '--output-dir', '.',
            '--retag'
        ])

    def _overwrite_uniform_sample_currently_in_s3(self):
        subprocess.run([
            'corpora', 'push_update',
            '--filepath', self.uniform_sample_file_updated_with_client_tags,
            '--bucket', 'asapp-corpora-tagging',
            f'condorsrssampling:week{self._start_date}uniform450'
        ])

    def _locally_update_corpora_tags(self):
        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_MLENG_ROOT, 'srs_data', 'autotagger.py'),
            'local://' + self.uniform_sample_file_updated_with_client_tags,
            'comcast_training,comcast_baseline,comcast_devtest,ccsrsprodweb',
            '--output-dir', 'corpora_tag_updates',
            '--retag'
        ])

    def _run_corpus_updater(self):
        subprocess.run([
            'corpus_updater',
            os.path.join(self._input_directory, 'corpora_tag_updates')
        ])
