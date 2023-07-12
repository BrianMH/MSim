"""
Simulator.py

Harness for performing model simulation. Frameworks for simulating are
expected to have an unknown number of desired parameters along with an
explanation of what is expected for each entry.
"""
import utils.framework as framework

class MarkovSim():
    MAX_OPTS = 2 # for now only two functions

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
            resList.append(self.curFramework.checkAndPerformTrial(simArgs))

        return resList
    
    def gridSearch(self, numTrials: int, gridArgs: dict, simArgs: dict) -> dict:
        """
        Performs a grid search across all parameters present in gridArgs and appends simArgs as
        constant parameters. Note that the total search space is equialent to the cartesian product
        of all key-value pairs in gridArgs.
        """
        pass

    def getFrameworkArgs(self) -> list[str]:
        """
        Returns the framework expected arguments as a list of strings.
        """
        return self.curFramework.getArgs()
    
    def getFrameworkArgType(self) -> dict[str, type[int | float | str]|tuple[type[int | float | str],...]]:
        """
        Returns the framework's expected arguments along with the requisite types.
        """
        return self.curFramework.getArgTypes()
    
    def checkValidUserArgs(self, userDict: dict) -> bool:
        """
        Returns whether or not the passed in user dict is a valid arg dict.
        """
        return False if len(self.curFramework.checkInvalidArgs(userDict)) > 0 else True

    def announceFrameworkArgs(self) -> str:
        """
        Presents user legible info about what a given framework expects as arguments for
        a proper simulation trial.
        """
        return "\nCurrent FW - {}\n\n{}".format(self.curFramework.__class__.__name__, self.curFramework.announceSelf())
    
    def announceSimOptions(self) -> str:
        """
        Presents user legible info about what this sim can do. For now, all it does is either perform a single
        trial analysis or create a grid sweep framework using the simulator.
        """
        return ("Available Options:\n" + 
                "\t1) Parameter Sweep\n" +
                "\t2) Fixed Parameter Simulation\n")
