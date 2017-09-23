#!/usr/bin/env pythona
import os
import shutil
import subprocess

from git import Repo
from asapp.common import config
from workflow.evaluate_model import run as evaluate_model

from workflow.paths import *

class GenerateBaselineReport:

    def __init__(self, config):
        self._config = config['metrics']['metric'][0]
        self._baseline = self._config['baseline']
        self._releases = self._config['releases']

    def checkout_model_repos(self, release):
        gasapp = Repo(ASAPP_SRS_ROOT)
        gasapp.git.checkout(release)

        gprodml = Repo(ASAPP_PRODML_ROOT)
        gprodml.git.checkout(release)

        gmleng = Repo(ASAPP_MLENG_ROOT)
        gmleng.git.checkout(release)

        gcomcast = Repo(ASAPP_COMCAST_SRS_ROOT)
        gcomcast.git.checkout(release)

        # get the business
        temp_dir =  ASAPP_ROOT + '/business_logic/'
        business_destination = temp_dir + release
        if not os.path.exists(business_destination):
            shutil.copytree(temp_dir, business_destination)


    def run(self):
        try:
            for release in self._releases:
                print("-- checkout repos --")
                self.checkout_model_repos(release)

                print("-- download and query model --")
                script = os.path.dirname(os.path.realpath(__file__)) + '/download_and_query_model.sh'
                subprocess.call([script, release, self._baseline])

                print("-- evaluate model --")
                evaluate_model(release, self._baseline)
        except Exception as e:
            print("ERROR encountered: ", e)

        self.checkout_model_repos('master')