"""
test_hexastats.py

Performs some testing to make sure that both the hexastat object manipulated
in the framework and the framework itself are both consistent and make sense
in their results.
"""
from utils.env.hexastats import HexaStatCore, HexaStatFramework
from random import Random
from collections import defaultdict
from os import path, remove
import pytest
import pickle

# global consts
RAND_SEED = 101
MIN_COST = 10
MAX_COST = 50
TEST_PATH = "./test/temp.tmp"

# non-tests
def getSeededRand(curSeed: int):
    randObj = Random(curSeed)
    return randObj.random


def getForcedValRand(retVal: float):
    """ Produces a callable that always returns the given return value. """
    return (lambda : retVal)


def dictInit():
    """ Initializer for default dict that gets pickled. """
    return False


# First we can evaluate our core for reasonable return results
def test_core_random_max_level():
    curCore = HexaStatCore(rngFunc = getSeededRand(RAND_SEED))
    
    for _ in range(1, HexaStatCore.MAX_LEVEL):
        curCore.levelNode()
        assert curCore.primaryStatLevel <= 10, "Primary stat reached impossible level."
        assert curCore.secondStatLevel <= 10, "Secondary stat reached impossible level."
        assert curCore.thirdStatLevel <= 10, "Third stat reached impossible level."

    assert curCore.level == 20, "Core could not reach maximum level."
    assert sum([curCore.primaryStatLevel, curCore.secondStatLevel, curCore.thirdStatLevel])-3 == 19, "Total accumulated levels must be 19 at max stage node."


def test_core_random_max_level_exception():
    curCore = HexaStatCore(rngFunc = getSeededRand(RAND_SEED))

    with pytest.raises(Exception):
        for _ in range(HexaStatCore.MAX_LEVEL):
            curCore.levelNode()
            assert curCore.primaryStatLevel <= 10, "Primary stat reached impossible level."
            assert curCore.secondStatLevel <= 10, "Secondary stat reached impossible level."
            assert curCore.thirdStatLevel <= 10, "Third stat reached impossible level."


def test_core_fixed_leveling():
    """ If return is fixed, then single stat should continously level 9 times and then likewise for the second and the third is left at level 2. """
    curCore = HexaStatCore(rngFunc = getForcedValRand(0.00))

    # first stat
    leveledStat = None
    lastLevel = None
    for _ in range(1, HexaStatCore.MAX_STAT_LEVEL):
        curCore.levelNode()

        if leveledStat is None:
            for attrName in ["primary", "second", "third"]:
                if getattr(curCore, attrName + "StatLevel") != HexaStatCore.INIT_LEVEL:
                    leveledStat = attrName + "StatLevel"

            assert leveledStat is not None, "Could not detect a leveled value following node leveling"
            lastLevel = getattr(curCore, leveledStat)
        else:
            assert getattr(curCore, leveledStat) > lastLevel
            lastLevel = getattr(curCore, leveledStat)

    # then second stat
    leveledStat = None
    lastLevel = None
    for _ in range(1, HexaStatCore.MAX_STAT_LEVEL):
        curCore.levelNode()

        if leveledStat is None:
            for attrName in ["primary", "second", "third"]:
                if getattr(curCore, attrName + "StatLevel") not in {1, HexaStatCore.MAX_STAT_LEVEL}:
                    leveledStat = attrName + "StatLevel"

            assert leveledStat is not None, "Could not detect a leveled value following node leveling"
            lastLevel = getattr(curCore, leveledStat)
        else:
            assert getattr(curCore, leveledStat) > lastLevel
            lastLevel = getattr(curCore, leveledStat)

    # then final stat can only level once
    curCore.levelNode()

    for attrName in ["primary", "second", "third"]:
        if getattr(curCore, attrName + "StatLevel") not in {1, HexaStatCore.MAX_STAT_LEVEL}:
            leveledStat = attrName + "StatLevel"

    assert leveledStat is not None, "Could not detect final leveled value following node leveling"
    lastLevel = getattr(curCore, leveledStat)
    assert curCore.level == 20, "Could not reach max level from enhancements"
    assert sum([curCore.primaryStatLevel, curCore.secondStatLevel, curCore.thirdStatLevel])-3 == 19, "Total accumulated levels must be 19 at max stage node."


def test_core_reset():
    curCore = HexaStatCore(rngFunc = getSeededRand(RAND_SEED))

    # test all points of reset
    for resLevel in range(HexaStatCore.MIN_RESET_LEVEL, HexaStatCore.MAX_LEVEL+1):
        for _ in range(1, resLevel):
            curCore.levelNode()
        curCore.resetNode()
    
        # make sure everything back to beginning
        assert curCore.primaryStatLevel == 1, "Did not reset primary level."
        assert curCore.secondStatLevel == 1, "Did not reset secondary level."
        assert curCore.thirdStatLevel == 1, "Did not reset other secondary stat level."
        assert curCore.level == 1, "Did not reset node level."


def test_core_framework_no_limit():
    curFw = HexaStatFramework(RAND_SEED)

    # Attempt test. Should be between init_cost and final_cost
    res = curFw.performTrial(1, "", 0)
    assert MIN_COST * 19 <= res["totalFragCost"] <= MAX_COST*19, "Cost not between realistic minimum/maximum"
    assert res["numResets"] == 0, "Expected 0 resets from a trial target of 1"
    assert res["totalEnhances"] == 19, "Expected 19 total enhancements from a trial target of 1"


def test_core_framework_with_limit(min_lim: int = 10, max_lim: int = 1000, interval: int = 50):
    curFw = HexaStatFramework(RAND_SEED)

    # Attempt test with non-zero limit. Should limit total usage of frag cores
    for maxLim in range(min_lim, max_lim + 1, interval):
        res = curFw.performTrial(1, "", maxLim)

        # Then enforce restriction
        assert res["totalFragCost"] <= maxLim, "Cost was not between expected maximum"
        assert res["numResets"] == 0, "Expected 0 resets from a trial target of 1"
        if min_lim >= MIN_COST:
            assert res["totalEnhances"] >= 1, "Expected at least one enhancement from given initial cost."


@pytest.mark.parametrize("test_lim", [100, 500, 1000, 1500, 2000])
@pytest.mark.usefixtures("fileCleaner")
def test_core_framework_with_policy_limit(test_lim: int):
    # Create fake dict that forces resets at level 10
    fakeDict = defaultdict(dictInit)
    for nodeLevel in range(HexaStatCore.MIN_RESET_LEVEL, HexaStatCore.MAX_LEVEL+1):
        for primStatLevel in range(1, HexaStatCore.MAX_STAT_LEVEL+1):
            fakeDict[(nodeLevel, primStatLevel)] = True # force reset at level 10 no matter what

    # Write to temp
    with open(TEST_PATH, 'wb') as outFile:
        pickle.dump(fakeDict, outFile)

    # Then attempt to check for this enforcement
    curFw = HexaStatFramework(RAND_SEED)
    res = curFw.performTrial(1, TEST_PATH, test_lim)
    assert res["totalFragCost"] <= test_lim, "Expected test to stay within the erda fragment limit"
    assert res["primaryLevel"]+res["secondaryLevel"]+res["thirdLevel"]-3 <= 10, "Test cannot level more than 10 times due to construct"
    if test_lim >= MIN_COST:
        assert res["totalEnhances"] >= 1, "Expected at least one enhancement from given limit cost"


@pytest.fixture
def fileCleaner():
    """ Cleans up files after the tests that use policies """
    yield
    if path.isfile(TEST_PATH):
        remove(TEST_PATH)