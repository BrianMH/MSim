'''
test_spelltrace.py

Tests the Spell Trace Enhancement simulation framework.
'''
import pytest
import utils.env.spelltrace as spelltrace


# non-test element
def generate_default_output(diffDict: dict[str, int]):
    """
    Spits out the expected output dict but with all values set to zero. Saves a bunch of space as this
    sim needs quite a few tests that vary in many ways.
    """
    return {"totalTraceCost" : diffDict.get("totalTraceCost", 0),
            "innoTraceCost": diffDict.get("innoTraceCost", 0),
            "scrollTraceCost" : diffDict.get("scrollTraceCost", 0),
            "cssTraceCost" : diffDict.get("cssTraceCost", 0),
            "hammerTraceCost" : diffDict.get("hammerTraceCost", 0),
            "numFailedScrolls" : diffDict.get("numFailedScrolls", 0),
            "numFailedInnos" : diffDict.get("numFailedInnos", 0),
            "numFailedCSS" : diffDict.get("numFailedCSS", 0),
            "numFailedHammers" : diffDict.get("numFailedHammers", 0),
            "numPassedScrolls" : diffDict.get("numPassedScrolls", 0),
            "numPassedInnos" : diffDict.get("numPassedInnos", 0),
            "numPassedCSS" : diffDict.get("numPassedCSS", 0),
            "numPassedHammers" : diffDict.get("numPassedHammers", 0),
            "numGuildSaves" : diffDict.get("numGuildSaves", 0)}


def test_nofail_execution_nohammer():
    testFW = spelltrace.SpellTraceFramework()

    # attempt to run framework with baked in arguments
    expected = generate_default_output({"totalTraceCost" : 1600,
                                        "scrollTraceCost" : 1600,
                                        "numPassedScrolls" : 8})

    res = testFW.performTrial(8, 112, 1.0, 111, 1.0, 0, False, 0, 1.0, 200, 1.0, 1.0)
    assert res == expected, "Non-failures simulation did not produce the expected results."


def test_nofail_execution_withhammer():
    testFW = spelltrace.SpellTraceFramework()

    # bake in different set of args to test hammer usage
    expected = generate_default_output({"totalTraceCost" : 2002,
                                        "scrollTraceCost" : 2000,
                                        "hammerTraceCost" : 2,
                                        "numPassedScrolls" : 10,
                                        "numPassedHammers" : 2})
    res = testFW.performTrial(8, 112, 1.0, 111, 1.0, 0, True, 1, 1.0, 200, 1.0, 1.0)
    assert res == expected, "Non-failures simulation did not produce the expected results."


def test_absolute_guildsaved_trial():
    assert False