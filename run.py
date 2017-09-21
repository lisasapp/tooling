from ruamel import yaml

from sampling import GenerateUniformSampleForClient


DEFAULT_CONFIG_PATH = 'config.yaml'


if __name__ == '__main__':
    CONFIG = yaml.safe_load(DEFAULT_CONFIG_PATH)
    GenerateUniformSampleForClient(config=CONFIG).run()
