"""
test_hexastats.py

Performs some testing to make sure that both the hexastat object manipulated
in the framework and the framework itself are both consistent and make sense
in their results.
"""
from utils.env.hexastats import HexaStatCore, HexaStatFramework
from random import Random
import pytest

# global const
RAND_SEED = 101

# non-tests
def getSeededRand(curSeed: int):
    randObj = Random(curSeed)
    return randObj.random

def getForcedValRand(retVal: float):
    """ Produces a callable that always returns the given return value. """
    return (lambda : retVal)

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
