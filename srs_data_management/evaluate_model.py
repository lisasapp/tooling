import os
from subprocess import Popen, PIPE
from srs_data_management import constants


class EvaluateModel:

    def __init__(self, config):
        self._client = config['client']
        metrics_config = config['metrics']
        self._baseline = metrics_config['metric']['baseline']
        self._output_dir = metrics_config['output_dir']

    def get_observed_metrics(self, key, level='1*', blacklist=None, whitelist=None):
        if self._client == 'condor':
            commandline = ['pythona',
                            '-m', 'asapp.metrics',
                            '--source', 'comcast_baseline',
                            '--observed-data', os.path.join('local://srs_data_management' , key +'_observed.csv'),
                            '--business-logic', os.path.join(constants.ASAPP_COMCAST_SRS_ROOT , 'business_logic'),
                            '--metrics', 'cust,acc,prec,recall',
                            '--taglevel', level
                          ]
        elif self._client == 'spear':
            commandline = ['pythona',
                           '-m', 'asapp.metrics',
                           '--source', 'spear_baseline',
                           '--observed-data', os.path.join('local://srs_data_management', key + '_observed.csv'),
                           '--metrics', 'fscore,prec,recall',
                           '--use-spear-other-transform',
                           '--taglevel', level
                           ]

        if blacklist:
            commandline += ['--blacklist-classes', blacklist]
        elif whitelist:
            commandline += ['--whitelist-classes', whitelist]
        process = Popen(commandline,
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
        if self._client == 'condor':
            output = self.get_observed_metrics(key=key,
                                               level=taglevel,
                                               blacklist='V,_*')
            self.write_xls(output, key + '_' + taglevel)
        elif self._client == 'spear':
            # All Intents
            all_output = self.get_observed_metrics(key=key,
                                                   level=taglevel,
                                                   blacklist='V,O')
            self.write_xls(all_output, key + '_all_' + taglevel)
            # Automated Intents
            auto_output = self.get_observed_metrics(key=key,
                                                    level=taglevel,
                                                    whitelist='AA,AH,BA,BB,BP,BQ')
            self.write_xls(auto_output, key + '_auto_' + taglevel)
