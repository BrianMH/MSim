"""
test_framework.py

Performs some basic testing with the most basic functionality of a non-specific
framework to ensure proper functionality.
"""
import utils.framework as framework
import pytest 


def test_default_execution():
    testFW = framework.Framework()

    with pytest.raises(Exception):
        testFW.performTrial(None, None, None)


def test_arg_mapping_empty():
    # set up process
    testFW = framework.Framework()
    inArgs = {"EXAMPLE1" : 1,
                "EXAMPLE2" : 2.0,
                "EXAMPLE3" : 1.3}
    copArgs = inArgs.copy()
    assert copArgs == testFW.mapArgs(inArgs), "Trivial (empty) mapping did not leave inArgs unchanged."


def test_arg_mapping_nonempty():
    # set up process
    testFW = framework.Framework()
    inArgs = {"EXAMPLE1" : 1,
                "EXAMPLE2" : 2.0,
                "EXAMPLE3" : 1.3}

    # test non-basic mapping
    testFW.ARG_MAPPING = {"EXAMPLE1": "ex1",
                            "EXAMPLE2": "ex2",
                            "EXAMPLE3": "ex3"}
    
    # expected return and eval
    expected = {"ex1" : 1,
                "ex2" : 2.0,
                "ex3" : 1.3}
    
    assert expected == testFW.mapArgs(inArgs), "Mapping was incorrectly produced"


def test_check_invalid_args():
    # set up fw again
    testFW = framework.Framework()
    inArgs = {"EXAMPLE1" : 1,
                "EXAMPLE2" : 1,
                "EXAMPLE3" : "incorrect"}
    
    # multiple errors
    assert set(testFW.checkInvalidArgs(inArgs)) == {"EXAMPLE2", "EXAMPLE3"}


def test_check_invalid_missing_args():
    testFW = framework.Framework()
    inArgs = {"EXAMPLE1" : 1,
                "EXAMPLE2" : 2.0}
    
    with pytest.raises(Exception):
        testFW.checkInvalidArgs(inArgs)


def test_check_invalid_extra_args():
    testFW = framework.Framework()
    inArgs = {"EXAMPLE1" : 1,
                "EXAMPLE2" : 1,
                "EXAMPLE3" : 1,
                "extra" : 4}
    
    with pytest.raises(Exception):
        testFW.checkInvalidArgs(inArgs)