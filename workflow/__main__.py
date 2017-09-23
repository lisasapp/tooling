#!/usr/bin/env pythona
import sys
import argparse
from ruamel import yaml

from asapp.common import cli
from workflow.generate_baseline_report import GenerateBaselineReport
from workflow.sampling import GenerateUniformSampleForClient

DEFAULT_CONFIG_PATH = 'workflow/default_config.yaml'


def get_parser():
    aparser = argparse.ArgumentParser(description=__doc__)
    cli.add_logging_to_parser(aparser)
    aparser.add_argument('CONFIG_FILE', nargs='?', default=DEFAULT_CONFIG_PATH, type=str, help='Path to the configuration file')
    return aparser


def parse_config(filepath):
    return yaml.safe_load(open(filepath, 'r'))


def run():
    parsed_args = get_parser().parse_args()
    config = parse_config(parsed_args.CONFIG_FILE)

    #GenerateUniformSampleForClient(config).run()
    GenerateBaselineReport(config).run()


if __name__ == '__main__':
    sys.exit(run())