import os
import subprocess
import sys
from shutil import copyfile

from srs_data_management.constants import ASAPP_ROOT, ASAPP_PRODML_ROOT, ASAPP_MLENG_ROOT
from srs_data_management.base import BaseTool


class GenerateUniformSampleForClient(BaseTool):

    """
    Generate a uniform sample of SRS data for client.

    This class performs five steps to the above effect:

    1. Take all records from SRS production logs for the specified
    ("start_date", "end_date") date range.
    2. Take a uniform sample of the results of the previous step.
    3. Auto-tag the uniform sample.
    4. Push the result of the previous step to S3, via corpora.
    5. Print the final steps to take before sending the autotagged,
    uniform sample to client.
    """

    def __init__(self, config):
        self._config = config['sampling']
        self._client = config['client']
        self._start_date = config['start_date']
        self._end_date = config['end_date']
        self._data_count = self._config['data_count']
        self._output_directory = self._get_output_dir()

    @property
    def uniform_sample_file(self):
        return os.path.join(self._output_directory, f'{self._client}srssampling-week{self._start_date}uniform-{self._data_count}.csv')

    @property
    def autotagged_uniform_sample_file(self):
        return self.uniform_sample_file.replace('.csv', '_auto.csv')

    def _get_output_dir(self):
        directory = os.path.join(ASAPP_ROOT, 'data', self._client, self._start_date)
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

    def _run_steps(self):
        self._sample_production_logs()
        self._take_uniform_sample()
        self._autotag_uniform_sample()
        self._push_uniform_sample_to_s3()
        if self._client == 'spear':
            self._create_tagger_shuffle_files()
            self._push_tagger_directory_to_s3()
        #self._print_next_steps()

    def _validate_input(self):
        """
        This class has no ostensible "input". As such, we simply `pass` during
        validation.
        """
        pass

    def _sample_production_logs(self):
        hostname = ""
        if self._client == 'condor':
            hostname = 'comcast-kibana.asapp.com'
        elif self._client == 'spear':
            hostname = 'sprint-kibana.asapp.com'

        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_PRODML_ROOT, 'tools', 'harvest_cc_logs.py'),
            '--dt_from', self._start_date + 'T0:0:0',
            '--dt_to', self._end_date + 'T0:0:0',
            '--output', os.path.join(self._output_directory, 'full-sample.csv'),
            '--no-collapse',
            '--host', hostname
        ])

    def _take_uniform_sample(self):
        if self._client == 'condor':
            subprocess.run([
                sys.executable,
                os.path.join(ASAPP_PRODML_ROOT, 'tools', 'hier_sample_logs.py'),
                '--consolidate',
                '--sample-size', self._data_count,
                '--custguid-blacklist', 'comcastblacklist:20170804',
                'local://' + os.path.join(self._output_directory, 'full-sample.csv'),
                self.uniform_sample_file
            ])
        elif self._client == 'spear':
            subprocess.run([
                sys.executable,
                os.path.join(ASAPP_PRODML_ROOT, 'tools', 'hier_sample_logs.py'),
                '--consolidate',
                '--sample-size', self._data_count,
                '--clean-pii',
                '--custguid-blacklist', 'spearblacklist:20170822',
                'local://' + os.path.join(self._output_directory, 'full-sample.csv'),
                self.uniform_sample_file
            ])

    def _autotag_uniform_sample(self):
        datalist = ""
        if self._client == 'condor':
            datalist = 'comcast_baseline,comcast_devtest,comcast_training,ccsrsprodweb'
        elif self._client == 'spear':
            datalist = 'spear_training,spear_baseline,spear_test'

        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_MLENG_ROOT, 'tools', 'autotagger.py'),
            '--retag',
            '--output-dir', self._output_directory,
            datalist,
            'local://' + self.uniform_sample_file
        ])

    def _push_uniform_sample_to_s3(self):
        # you need to specify a corpus here. for spear, it should be spearsrstagging!
        subprocess.run([
            'corpora', 'push',
            '--filepath', self.autotagged_uniform_sample_file,
            '--bucket', 'asapp-corpora-tagging',
            f'{self._client}srssampling:week{self._start_date}uniform{self._data_count}'
        ])

    def _create_tagger_shuffle_files(self):
        tagging_file = os.path.join(self._output_directory, f'{self._client}srstagging-week{self._start_date}uniform{self._data_count}.csv')
        copyfile(self.autotagged_uniform_sample_file, tagging_file)
        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_MLENG_ROOT, 'tools', 'corpus_split.py'),
            '--n-splits', self._config['splits'],
            '--tagger-shuffle', self._config['tagger_count'],
            '--output-dir', os.path.join(self._output_directory, 'tagger'),
            'local://' + tagging_file
        ])

    def _push_tagger_directory_to_s3(self):
        subprocess.run([
            'corpora', 'push',
            '--directory', os.path.join(self._output_directory, 'tagger/'),
            '--bucket', 'asapp-corpora-tagging'
        ])

    def _print_next_steps(self):
        print(
f"""
\nAs a final step, please perform the following:
    1. Open {self.autotagged_uniform_sample_file} in Excel.
    2. Remove all columns except: `tag`, `observed`, `weight`, `text`.
    3. Save result as {CLIENT_FULL_NAMES[self._client]}{self._start_date}.xslx.
    4. Email this file to {self._client.capitalize()}.
"""
        )
