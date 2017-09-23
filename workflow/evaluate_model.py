import argparse
import os

from subprocess import Popen, PIPE
from asapp.common import cli
from asapp.common import config

from workflow.paths import *

def parse_args(args):
    aparser = argparse.ArgumentParser(description=__doc__)
    cli.add_logging_to_parser(aparser)

    aparser.add_argument('RELEASE', default=None, type=str, help='Name of the model release')
    aparser.add_argument('BASELINE', default=None, type=str, help='Date of the baseline set to use')

    return aparser.parse_args()


def get_observered_metrics(observedfile, level='1*'):
    process = Popen(['pythona',
                    '-m', 'asapp.metrics',
                    '--source', 'comcast_baseline',
                    '--observed-data', 'local://'+observedfile,
                    '--business-logic', ASAPP_COMCAST_SRS_ROOT + '/business_logic',
                    '--metrics', 'acc,prec,recall',
                    '--filter-classes', 'V,_*',
                    '--taglevel', level
                    ],
                   stdout=PIPE,
                   stderr=PIPE)
    output,err = process.communicate()
    return output

def write_xls(output, baseline, title):
    # write to file -> later change to excel
    # write summary
    #metrics_dir = '/Users/lisa/ASAPPinc/releases/condor/' + baseline + '/'
    metrics_dir = baseline + '/'
    if not os.path.exists(metrics_dir):
        os.makedirs(metrics_dir)

    file = open(
        metrics_dir + title + '_metrics.xls',
        'wb')
    file.write(output)
    file.close()

def run(release, baseline):
    #parsed_args = parse_args(args)
    #release = parsed_args.RELEASE
    #baseline = parsed_args.BASELINE

    uniquekey = release + '_' + baseline
    observed = uniquekey + '_observed.csv'

    print("evaluate taglevel1")
    output = get_observered_metrics(observed)
    write_xls(output, baseline, uniquekey)

    print("evaluate taglevel4")
    output_4level = get_observered_metrics(observed, '4*')
    write_xls(output_4level, baseline, uniquekey + '_taglevel4')
