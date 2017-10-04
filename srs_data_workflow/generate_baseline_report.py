import os
import subprocess
from git import Repo
from srs_data_workflow.evaluate_model import EvaluateModel
from srs_data_workflow import constants

class GenerateBaselineReport:


    def __init__(self, config):
        self._config = config['metrics']
        # change this later to loop through instead of just indexing first
        self._baseline = self._config['metric']['baseline']
        self._evaluations = self._config['metric']['evaluation']
        self._releases = self._evaluations[0]['releases']

        self._current_dir = os.path.dirname(os.path.realpath(__file__))


    def checkout_model_repos(self, release):
        gasapp = Repo(constants.ASAPP_SRS_ROOT)
        gasapp.git.checkout(release)

        gprodml = Repo(constants.ASAPP_PRODML_ROOT)
        gprodml.git.checkout(release)

        gmleng = Repo(constants.ASAPP_MLENG_ROOT)
        gmleng.git.checkout(release)

        gcomcast = Repo(constants.ASAPP_COMCAST_SRS_ROOT)
        gcomcast.git.checkout(release)


    def download_and_query_model(self, release):
        script =  os.path.join(os.path.dirname(os.path.realpath(__file__)), 'download_and_query_model.sh')
        subprocess.run([script, release, self._baseline])


    def run(self):
        try:
            evaluater = EvaluateModel(self._config)
            for release in self._releases:
                print("-- checkout repos --")
                self.checkout_model_repos(release)

                print("-- download and query model --")
                self.download_and_query_model(release)

            self.checkout_model_repos('master')
            for evaluation in self._evaluations:
                print("-- evaluate model --")
                for release in evaluation['releases']:
                    evaluater.run(release, evaluation['taglevel'])
        except Exception as e:
            print("ERROR encountered: ", e)

        self.checkout_model_repos('master')
