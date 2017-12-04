#!/usr/bin/env pythona
import os
import argparse
import sys
import subprocess
import threading
from queue import Queue
import traceback
from asapp.common import log, cli
import constants

class ModelServer:
    def __init__(self, client, release, baseline):
        self._release = release
        self._baseline = baseline
        self._client = client

        if self._client == 'condor':
            self._model = 'ccSklearnLogitEnsemble'
        elif self._client == 'spear':
            self._model = 'boostLogitW2VT300Prod'

    def get_model_from_s3(self):
        subprocess.call(['model_stash', '--bucket', 'asapp-models-dev','get', self._model])

    def start_server(self, queue):
        if client == 'condor':
            server = subprocess.Popen(['pythona',
                                       os.path.join(constants.ASAPP_SRS_ROOT, 'run_hierserver.py'),
                                       '--routing-json', os.path.join(constants.ASAPP_COMCAST_SRS_ROOT, 'routing.json'),
                                       '--model-name', self._model,
                                       '--business-logic', os.path.join(constants.ASAPP_COMCAST_SRS_ROOT, 'business_logic'),
                                       '-p', '9999',
                                       '-l', 'DEBUG'])
        elif client == 'spear':
            server = subprocess.Popen(['pythona',
                             os.path.join(constants.ASAPP_SRS_ROOT, 'run_hierserver.py'),
                             '--known-good', os.path.join(constants.ASAPP_SPRINT_SRS_ROOT,'knowngood', 'knowngood.yaml'),
                             '--model-name', self._model])
        queue.put(server)

    def query_server(self):
        if self._client == 'condor':
            client_baseline = 'comcast_baseline'
        elif self._client == 'spear':
            client_baseline = 'spear_baseline'

        uniquekey = self._release + '_' + self._baseline
        final_file = uniquekey + '_observed.csv'
        subprocess.run(['pythona',
                        os.path.join(constants.ASAPP_SRS_ROOT, 'tools', 'hier_server_query.py'),
                         '--source', client_baseline,
                         '--host', 'localhost',
                         '--protocol', 'http',
                         '--port', '9999',
                         final_file])

    def run_and_query_server(self):
        queue = Queue()
        thread = threading.Thread(target=self.start_server,args=(queue,))
        thread.start()

        self.query_server()
        server = queue.get()
        server.terminate()

    def run(self):
        try:
            self.get_model_from_s3()
            self.run_and_query_server()
        except Exception as e:
            print("SKIPPING: " + self._release + "_baseline" + self._baseline)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)


def parse_args():
    aparser = argparse.ArgumentParser(description=__doc__)
    cli.add_logging_to_parser(aparser)

    aparser.add_argument('CLIENT', default=None, type=str, help='Name of the client')
    aparser.add_argument('RELEASE', default=None, type=str, help='Name of the model release')
    aparser.add_argument('BASELINE', default=None, type=str, help='Date of the baseline set to use')

    return aparser.parse_args()


if __name__ == '__main__':
    parsed_args = parse_args()
    client = parsed_args.CLIENT
    release = parsed_args.RELEASE
    baseline = parsed_args.BASELINE
    model_server = ModelServer(client, release, baseline)
    sys.exit(model_server.run())
