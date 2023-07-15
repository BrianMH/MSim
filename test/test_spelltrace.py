'''
test_spelltrace.py

Tests the Spell Trace Enhancement simulation framework.
'''
import pytest
import utils.env.spelltrace as spelltrace

# global seed setting
RAND_SEED = 100

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
    testFW = spelltrace.SpellTraceFramework(RAND_SEED)

    # attempt to run framework with baked in arguments
    expected = generate_default_output({"totalTraceCost" : 1600,
                                        "scrollTraceCost" : 1600,
                                        "numPassedScrolls" : 8})

    res = testFW.performTrial(8, 112, 1.0, 111, 1.0, 0, False, 0, 1.0, 200, 1.0, 1.0)
    assert res == expected, "Non-failures simulation did not produce the expected results."


def test_nofail_execution_withhammer():
    testFW = spelltrace.SpellTraceFramework(RAND_SEED)

    # bake in different set of args to test hammer usage
    expected = generate_default_output({"totalTraceCost" : 2002,
                                        "scrollTraceCost" : 2000,
                                        "hammerTraceCost" : 2,
                                        "numPassedScrolls" : 10,
                                        "numPassedHammers" : 2})
    res = testFW.performTrial(8, 112, 1.0, 111, 1.0, 0, True, 1, 1.0, 200, 1.0, 1.0)
    assert res == expected, "Non-failures simulation did not produce the expected results."


@pytest.mark.parametrize('num_slots', [1, 2, 100])
@pytest.mark.parametrize('use_hammer', [False, True])
def test_absolute_guildsaved_trial(num_slots: int, use_hammer: bool, scroll_cost: int = 201):
    testFW = spelltrace.SpellTraceFramework(RAND_SEED)

    # bake in different set of args to test guild slot saving
    res = testFW.performTrial(num_slots, 1, 1.0, 1, 1.0, (num_slots + use_hammer*2) + 1, use_hammer, 0, 1.0, scroll_cost, 0.1, 1.0)
    assert res['numFailedScrolls'] == res['numGuildSaves'] # 100% guild save
    assert res['innoTraceCost'] == res['cssTraceCost'] == res['hammerTraceCost'] == 0 # no costs aside from scrolls
    assert res['totalTraceCost'] >= num_slots * scroll_cost # cost must be at least equal to 100% scroll pass rate


@pytest.mark.parametrize('num_slots', [1, 2, 100])
@pytest.mark.parametrize('use_hammer', [False, True])
def test_absolute_css_trial(num_slots: int, use_hammer: bool, scroll_cost: int = 201):
    testFW = spelltrace.SpellTraceFramework(RAND_SEED)

    # now test scroll usage with non-100% scrolls but 100% css
    res = testFW.performTrial(num_slots, 1, 1.0, 1, 1.0, (num_slots + use_hammer*2) + 1, use_hammer, 0, 1.0, scroll_cost, 0.1, 0.0)
    assert res['numFailedScrolls'] == res['numPassedCSS'] # only css are used
    assert res['innoTraceCost'] == res['hammerTraceCost'] == 0 # no costs aside from scrolls/css
    assert res['totalTraceCost'] >= num_slots * scroll_cost

@pytest.mark.parametrize('num_slots', [1, 2, 5])
@pytest.mark.parametrize('use_hammer', [False, True])
def test_absolute_inno_trial(num_slots: int, use_hammer: bool, scroll_cost: int = 201):
    testFW = spelltrace.SpellTraceFramework(RAND_SEED)

    # now test execution using inno immediately after any failure
    res = testFW.performTrial(num_slots, 1, 1.0, 1, 1.0, 0, use_hammer, 0, 1.0, scroll_cost, 0.1, 0.0)
    assert res['numFailedScrolls'] == res['numPassedInnos']
    assert res['cssTraceCost'] == res['hammerTraceCost'] == 0
    assert res['totalTraceCost'] >= num_slots * scroll_cost


"""
Coverage for performTrial:

Branches on:
    num_slots: 0, 1, >1
    inno_tol: 0, 0 < x < num_slots, num_slots (x > num_slots)
    use_hammer: true, false
    scroll_rate: 0 < x < 1.0, 1.0         => 0 implies infinite loop so untested here
    gs_rate: 0, >0
"""
@pytest.mark.parametrize('num_slots', [0, 1, 4])
@pytest.mark.parametrize('inno_tol', [0, 1, 4])
@pytest.mark.parametrize('use_hammer', [False, True])
@pytest.mark.parametrize('scroll_rate', [0.1, 0.5, 1.0])
@pytest.mark.parametrize('gs_rate', [0.00, 0.04, 1.0])
def test_complete_coverage(num_slots: int, inno_tol: int, use_hammer: bool, scroll_rate: float, gs_rate: float, scroll_cost: int = 201):
    testFW = spelltrace.SpellTraceFramework(RAND_SEED)

    # now test with given specifications for coverage purposes
    res = testFW.performTrial(num_slots, scroll_cost, 1.0, scroll_cost, 1.0, inno_tol, use_hammer, scroll_cost, 1.0,
                              scroll_cost, scroll_rate, gs_rate)
    assert res['totalTraceCost'] >= num_slots * scroll_cost
