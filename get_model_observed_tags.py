#!/usr/bin/env pythona
import argparse
import os
import shutil
import sys
import subprocess
import threading
import signal
from queue import Queue

import traceback

from asapp.common import log, cli
from asapp.common import config

def parse_args(args):
    aparser = argparse.ArgumentParser(description=__doc__)
    cli.add_logging_to_parser(aparser)

    aparser.add_argument('RELEASE', default=None, type=str, help='Name of the model release')
    aparser.add_argument('BASELINE', default=None, type=str, help='Date of the baseline set to use')

    return aparser.parse_args()


def get_model_from_s3(modelname):
    subprocess.call(['model_stash', '--bucket', 'asapp-models-dev','get', modelname])

def start_server(modelname, queue):
    #inputArgs = [
    #    '--routing-json', config.env_vars['ASAPP_' + CLIENT_NAME + '_SRS_ROOT'] + '/routing.json',
    #    '--model-name', modelname,
    #    '--business-logic', config.env_vars['ASAPP_' + CLIENT_NAME + '_SRS_ROOT'] + '/business_logic',
    #    '-p', '9999',
    #    '-l', 'DEBUG'
    #]
    #aparser = run_hiernado_parser()
    #args = aparser.parse_args(inputArgs)
    #run_hiernado(args)
    server = subprocess.Popen(['pythona',
                     config.env_vars['ASAPP_SRS_ROOT'] + '/run_hierserver.py',
                     '--routing-json', config.env_vars['ASAPP_COMCAST_SRS_ROOT'] + '/routing.json',
                     '--model-name', modelname,
                     '--business-logic', config.env_vars['ASAPP_COMCAST_SRS_ROOT'] + '/business_logic',
                     '-p', '9999',
                     '-l', 'DEBUG'])
    queue.put(server)

def query_server(uniquekey):
    final_file = uniquekey + '_observed.csv'
    subprocess.run(['pythona',
                     config.env_vars['ASAPP_SRS_ROOT'] + '/tools/hier_server_query.py',
                     '--source', 'comcast_baseline',
                     '--host', 'localhost',
                     '--protocol', 'http',
                     '--port', '9999',
                     final_file])


def run_and_query_server(modelname, release, baseline):
    queue = Queue()
    thread = threading.Thread(target=start_server,args=(modelname,queue))
    thread.start()
    uniquekey = release + '_' + baseline
    query_server(uniquekey)
    server = queue.get()
    server.terminate()

def run(args):
    parsed_args = parse_args(args)
    release = parsed_args.RELEASE
    baseline = parsed_args.BASELINE
    model = 'ccSklearnLogitEnsemble'

    try:
        get_model_from_s3(model)
        run_and_query_server(model, release, baseline)

    except Exception as e:
        print("SKIPPING: " + release + "_baseline" + baseline)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)



if __name__ == '__main__':
    sys.exit(run(sys.argv[1:]))