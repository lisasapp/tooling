import os, subprocess

from tools import ASAPP_ROOT, ASAPP_MLENG_ROOT, ASAPP_PRODML_ROOT

import pandas as pd


class ProcessTagsThatClientReturns:

    EXPECTED_INPUT_FILE_HEADER = ['text', 'tag', 'notes']

    def __init__(self, config):
        self._config = config['tools']['tagging']
        self._client = config['client']
        self._start_date = config['start_date']
        self._end_date = config['end_date']
        self._output_directory = os.path.join(ASAPP_ROOT, 'data', self._client, self._start_date)

    @property
    def input_file(self):
        return os.path.join(self._output_directory, f'{self._client}-tagsource{self._start_date}.csv')

    def run(self):
        self._validate_input()
        self._run_steps()

    def _run_steps(self):
        self._overwrite_uniform_sample_currently_in_s3()

    def _validate_input(self):
        input_file_header = set(pd.read_csv(self.input_file).columns)
        if not input_file_header == self.EXPECTED_INPUT_FILE_HEADER:
            raise Exception('Input does not contain the correct columns')

    def _overwrite_uniform_sample_currently_in_s3(self):
        subprocess.run([
            'corpora', 'push_update',
            '--filepath', os.path.join(self._output_directory, f'{self._client}-tagsource{self._start_date}.csv'),
            '--bucket', 'asapp-corpora-tagging',
            'condorsrssampling:week{self._start_date}uniform450'
        ])
