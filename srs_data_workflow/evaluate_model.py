import os
from subprocess import Popen, PIPE
from srs_data_workflow import constants

class EvaluateModel:

    def __init__(self, config):
        self._baseline = config['metric']['baseline']
        self._output_dir = config['output_dir']


    def get_observed_metrics(self, key, level='1*'):
        process = Popen(['pythona',
                        '-m', 'asapp.metrics',
                        '--source', 'comcast_baseline',
                        '--observed-data', 'local://srs_data_workflow/'+ key +'_observed.csv',
                        '--business-logic', constants.ASAPP_COMCAST_SRS_ROOT + '/business_logic',
                        '--metrics', 'cust,acc,prec,recall',
                        '--filter-classes', 'V,_*',
                        '--taglevel', level
                        ],
                       stdout=PIPE,
                       stderr=PIPE)
        output,err = process.communicate()
        return output


    def write_xls(self, output, title):
        # write to file -> later change to excel
        metrics_dir = self._output_dir + '/' + self._baseline + '/'
        if not os.path.exists(metrics_dir):
            os.makedirs(metrics_dir)

        file = open(
            metrics_dir + title + '_metrics.xls',
            'wb')
        file.write(output)
        file.close()


    def _create_release_key(self, release, taglevel):
        uniquekey = release + '_' + self._baseline
        return uniquekey


    def run(self, release, taglevel):
        print("evaluate ", release, taglevel)
        key = self._create_release_key(release, taglevel)
        output = self.get_observed_metrics(key, taglevel)
        self.write_xls(output, key + '_' + taglevel)


