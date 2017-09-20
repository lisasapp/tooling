import os
import subprocess
import sys

from ruamel import yaml


DEFAULT_CONFIG_PATH = 'config.yml'
ASAPP_ROOT = os.environ['ASAPP_ROOT']
ASAPP_PRODML_ROOT = os.environ['ASAPP_PRODML_ROOT']
ASAPP_MLENG_ROOT = os.environ['ASAPP_MLENG_ROOT']


class GenerateUniformSampleForClient:

    """
    Generate a uniform sample of SRS data for client.

    # TODO: Explain these steps in detail.
    """

    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        config_file = open(config_path, 'rb')
        self.config = yaml.safe_load(config_file)['sampling']
        self.client = self.config['client']
        self.start_date = self.config['start_date']
        self.end_date = self.config['end_date']
        self.log_directory = os.path.join(ASAPP_ROOT, 'data', self.client, self.start_date)

    def run(self):
        self._sample_production_logs()
        self._take_uniform_sample()
        self._autotag_uniform_sample()
        self._push_uniform_sample_to_s3()
        self._print_next_steps()

    def _sample_production_logs(self):
        subprocess.run(['cd', self.log_directory])
        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_PRODML_ROOT, 'tools', 'harvest_cc_logs.py'),
            '--dt_from', self.start_date + 'T0:0:0',
            '--dt_to', self.end_date + 'T0:0:0',
            '--output', os.path.join(self.log_directory, 'full-sample.csv'),
            '--no-collapse'
        ])

    def _take_uniform_sample(self):
        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_PRODML_ROOT, 'tools', 'hier_sample_logs.py'),
            '--consolidate',
            '--sample-size', '450',
            '--custguid-blacklist', 'comcastblacklist:20170804',
            'local://' + os.path.join(self.log_directory, 'full-sample.csv'),
            os.path.join(self.log_directory, f'ccsrsprod-week{self.start_date}uniform-450.csv')
        ])

    def _autotag_uniform_sample(self):
        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_MLENG_ROOT, 'tools', 'autotagger.py'),
            '--output-dir', self.log_directory,
            'comcast_baseline,comcast_devtest,comcast_training,ccsrsprodweb',
            'local://' + os.path.join(self.log_directory, f'ccsrsprod-week{self.start_date}uniform-450.csv')
        ])

    def _push_uniform_sample_to_s3(self):
        subprocess.run([
            'corpora', 'push',
            '--filepath', os.path.join(self.log_directory, f'ccsrsprod-week{self.start_date}uniform-450_auto.csv'),
            '--bucket', 'asapp-corpora-tagging',
            'condorsrssampling:week{self.start_date}uniform450'
        ])

    def _print_next_steps(self):
        print(
f"""
\nAs a final step, please perform the following:
    1. Open ccsrsprod-week{self.start_date}uniform-450_auto.csv in Excel.
    2. Remove all columns except: `tag`, `observed`, `weight`, `text`.
    3. Save result as {self.client}{self.start_date}.xslx.
    4. Email this file to {self.client.capitalize()}.
"""
        )
