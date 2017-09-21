#!/usr/bin/env pythona
import os
import shutil
import subprocess

from git import Repo
from asapp.common import config
from evaluate_model import run as evaluate_model


class GenerateBaselineReport:

    def __init__(self, config):
        # pull config stuff
        # check to make sure all required fields are there blahblah
        temp_config = {
            'baseline': '20170828',
            'releases': [
                'ComcastSRS-2.18.0',
                'ComcastSRS-2.17.0',
                'ComcastSRS-2.16.8',
                'ComcastSRS-2.15.0',
                'ComcastSRS-2.14.1',
                'ComcastSRS-2.9.2',
                'ComcastSRS-2.8.3',
                'ComcastSRS-2.7.5',
                'ComcastSRS-2.6.4'
            ]
        }

        self._baseline = temp_config['baseline']
        self._releases = temp_config['releases']

    def checkout_model_repos(self, release):
        gasapp = Repo(config.env_vars['ASAPP_SRS_ROOT'])
        gasapp.git.checkout(release)

        gprodml = Repo(config.env_vars['ASAPP_PRODML_ROOT'])
        gprodml.git.checkout(release)

        gmleng = Repo(config.env_vars['ASAPP_MLENG_ROOT'])
        gmleng.git.checkout(release)

        gcomcast = Repo(config.env_vars['ASAPP_COMCAST_SRS_ROOT'])
        gcomcast.git.checkout(release)

        # get the business
        temp_dir = '/tmp/lisa/business_logic'
        business_destination = temp_dir + '/' + release
        if not os.path.exists(business_destination):
            shutil.copytree(temp_dir, business_destination)


    def run(self):
        for release in self._releases:
            print("-- checkout repos --")
            self.checkout_model_repos(release)

            print("-- download and query model --")
            subprocess.call(['/Users/lisa/ASAPPinc/tooling/download_and_query_model.sh', release, self._baseline])

            print("-- evaluate model --")
            evaluate_model(release, self._baseline)

        self.checkout_model_repos('master')