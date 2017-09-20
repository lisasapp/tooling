import os
import subprocess
import sys

from ruamel import yaml


DEFAULT_CONFIG_PATH = 'config.yml'
ASAPP_ROOT = os.environ['ASAPP_ROOT']
ASAPP_PRODML_ROOT = os.environ['ASAPP_PRODML_ROOT']


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

    def run(self):
        # self._sample_production_logs()
        self._take_uniform_sample()
        # self._autotag_uniform_sample()
        # self._push_uniform_sample_to_s3()
        # self._print_next_steps()

    def _sample_production_logs(self):
        log_directory = os.path.join(ASAPP_ROOT, 'data', self.client, self.start_date)
        subprocess.run(['cd', log_directory])
        subprocess.run([
            sys.executable,
            os.path.join(ASAPP_PRODML_ROOT, 'tools', 'harvest_cc_logs.py'),
            '--dt_from', self.start_date + 'T0:0:0',
            '--dt_to', self.end_date + 'T0:0:0',
            '--output', os.path.join(log_directory, 'full-sample.csv'),
            '--no-collapse'
        ])
