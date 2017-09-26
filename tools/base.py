from abc import ABCMeta, abstractmethod


class BaseTool(metaclass=ABCMeta):

    @abstractmethod
    def _validate_input(input):
        pass

    @abstractmethod
    def _run_steps(self):
        pass
