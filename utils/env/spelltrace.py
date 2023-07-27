"""
SpellTraceFramework.py

Sets up a framework class type for spell trace simulation that is completely independent of
the item entity. User is expected to input all relevant information.

Stats will be irrelevant for now (since they can be computer after-the-fact using the evidence
of passes/fails.)

Note that if hammer % is set to 1.0 (always passes), then hammers will be applied prior to running
the algorithm. However, if the hammer % value is less than 1.0, then hammers will instead be applied
to the end. Further, note that all costs are in terms of spell traces.
"""
from ..framework import Framework as _FW
from random import Random as _Rand

class SpellTraceFramework(_FW):
    """
    A framework for calculating trials using spell traces.
    """

    # CLASS VAR PARAMETERS
    MAN_MSG = ("Spell Trace Enhancement framework. Provides the base framework needed to perform " +
               "enhancement of items using the available spell trace system. Constants for the " +
               "system are defined externally outside of classes for convenience.")
    
    ARG_TYPES : dict[str, type|tuple[type,...]] = {"Num Slots": int,
                                                   "CSS Cost": int,
                                                   "CSS %": float,
                                                   "Inno Cost": float,
                                                   "Inno %": float,
                                                   "Inno Fail Count": int,
                                                   "Use Hammer": bool,
                                                   "Hammer Cost": int,
                                                   "Hammer %": float,
                                                   "Scroll Cost": int,
                                                   "Scroll %": float,
                                                   "Guild Save %": float}
    
    ARG_MAN = {"Num Slots" : "The number of slots available for the item (prior to hammering)",
               "CSS Cost" : "Sets the cost of the clean slate scroll scroll",
               "CSS %" : "Sets the pass rate for the clean slate scroll (0.0 - 1.0)",
               "Inno Cost" : "Sets the cost of an innocence scroll",
               "Inno %": "Sets the pass rate for the innocence scroll (0.0 - 1.0)",
               "Inno Fail Count": "The number of lost slots to tolerate prior to forcing innocence use.",
               "Use Hammer": "Whether or not to use hammers on the item (y/n)",
               "Hammer Cost": "Sets the cost of a hammer",
               "Hammer %": "Sets the pass rate for the hammer (0.0 - 1.0)",
               "Scroll Cost": "Sets the cost of the current spell trace scroll being used",
               "Scroll %": "Sets the pass rate for the spell trace scroll (0.0 - 1.0)",
               "Guild Save %": "Sets the rate for at which the guild slot saving activates (0.00 - 0.04)"}
    
    # CLASS INTRINSICS
    ARG_MAPPING = {"Num Slots" : "eqpSlots",
                   "CSS Cost" : "cssCost",
                   "CSS %" : "cssRate",
                   "Inno Cost" : "innoCost",
                   "Inno %" : "innoRate",
                   "Inno Fail Count" : "innoAfterTol",
                   "Use Hammer" : "useHammer",
                   "Hammer Cost" : "hammerCost",
                   "Hammer %" : "hammerRate",
                   "Scroll Cost" : "scrollCost",
                   "Scroll %" : "scrollRate",
                   "Guild Save %" : "guildSaveRate"}

    # CLASS FUNCS
    def __init__(self, rSeed: int|None = None, greedyFinish: bool = True):
        """
        Sets up a simple framework for testing spell trace enhancement.

        Args:
            rSeed : A set seed for the randomizer used here
            greedyFinish : Determines whether or not to use inno tolerance following hamers near the end.
        """
        self.rng = _Rand(rSeed)
        self.random = self.rng.random
        self.greedyAfterInno = greedyFinish

    def performTrial(self, eqpSlots: int, cssCost: int, cssRate: float, innoCost: int, innoRate: float,
                     innoAfterTol: int, useHammer: bool, hammerCost: int, hammerRate: float, scrollCost: int,
                     scrollRate: float, guildSaveRate: float) -> dict:
        """
        Performs a trial simulation for an enhancement of an item with a given number of slots using a given
        set of parameters relating to item usage.

        Args:
            eqpSlots : number of slots to scroll
            cssCost : trace cost of css
            cssRate : pass rate of css
            innoCost : trace cost of inno scroll
            innoRate : pass rate of inno scroll
            innoAfter : failure tolerance before forced inno (implicitly all CSS after)
            useHammer : whether or not to hammer item in simulation
            hammerCost : trace cost of hammer
            hammerRate : pass rate of hammer
            scrollCost : trace cost of spell trace scroll being used
            scrollRate : pass rate of the spell trace scroll
            guildSaveRate : rate at which the guild slot saving skill can proc on item

        Returns:
            A dictionary with the following metrics as useful information for plotting:
                {"totalTraceCost", "innoTraceCost", "scrollTraceCost", "cssTraceCost",
                 "numFailedScrolls", "numFailedInnos", "numFailedCSS", "numFailedHammers",
                 "numPassedScrolls", "numPassedInnos", "numPassedCSS", "numPassedHammers",
                 "numGuildSaves"}
        """
        # Prepare our values for return
        innoCosts, scrollCosts, cssCosts, hammerCosts = 0, 0, 0, 0
        fScrolls, fInnos, fCSS, fHammers = 0, 0, 0, 0
        pScrolls, pInnos, pCSS, pHammers = 0, 0, 0, 0
        numGS = 0

        # Some properties that are used for keeping track of sim prog
        eqpHammers = False
        curPassed, curFailed = 0, 0
        totSlots = eqpSlots + 2 if useHammer else eqpSlots
        availSlots = eqpSlots
        
        # functor for resetting progress
        def resetState():
            nonlocal eqpHammers, curPassed, curFailed, availSlots
            eqpHammers = 0
            curPassed, curFailed = 0, 0
            availSlots = eqpSlots

        # Then proceed with simulation of spell trace enhancement
        while curPassed < totSlots:
            # enhance if possible
            if availSlots > 0:
                scrollPassed = (self.random() <= scrollRate)
                scrollCosts += scrollCost
                if scrollPassed:
                    availSlots -= 1
                    pScrolls += 1
                    curPassed += 1
                else:
                    guildSaved = (self.random() < guildSaveRate)
                    numGS += 1 if guildSaved else 0
                    availSlots -= 0 if guildSaved else 1
                    fScrolls += 1
                    curFailed  += 0 if guildSaved else 1

            # check if inno, hammer, or css has to be used
            if curFailed > innoAfterTol:
                # accumulate cost
                inProcCost, inProcFails = self.simulateForcePassedScroll(innoRate, innoCost)
                innoCosts += inProcCost
                fInnos += inProcFails
                pInnos += 1

                # reset state and restart process
                resetState()
            elif useHammer and (availSlots == 0 and eqpHammers < 2):
                # update values with used hammers
                eqpHammers += 1
                hammerCosts += hammerCost
                hammProcSucc = (self.random() < hammerRate)
                fHammers += (1-hammProcSucc)
                pHammers += hammProcSucc

                # Item slots + 2 but available slots scale only with passed hammers
                curFailed += (1-hammProcSucc)
                availSlots += hammProcSucc

                # Generally, once we start hammering, we no longer consider innocence scrolling,
                # but it can optionally be turned off (be warned this can increase the trial
                # horizon significantly!)
                if self.greedyAfterInno:
                    innoAfterTol += 1
            elif availSlots == 0 and curFailed > 0:
                # accumulate cost
                cssProcCost, cssProcFails = self.simulateForcePassedScroll(cssRate, cssCost)
                cssCosts += cssProcCost
                fCSS += cssProcFails
                pCSS += 1

                # adjust state to reflect CSS passing
                availSlots += 1
                curFailed -= 1

        # nearly organize all values into legible return dict
        return {"totalTraceCost" : innoCosts + cssCosts + scrollCosts + hammerCosts, 
                "innoTraceCost" : innoCosts,
                "scrollTraceCost" : scrollCosts,
                "cssTraceCost" : cssCosts,
                "hammerTraceCost" : hammerCosts,
                "numFailedScrolls" : fScrolls,
                "numFailedInnos" : fInnos, 
                "numFailedCSS" : fCSS, 
                "numFailedHammers" : fHammers,
                "numPassedScrolls" : pScrolls, 
                "numPassedInnos" : pInnos, 
                "numPassedCSS" : pCSS, 
                "numPassedHammers" : pHammers,
                "numGuildSaves" : numGS}

    def simulateForcePassedScroll(self, scrollRate: float, scrollCost: int) -> tuple[int, int]:
        """
        Sub-simulation for forced (css/inno) scrolling. Continuously attempts to pass the success rate
        and returns the associated cost and number of failures from the attempts.

        Args:
            scrollRate : The pass rate for the innocence scroll
            scrollCost : The trace cost for the innocence scroll

        Returns:
            A tuple of (total trace cost, number of failures) for the process
        """
        curCost, curFails = 0, 0
        while (self.random() > scrollRate): # while we fail inno scrolls
            curCost += scrollCost
            curFails += 1
        
        return (curCost + scrollCost, curFails)
    