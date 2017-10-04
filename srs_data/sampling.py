import os
import subprocess
import sys

from srs_data import constants

class GenerateUniformSampleForClient:

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
        self._client = self._config['client']
        self._start_date = self._config['start_date']
        self._end_date = self._config['end_date']
        self._output_directory = os.path.join(constants.ASAPP_ROOT, 'data', self._client, self._start_date)

    def run(self):
        self._sample_production_logs()
        self._take_uniform_sample()
        self._autotag_uniform_sample()
        self._push_uniform_sample_to_s3()
        self._print_next_steps()

    def _sample_production_logs(self):
        subprocess.run([
            sys.executable,
            os.path.join(constants.ASAPP_PRODML_ROOT, 'workflow', 'harvest_cc_logs.py'),
            '--dt_from', self._start_date + 'T0:0:0',
            '--dt_to', self._end_date + 'T0:0:0',
            '--output', os.path.join(self._output_directory, 'full-sample.csv'),
            '--no-collapse'
        ])

    def _take_uniform_sample(self):
        subprocess.run([
            sys.executable,
            os.path.join(constants.ASAPP_PRODML_ROOT, 'workflow', 'hier_sample_logs.py'),
            '--consolidate',
            '--sample-size', '450',
            '--custguid-blacklist', 'comcastblacklist:20170804',
            'local://' + os.path.join(self._output_directory, 'full-sample.csv'),
            os.path.join(self._output_directory, f'ccsrsprod-week{self._start_date}uniform-450.csv')
        ])

    def _autotag_uniform_sample(self):
        subprocess.run([
            sys.executable,
            os.path.join(constants.ASAPP_MLENG_ROOT, 'workflow', 'autotagger.py'),
            '--output-dir', self._output_directory,
            'comcast_baseline,comcast_devtest,comcast_training,ccsrsprodweb',
            'local://' + os.path.join(self._output_directory, f'ccsrsprod-week{self._start_date}uniform-450.csv')
        ])

    def _push_uniform_sample_to_s3(self):
        subprocess.run([
            'corpora', 'push',
            '--filepath', os.path.join(self._output_directory, f'ccsrsprod-week{self._start_date}uniform-450_auto.csv'),
            '--bucket', 'asapp-corpora-tagging',
            'condorsrssampling:week{self._start_date}uniform450'
        ])

    def _print_next_steps(self):
        print(
f"""
\nAs a final step, please perform the following:
    1. Open ccsrsprod-week{self._start_date}uniform-450_auto.csv in Excel.
    2. Remove all columns except: `tag`, `observed`, `weight`, `text`.
    3. Save result as {self._client}{self._start_date}.xslx.
    4. Email this file to {self._client.capitalize()}.
"""
        )

