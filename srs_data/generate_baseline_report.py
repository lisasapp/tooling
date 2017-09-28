#!/usr/bin/env pythona
import os
import shutil
import subprocess

from git import Repo

from srs_data.base import BaseTool
from srs_data.evaluate_model import EvaluateModel
from srs_data.constants import *


class GenerateBaselineReport(BaseTool):

    def __init__(self, config):
        self._config = config['metrics']['metric'][0]
        self._baseline = self._config['baseline']
        self._releases = self._config['releases']
        self._download_and_query_model_script = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'download_and_query_model.sh'
        )

    def checkout_model_repos(self, release):
        gasapp = Repo(ASAPP_SRS_ROOT)
        gasapp.git.checkout(release)

        gprodml = Repo(ASAPP_PRODML_ROOT)
        gprodml.git.checkout(release)

        gmleng = Repo(ASAPP_MLENG_ROOT)
        gmleng.git.checkout(release)

        gcomcast = Repo(ASAPP_COMCAST_SRS_ROOT)
        gcomcast.git.checkout(release)

        # Copy business logic into correct directory
        temp_dir = ASAPP_ROOT + '/business_logic/'
        business_destination = temp_dir + release
        if not os.path.exists(business_destination):
            shutil.copytree(temp_dir, business_destination)

    def run(self):
        try:
            evaluater = EvaluateModel(self._baseline)
            for release in self._releases:
                print("-- checkout repos --")
                self.checkout_model_repos(release)

                print("-- download and query model --")
                self._download_and_query_model(release)

                print("-- evaluate model --")
                evaluater.run(release)
        except Exception as e:
            print("ERROR encountered: ", e)

        self.checkout_model_repos('master')

    def _download_and_query_model(self, release):
        subprocess.call([
            self._download_and_query_model_script,
            release,
            self._baseline
        ])
