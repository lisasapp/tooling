import os
import subprocess
import sys

from srs_data_management.constants import ASAPP_ROOT, ASAPP_MLENG_ROOT
from srs_data_management.constants import CLIENT_FULL_NAMES
from srs_data_management.base import BaseTool
from srs_data_management.sampling import GenerateUniformSampleForClient

import pandas as pd


class ProcessTagsThatClientReturns(BaseTool):

    """
    Before running this class, the client's changes to tags must be
    incorporated manually into the uniform tag sample, then saved locally.
    These steps are enumerated in the README under the
    `ProcessTagsThatClientReturns` sub-header.

    With the updated uniform sample, this class performs three steps:
    1. Prepare tag updates to original uniform sample based on the updated
    uniform sample (the file returned from client, in the case of Condor).
    2. Apply prepared tag updates to the uniform sample file (which lives
    in S3, as per `GenerateUniformSampleForClient._push_uniform_sample_to_s3`).
    3. Prepare tag updates to virtual corpora. For Condor, these corpora
    include: `comcast_training,comcast_baseline,comcast_devtest,ccsrsprodweb`.
    4. Apply prepared tag updates to virtual corpora (which live in S3).

    !!! CURRENTLY ONLY WORKS FOR CONDOR

    TODO: GENERALIZE FOR SPEAR
    python $ASAPP_MLENG_ROOT/tools/autotagger.py local://spearsrsmerging-week20170924.csv spearsrssampling:week20170924uniform1200 --output-dir retag --retag
    python $ASAPP_MLENG_ROOT/tools/corpus_split.py --n-splits 3 --stratified tag --output-dir uploads local://retag/spearsrssampling-week20170924uniform1200_auto.csv
    corpora push --directory uploads/ --bucket asapp-corpora-spear
    code for add_corpus, remove_corpus
    """

    EXPECTED_INPUT_FILE_COLUMNS = ['text', 'tag', 'notes']

    def __init__(self, config):
        self._config = config['tagging']
        self._client = config['client']
        self._start_date = config['start_date']
        self._end_date = config['end_date']
        self._input_directory = os.path.join(ASAPP_ROOT, 'data', self._client, self._start_date)

    @property
    def input_file(self):
        return os.path.join(
            self._input_directory,
            f'{CLIENT_FULL_NAMES[self._client]}-tagsource{self._start_date}.csv'
        )

    @property
    def uniform_sample_file(self):
        return f'ccsrsprod-week{self._start_date}uniform-450.csv'

    @property
    def uniform_sample_file_corpora_spec(self):
        return f'condorsrssampling:week{self._start_date}uniform450'

    @property
    def uniform_sample_file_updated_with_client_tags(self):
        return self.uniform_sample_file.replace('.csv', '_auto.csv')

    def _run_steps(self):
        self._prepare_tag_updates_to_original_uniform_sample()
        self._update_uniform_sample_in_s3()

        self._prepare_tag_updates_to_virtual_corpora()
        self._update_virtual_corpora_in_s3()

    def _validate_input(self):
        input_file_header = pd.read_csv(self.input_file, encoding='utf-8-sig')
        input_file_columns = input_file_header.columns.tolist()
        if not input_file_columns == self.EXPECTED_INPUT_FILE_COLUMNS:
            raise Exception('Input does not contain the correct columns')

    def _prepare_tag_updates_to_original_uniform_sample(self):
        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_MLENG_ROOT, 'tools', 'autotagger.py'),
            'local://' + self.input_file,
            self.uniform_sample_file_corpora_spec,
            '--output-dir', '.',
            '--retag'
        ])

    def _update_uniform_sample_in_s3(self):
        subprocess.run([
            'corpora', 'push_update',
            '--filepath', 'local://' + self.uniform_sample_file_updated_with_client_tags,
            '--bucket', 'asapp-corpora-tagging',
            self.uniform_sample_file_corpora_spec
        ])

    def _prepare_tag_updates_to_virtual_corpora(self):
        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_MLENG_ROOT, 'tools', 'autotagger.py'),
            self.uniform_sample_file_corpora_spec,
            'comcast_training,comcast_baseline,comcast_devtest,ccsrsprodweb',
            '--output-dir', os.path.join(self._input_directory, 'virtual_corpora_tag_updates'),
            '--retag'
        ])

    def _update_virtual_corpora_in_s3(self):
        subprocess.run([
            'corpus_updater',
            os.path.join(self._input_directory, 'virtual_corpora_tag_updates')
        ])
