#!/usr/bin/env pythona
import argparse
import sys
import subprocess
import threading
from queue import Queue
import traceback
from asapp.common import log, cli
from paths import *


class ModelServer:
    def __init__(self, release, baseline, model):
        self._release = release
        self._baseline = baseline
        self._model = model


    def get_model_from_s3(self):
        subprocess.call(['model_stash', '--bucket', 'asapp-models-dev','get', self._model])


    def start_server(self, queue):
        server = subprocess.Popen(['pythona',
                         ASAPP_SRS_ROOT + '/run_hierserver.py',
                         '--routing-json', ASAPP_COMCAST_SRS_ROOT + '/routing.json',
                         '--model-name', self._model,
                         '--business-logic', ASAPP_COMCAST_SRS_ROOT + '/business_logic',
                         '-p', '9999',
                         '-l', 'DEBUG'])
        queue.put(server)


    def query_server(self):
        uniquekey = self._release + '_' + self._baseline
        final_file = uniquekey + '_observed.csv'
        subprocess.run(['pythona',
                        ASAPP_SRS_ROOT + '/tools/hier_server_query.py',
                         '--source', 'comcast_baseline',
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

    aparser.add_argument('RELEASE', default=None, type=str, help='Name of the model release')
    aparser.add_argument('BASELINE', default=None, type=str, help='Date of the baseline set to use')

    return aparser.parse_args()


if __name__ == '__main__':
    parsed_args = parse_args()
    release = parsed_args.RELEASE
    baseline = parsed_args.BASELINE
    model = 'ccSklearnLogitEnsemble'

    model_server = ModelServer(release, baseline, model)
    sys.exit(model_server.run())
