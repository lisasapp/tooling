from abc import ABCMeta, abstractmethod


class BaseTool(metaclass=ABCMeta):

    @property
    @abstractmethod
    def input_file(self):
        return None

    @abstractmethod
    def _validate_input(input):
        pass

    @abstractmethod
    def _run_steps(self):
        pass
