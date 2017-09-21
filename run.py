from ruamel import yaml

from sampling import GenerateUniformSampleForClient


DEFAULT_CONFIG_PATH = 'config.yml'


if __name__ == '__main__':
    CONFIG = yaml.safe_load(config_file)
    GenerateUniformSampleForClient(config=CONFIG).run()
