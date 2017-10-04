import os
from subprocess import Popen, PIPE
from srs_data import constants

class EvaluateModel:

    def __init__(self, config):
        self._baseline = config['metric']['baseline']
        self._output_dir = config['output_dir']


    def get_observed_metrics(self, key, level='1*'):
        process = Popen(['pythona',
                        '-m', 'asapp.metrics',
                        '--source', 'comcast_baseline',
                        '--observed-data', os.path.join('local://srs_data' , key +'_observed.csv'),
                        '--business-logic', os.path.join(constants.ASAPP_COMCAST_SRS_ROOT , 'business_logic'),
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
        metrics_dir = os.path.join(self._output_dir, self._baseline)
        if not os.path.exists(metrics_dir):
            os.makedirs(metrics_dir)

        file = open(
            os.path.join(metrics_dir, title + '_metrics.xls'),
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


