#!/usr/bin/env pythona
import sys
import argparse
from ruamel import yaml

from asapp.common import cli
from srs_data_management.sampling import GenerateUniformSampleForClient
from srs_data_management.tagging import ProcessTagsThatClientReturns
from srs_data_management.generate_baseline_report import GenerateBaselineReport

DEFAULT_CONFIG_PATH = 'srs_data/config.yaml'


def get_parser():
    aparser = cli.ASAPPArgumentParser(description=__doc__)
    aparser.add_argument('CONFIG_FILE', nargs='?', default=DEFAULT_CONFIG_PATH, type=str, help='Path to the configuration file')
    return aparser


def parse_config(filepath):
    return yaml.safe_load(open(filepath, 'r'))


def run():
    parsed_args = get_parser().parse_args()
    config = parse_config(parsed_args.CONFIG_FILE)

    GenerateUniformSampleForClient(config).run()
    #ProcessTagsThatClientReturns(config).run()
    # GenerateBaselineReport(config).run()


if __name__ == '__main__':
    sys.exit(run())
