#!/usr/bin/env pythona
import sys
import argparse
from asapp.common import cli

from generate_baseline_report import GenerateBaselineReport

def parse_args(args):
    aparser = argparse.ArgumentParser(description=__doc__)
    cli.add_logging_to_parser(aparser)
    aparser.add_argument('CONFIG_FILE', default=None, type=str, help='Path to the configuration file')

    return aparser.parse_args()

def parse_config(filepath):
    # do the things to parse the file into a config object
    pass

def run(args):
    parsed_args = parse_args(args)
    config = parse_config(parsed_args.CONFIG_FILE)

    GenerateBaselineReport(config).run()

if __name__ == '__main__':
    sys.exit(run(sys.argv[1:]))