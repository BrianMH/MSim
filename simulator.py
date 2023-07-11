"""
Simulator.py

Harness for performing model simulation. Frameworks for simulating are
expected to have an unknown number of desired parameters along with an
explanation of what is expected for each entry.
"""
import utils.framework as framework
import utils.env
from utils.env import * # pollutes environment, maybe better way?

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


if __name__ == "__main__":
    # welcome screen
    print("The following are the list of environments currently available:")
    for envName, envDesc in utils.env.__envs__.items():
        print("{: >15}\t\t{}".format(envName, envDesc))

    # prompt user for specific simulation
    userIn = ""
    while userIn not in utils.env.__envs__:
        userIn = input("Select environment by name: ")

    # report back with the expected inputs and attempt to find the relevant framework
    curSim = MarkovSim()
    chosenFW = None
    userDefinedModule = locals()[userIn]
    for className in dir(userDefinedModule):
        relAttr = getattr(userDefinedModule, className)
        if isinstance(relAttr, type) and issubclass(relAttr, framework.Framework) and relAttr != framework.Framework:
            chosenFW = relAttr()
    
    # finally select framework if found
    if chosenFW is None:
        raise LookupError("Framework subclass does not exist within given sim.")
    curSim.selectFramework(chosenFW)

    # Then proceed to evaluate what the user would like to do
    print(curSim.announceFrameworkArgs())
    print(curSim.announceSimOptions())
    userIn = ""
    while not userIn.isnumeric() or not (1 <= int(userIn) <= curSim.MAX_OPTS):
        userIn = input("Select operation for sim (1-{}): ".format(curSim.MAX_OPTS))