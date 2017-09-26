import os
from subprocess import Popen, PIPE
from workflow.paths import *

class EvaluateModel:

    def __init__(self, baseline):
        self._baseline = baseline

    def get_observed_metrics(self, observedfile, level='1*'):
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

    def write_xls(self, output, title):
        # write to file -> later change to excel
        # write summary
        #metrics_dir = '/Users/lisa/ASAPPinc/releases/condor/' + baseline + '/'
        metrics_dir = self._baseline + '/'
        if not os.path.exists(metrics_dir):
            os.makedirs(metrics_dir)

        file = open(
            metrics_dir + title + '_metrics.xls',
            'wb')
        file.write(output)
        file.close()

    def run(self, release):
        #parsed_args = parse_args(args)
        #release = parsed_args.RELEASE
        #baseline = parsed_args.BASELINE

        uniquekey = release + '_' + self._baseline
        observed = uniquekey + '_observed.csv'

        print("evaluate taglevel1")
        output = self.get_observed_metrics(observed)
        self.write_xls(output, uniquekey)

        #print("evaluate taglevel4")
        #output_4level = get_observered_metrics(observed, '4*')
        #write_xls(output_4level, baseline, uniquekey + '_taglevel4')


