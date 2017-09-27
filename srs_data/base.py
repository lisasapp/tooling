from abc import ABCMeta, abstractmethod


class BaseTool(metaclass=ABCMeta):

    def run(self):
        self._validate_input()
        self._run_steps()

    @abstractmethod
    def _validate_input(input):
        pass

    @abstractmethod
    def _run_steps(self):
        pass
