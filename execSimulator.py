"""
execSimulator.py

Uses the simulator interface
"""
from typing import Callable
from simulator import MarkovSim
from utils import framework
import utils.env
from utils.env import * # pollutes environment, maybe better way?

def executeWelcome():
    '''
    Just prints the message expected form executing the program. Produces a simple introduction
    along with the environments currently available.
    '''
    # show all posible environments available for use
    print("The following are the list of environments currently available:")
    for envName, envDesc in utils.env.__envs__.items():
        print("{: >15}\t\t{}".format(envName, envDesc))

def promptUserForEnv() -> framework.Framework:
    '''
    Prompts the user for an environment from one of the envs in utils.env. It then returns an
    instantiated framework for the environment.
    '''
    # prompt user for specific simulation
    userIn = ""
    while userIn not in utils.env.__envs__:
        userIn = input("Select environment by name: ")

    # report back with the expected inputs and attempt to find the relevant framework
    chosenFW = None
    userDefinedModule = globals()[userIn]
    for className in dir(userDefinedModule):
        relAttr = getattr(userDefinedModule, className)
        if isinstance(relAttr, type) and issubclass(relAttr, framework.Framework) and relAttr != framework.Framework:
            chosenFW = relAttr()

    # finally select framework if found
    if chosenFW is None:
        raise LookupError("Framework subclass does not exist within given sim.")
    return chosenFW

def generateGridSearchFunctor(curSim: MarkovSim) -> Callable:
    """
    Generates a callable functor for a prepared grid search parameters after
    prompting user for specific args.
    """
    print("Select whether or not the simulation will be dynamic on the following arguments: (y\\n)")
    for curArgStr in curSim.getFrameworkArgs():
        pass

    raise NotImplementedError()

def generateFixedParamFunctor(curSim: MarkovSim) -> Callable:
    """
    Generates a callable functor for a fixed parameter simulation after prompting
    user for specific args.
    """
    print("Please enter desired parameter values for the following arguments: ")
    argDict : dict = {argStr:0 for argStr in curSim.getFrameworkArgs()}
    while not curSim.checkValidUserArgs(argDict):
        print("\nEnter values according to specified types...\n")
        for curArgStr, argType in curSim.getFrameworkArgType().items():
            # grab lease restrictive type from tuple
            if isinstance(argType, tuple):
                curType = argType[0]
            else:
                curType = argType
            
            # grab input and convert
            userInput = input("{: >15} : ".format(curArgStr))
            if curType == bool: # bool must be explicitly converted from string entry
                match userInput.strip():
                    case "y":
                        argDict[curArgStr] = True
                    case "n":
                        argDict[curArgStr] = False
                    case _:
                        raise ValueError("Boolean values only take y/n inputs.")
            else: # attempt implicit conversion if not bool
                argDict[curArgStr] = curType(userInput)
    
    # generate function from argDict
    return lambda numTrials : curSim.simulate(numTrials, argDict)

def promptUserForOption(curSim: MarkovSim) -> Callable:
    """
    Takes in the current simulation that has been adjusted to the proper framework and returns
    an functor that produces the values the user requested. All parameters are bound to the
    function in the return so it is parameterless.
    """
    # Then proceed to evaluate what the user would like to do
    print(curSim.announceFrameworkArgs())
    print(curSim.announceSimOptions())
    userIn = ""
    while not userIn.isnumeric() or not (1 <= int(userIn) <= curSim.MAX_OPTS):
        userIn = input("Select operation for sim (1-{}): ".format(curSim.MAX_OPTS))

    # Prompt arguments that will be static vs changing if grid search
    match int(userIn):
        case 1:
            resFunc = generateGridSearchFunctor(curSim)
        case 2:
            resFunc = generateFixedParamFunctor(curSim)
        case _:
            raise ValueError("Operation does not exist.")
        
    # bind number of trials and return
    return bindNumTrialsToFunctor(resFunc)
        
def bindNumTrialsToFunctor(resFunc: Callable) -> Callable:
    """
    Binds the number of trials per test to the callable function based on user input.
    """
    userInput = ""
    while not userInput or not int(userInput) > 0:
        userInput = input("\nEnter number of times for each trial to execute: ")

    return lambda : resFunc(int(userInput))

# Interactive loop
if __name__ == "__main__":
    import pickle

    executeWelcome()
    curSim = MarkovSim()
    curSim.selectFramework(promptUserForEnv())
    resFunc = promptUserForOption(curSim)
    results = resFunc()

    # saves results from execution in a file
    with open("res_output.pkl", 'wb') as outFile:
        pickle.dump(results, outFile)