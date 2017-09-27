from ruamel import yaml

from srs_data.sampling import GenerateUniformSampleForClient
from srs_data.tagging import ProcessTagsThatClientReturns


DEFAULT_CONFIG_PATH = 'srs_data/config.yaml'


if __name__ == '__main__':
    CONFIG = yaml.safe_load( open(DEFAULT_CONFIG_PATH, 'r') )
    GenerateUniformSampleForClient(config=CONFIG).run()
    ProcessTagsThatClientReturns(config=CONFIG).run()
