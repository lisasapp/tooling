import os
import subprocess
from git import Repo
from srs_data_management.evaluate_model import EvaluateModel
from srs_data_management import constants


class GenerateBaselineReport:

    def __init__(self, config):
        self._config = config
        self._client = config['client']

        metrics_config = config['metrics']
        self._baseline = metrics_config['metric']['baseline']
        self._evaluations = metrics_config['metric']['evaluation']
        # TODO: change this later to loop through taglevel instead of just indexing first
        self._releases = self._evaluations[0]['releases']
        self._current_dir = os.path.dirname(os.path.realpath(__file__))

    def checkout_model_repos(self, release):
        gasapp = Repo(constants.ASAPP_SRS_ROOT)
        gasapp.git.checkout(release)

        gprodml = Repo(constants.ASAPP_PRODML_ROOT)
        gprodml.git.checkout(release)

        gmleng = Repo(constants.ASAPP_MLENG_ROOT)
        gmleng.git.checkout(release)

        if self._client == 'condor':
            gclient = Repo(constants.ASAPP_COMCAST_SRS_ROOT)
        elif self._client == 'spear':
            gclient = Repo(constants.ASAPP_SPRINT_SRS_ROOT)
        gclient.git.checkout(release)

    def download_and_query_model(self, release):
        script =  os.path.join(os.path.dirname(os.path.realpath(__file__)), 'download_and_query_model.sh')
        subprocess.run([script, self._client, release, self._baseline])

    def query_historic_ami(self, release):
        # TODO: query using the historic AMI tool
        raise NotImplementedError

    def run(self):
        try:
            evaluater = EvaluateModel(self._config)
            for release in self._releases:
                print("-- checkout repos --")
                self.checkout_model_repos(release)
                print("-- download and query model --")
                self.download_and_query_model(release)
                # TODO: add check for whether historic release is available

            self.checkout_model_repos('master')
            for evaluation in self._evaluations:
                print("-- evaluate model --")
                for release in evaluation['releases']:
                    evaluater.run(release, evaluation['taglevel'])
        except Exception as e:
            print("ERROR encountered: ", e)

        self.checkout_model_repos('master')
