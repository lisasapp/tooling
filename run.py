from ruamel import yaml

from tools.sampling import GenerateUniformSampleForClient
from tools.tagging import ProcessTagsThatClientReturns


DEFAULT_CONFIG_PATH = 'config.yaml'


if __name__ == '__main__':
    CONFIG = yaml.safe_load( open(DEFAULT_CONFIG_PATH, 'r') )
    GenerateUniformSampleForClient(config=CONFIG).run()
    ProcessTagsThatClientReturns(config=CONFIG).run()
