"""
test_markovsim.py

Tests the markov sim API using a dummy framework.
"""
from utils.framework import Framework
from simulator import MarkovSim
import pytest

class DummyFramework(Framework):
    # class vars
    ARG_TYPES : dict[str, type[int | float | str]|tuple[type[int | float | str],...]] = {"arg1": int,
                                                                                         "arg2": int}
    
    ARG_MAN = {"arg1" : "arg1",
               "arg2" : "arg2"}

    # class methods (basic implementation)
    def __init__(self):
        self.numExecutions = 0

    def performTrial(self, arg1, arg2):
        self.numExecutions += 1

        return {"numExecutions" : 1, "result" : arg1 + arg2,
                "iArg1": arg1, "iArg2": arg2}


def test_sim_framework_choosing():
    '''
    Checks if the framework properly instantiates itself within the simulation class
    '''
    curSim = MarkovSim()
    frameRef = DummyFramework()
    curSim.selectFramework(frameRef)

    # first make sure the framework is properly changed
    assert isinstance(curSim.curFramework, Framework), "Sanity check for dummy framework failed."

    # and ensure nothing has been run within the framework
    assert frameRef.numExecutions == 0, "Framework should not be run prior to a simulation."


def test_sim_framework_simulation_single_runs():
    '''
    Checks to make sure simulation runs are properly performed within the simulator.
    '''
    curSim = MarkovSim()
    frameRef = DummyFramework()
    curSim.selectFramework(frameRef)

    for curValue in range(1, 100):
        res = curSim.simulate(1, {"arg1":curValue, "arg2":curValue})
        assert len(res) == 1, "Should only contain one resultant dictionary per iteration."
        assert frameRef.numExecutions == curValue, "Framework should only be executing sim once."
        assert res[0]["result"] == curValue*2, "Did not generate proper output."


def test_sim_framework_simulation_variable_runs():
    '''
    Checks to make sure simulation runs are properly performed within the simulator, but this time
    with variable number of trials.
    '''
    curSim = MarkovSim()
    frameRef = DummyFramework()
    curSim.selectFramework(frameRef)

    totTrials = 0
    for curValue in range(1, 100):
        res = curSim.simulate(curValue, {"arg1":curValue, "arg2":curValue})
        totTrials += curValue

        assert len(res) == curValue, "Expected an output result list of size {}".format(curValue)
        assert frameRef.numExecutions == totTrials, "Framework should only be executing sim {} times".format(curValue)
        for resDict in res:
            assert resDict["result"] == curValue*2, "Did not generate proper output for contained result dict."


def test_sim_framework_grid_search_all_variadic():
    '''
    Makes sure that the grid search function passes the proper number of executions to the 
    simulate function. There are no static arguments this time.
    '''
    testInDict = {"arg1":(1, 2, 3), "arg2":(1, 5, 6)} # prod card : 3 x 3 = 9
    curSim = MarkovSim()
    frameRef = DummyFramework()
    curSim.selectFramework(frameRef)

    # now use grid search
    resDictCollection = curSim.gridSearch(1, testInDict, {})
    assert len(resDictCollection) == 9, "Expected number of results equivalent to cartesian product of input sizes."
    assert frameRef.numExecutions == 9, "Frame experienced more executions than necessary for operation."
    for resDictList in resDictCollection.values():
        assert len(resDictList) == 1, "Only one execution must be made per single call."

        resDict = resDictList[0]
        assert resDict['result'] == resDict['iArg1'] + resDict['iArg2'], "Improper output detected from given input arguments."
        assert resDict['numExecutions'] == 1, "Result should have only been executed once."


def test_sim_framework_grid_search_all_static():
    '''
    Makes sure that the grid search function passes the proper number of executions to the 
    simulate function. There are no variable arguments this time.
    '''
    testInDict = {"arg1":1, "arg2": 1} # prod card : |{0}| = 1
    curSim = MarkovSim()
    frameRef = DummyFramework()
    curSim.selectFramework(frameRef)

    # now use grid search
    resDictCollection = curSim.gridSearch(1, {}, testInDict)
    assert len(resDictCollection) == 1, "Expected number of results equivalent to cartesian product of input sizes."
    assert frameRef.numExecutions == 1, "Frame experienced more executions than necessary for operation."
    for resDictList in resDictCollection.values():
        assert len(resDictList) == 1, "Only one execution must be made per single call."

        resDict = resDictList[0]
        assert resDict['result'] == resDict['iArg1'] + resDict['iArg2'], "Improper output detected from given input arguments."
        assert resDict['numExecutions'] == 1, "Result should have only been executed once."


def test_sim_framework_dict_generator():
    '''
    Tests to make sure the dictionary generator works to produce proper cartesian product
    of inputs as the output dict.
    '''
    testInDict = {"A":(1,), "B":(4., 5.), "C":(True, False)}
    expected = [{"A":1, "B":4., "C":True},
                {"A":1, "B":4., "C":False},
                {"A":1, "B":5., "C":True},
                {"A":1, "B":5., "C":False}]
    
    # eval gen dict
    outList = list(MarkovSim.varDictGen(testInDict))
    assert len(outList) == len(expected), "Output contained improper cartesian product cardinality."
    for elem in expected:
        assert elem in outList, "Found unknown/missing dict in the output generator."
