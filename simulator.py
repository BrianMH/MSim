"""
Simulator.py

Harness for performing model simulation. Frameworks for simulating are
expected to have an unknown number of desired parameters along with an
explanation of what is expected for each entry.
"""
import utils.framework as framework
import utils.env

class MarkovSim():
    def __init__(self):
        self.curFramework : framework.Framework = framework.Framework()

    def selectFramework(self, fwork: framework.Framework):
        """
        Changes the current simulation into another according to fwork specifications.
        """
        self.curFramework = fwork

    def simulate(self, numTrials: int, simArgs: dict) -> list:
        """
        Performs a simulation according to what is allowed by framework specifications. Only
        functions after a framework is selected.
        """
        if numTrials < 0:
            raise ValueError("Number of trials must be a positive integer greater than 0.")

        resList = list()
        for _ in range(numTrials):
            resList.append(self.curFramework.performTrial(**simArgs))

        return resList

    @staticmethod
    def announceFrameworkArgs(fwork: framework.Framework):
        """
        Presents user legible info about what a given framework expects as arguments for
        a proper simulation trial.
        """
        print("Current FW - {}\n\n{}".format(fwork.__class__.__name__, fwork.announceSelf()))


if __name__ == "__main__":
    print(utils.env.__all__)