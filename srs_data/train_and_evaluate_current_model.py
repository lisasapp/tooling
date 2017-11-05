#!/usr/bin/env pythona
import sys
import argparse
from ruamel import yaml
import os
import argparse
import sys
import subprocess
import threading
from queue import Queue
import traceback
from asapp.common import log, cli
import constants


from asapp.common import cli

def get_parser():
    aparser = cli.ASAPPArgumentParser(description=__doc__)
    aparser.add_argument('modelname', nargs='?', default='boostLogitW2VT300Prod', type=str, help='Model to pull and evaluate')
    return aparser

def start_server(self, queue):
    server = subprocess.Popen(['pythona',
                     os.path.join(constants.ASAPP_SRS_ROOT, 'run_hierserver.py'),
                     '--model-name', self._model,
                     '--business-logic', os.path.join(constants.ASAPP_COMCAST_SRS_ROOT, 'business_logic'),
                     '-p', '9999',
                     '-l', 'DEBUG'])
    queue.put(server)

def query_server(self):
    uniquekey = self._release + '_' + self._baseline
    final_file = uniquekey + '_observed.csv'
    subprocess.run(['pythona',
                    os.path.join(constants.ASAPP_SRS_ROOT, 'tools', 'hier_server_query.py'),
                     '--source', 'spear_baseline',
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


def run():
    parsed_args = get_parser().parse_args()
    parsed_args.modelname
    run_and_query_server()



if __name__ == '__main__':
    sys.exit(run())