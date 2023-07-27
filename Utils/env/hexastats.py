"""
hexastats.py

Framework used to simulate the process of upgrading the hexa stat core. There are
two options available for simulation:

    1) Non-targeted simulation -> (Enhance until overall stat level is 20 [or materials run out])
    2) Targeted simulation -> (Enhance and reset until primary stat level is X)
        2.1) Policy Fxn Usage : (Custom policy function can be used in order to optimize costs; See addendum.)

        
The upgrade path for hexa cores can be thought of as follows (the actual stats chosen are irrelevant here):

    1) For any given core with primary stat of level X, the probability of that stat increasing is equivalent to
        table 1)'s value as seen below.
        1.1) The probability of the secondary/tertiary stat is equal under the assumption of primary enhancement fail.
    2) Upon ehancement, the cost of enhancing can be extracted from (Table 2). It increases proportionally with the
        primary skill level as well.
    3) If a reset is desired, user can spend 10m mesos in order to start over, but this is only an option if the
        hexa stat level is at least 10.

Meso cost is largely ignored because it is only applied during resets, which will be counted anwyay. One thing to
keep in mind is that the reset point will also be calculated and returned in the final results in case that is needed
for analysis.
    

------- Upgrade Table (Table 1) --------                    ------------ Cost Table (Table 2) --------------
Primary Level   | % success for enhance                         Sol Erda            |       Sol Erda Frags
----------------------------------------                    ------------------------------------------------
      1-2       |         35 %                                      5               |           10
      3-6       |         20 %                                      5               |           20
       7        |         15 %                                      5               |           30
       8        |         10 %                                      5               |           40
       9        |         5 %                                       5               |           50
      10        |         0 %                                       5               |           50


Finally, a note on the policy function to be used when enhancing. By default, the policy function will simply choose to
always enhance the current core regardless of either the primary stat level or the overall stat level. However, a 
policy function can be searched through RL means externally from this framework and provided as a collection that
supports indexing based on a hashable state much like a dictionary.
"""

from ..framework import Framework as _FW
from random import Random as _Rand
from collections import defaultdict
from typing import MutableMapping, Callable
import pickle

class HexaStatCore():
    """
    Container for hexa stat methods. Implements leveling and reset methods.
    """
    # consts
    INIT_LEVEL = 1
    MIN_RESET_LEVEL = 10
    MAX_LEVEL = 20
    MAX_STAT_LEVEL = 10

    # index markers to clean up magic nums
    PRIM_ARG_POS = 0
    SEC_ARG_POS = 1
    THIRD_ARG_POS = 2

    # probs & costs
    P_SUCC_VALS = [None, 0.35, 0.35, 0.2, 0.2, 0.2, 0.2, 0.15, 0.1, 0.05, 0]
    PB_ERDA_FRAG_COST_VALS = [None, 10, 10, 20, 20, 20, 20, 30, 40, 50, 50]
    PB_ERDA_COST_VALS = [None, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

    def __init__(self, *, rngFunc : Callable[[], float]|None = None):
        # initialize our level values
        self._nodeLevel = self.INIT_LEVEL
        self._statLevels = [self.INIT_LEVEL] * 3

        # and then our rng object is passed into here (or make one)
        self.rng : Callable[[], float]
        if rngFunc is not None:
            self.rng = rngFunc
        else:
            self.rngObj = _Rand()
            self.rng = self.rngObj.random
        
    def updateInd(self, curProb: float) -> int:
        """
        Returns an integer corresponding to the index of the value that should be updated. In
        general, the process is as follows:
            1) With a given random die roll, check first if the primary stat levels
            2) If the primary stat does not level, test whether or not either secondary stat increases at equal rates
                2.1) If a secondary stat is already maxed, then level the other at a 100% chance
        
        Args:
            curProb : A value between 0 and 1 (non-inclusive) that represents a probabilistical roll
        """
        if not 0 <= curProb < 1:
            raise RuntimeError("Probability must be a value between 0 and 1.")

        # check primary leveling
        if self.primaryStatLevel < self.MAX_STAT_LEVEL and curProb < self.P_SUCC_VALS[self.primaryStatLevel]:
            return self.PRIM_ARG_POS
        
        # then check secondary stats
        if self.secondStatLevel == 10 and self.thirdStatLevel == 10:
            return self.PRIM_ARG_POS
        elif self.secondStatLevel == 10:
            return self.THIRD_ARG_POS
        elif self.thirdStatLevel == 10:
            return self.SEC_ARG_POS
        else:
            return (self.SEC_ARG_POS if 0 <= curProb - self.P_SUCC_VALS[self.primaryStatLevel] < (1 - self.P_SUCC_VALS[self.primaryStatLevel])/2 
                                     else self.THIRD_ARG_POS)

    def levelNode(self) -> tuple[int, int]:
        """
        Levels up the hexa stat core. Returns a tuple of
            (sol erda cost, sol erda fragment cost)

        If the max level has already been reached, then an exception is thrown.
        """
        # edge case (reached max level)
        if self.level == self.MAX_LEVEL:
            raise RuntimeError("Hexa stat core level can no longer be raised.")

        # roll our rng function
        curRoll = self.rng()

        # update appropriate level and find cost before
        curCost = (self.curStoneCost, self.curFragCost)
        self._statLevels[self.updateInd(curRoll)] += 1
        self._nodeLevel += 1

        # return cost of leveling
        return curCost
    
    def resetNode(self):
        """
        Resets the hexa stat core, if possible. If the core is unable to reset (lower than level 10), then an exception
        is thrown.
        """
        if self._nodeLevel < self.MIN_RESET_LEVEL:
            raise RuntimeError("Cannot reset node with level under the reset threshold of {}".format(self.MIN_RESET_LEVEL))

        # then reset
        self._nodeLevel = self.INIT_LEVEL
        self._statLevels = [self.INIT_LEVEL]*3

    def isMaxLevel(self):
        """ Returns whether or not the node has reached the maximum level. """
    
    @property
    def primaryStatLevel(self) -> int:
        return self._statLevels[0]
    
    @property
    def secondStatLevel(self) -> int:
        return self._statLevels[1]
    
    @property
    def thirdStatLevel(self) -> int:
        return self._statLevels[2]
    
    @property
    def level(self) -> int:
        return self._nodeLevel
    
    @property
    def curFragCost(self) -> int:
        return self.PB_ERDA_FRAG_COST_VALS[self.primaryStatLevel]
    
    @property
    def curStoneCost(self) -> int:
        return self.PB_ERDA_COST_VALS[self.primaryStatLevel]


class HexaStatFramework(_FW):
    """
    A framework for performing trials for the hexa stat system.
    """

    # CLASS VAR PARAMETERS
    MAN_MSG = ("Hexa stat enhamcement framework. Provides the base framework needed to perform " +
               "enhancement of the stat matrix using sol erda and fragments. There are two simulator " +
               "options available along with the ability to provide a policy function if desired.\n" +
               "If erda fragment limit is set to 0, then it is ignored when leveling up and resetting.")
    
    ARG_TYPES : dict[str, type|tuple[type,...]] = {"Target Primary Level": int,
                                                   "Custom Policy Name": str,
                                                   "Erda Frag Limit": int}
    
    ARG_MAN = {"Target Primary Level": "Sets the desired hex stat primary level",
               "Custom Policy Name": "Declares location of the custom policy object",
               "Erda Frag Limit": "Limits the amount of erda fragments used (0 if infinite)"}
    
    # CLASS INTRINSICS
    ARG_MAPPING = {"Target Primary Level": "target",
                   "Custom Policy Name": "policyPath",
                   "Erda Frag Limit": "erdaFragLim"}
    
    
    def __init__(self, rSeed: int|None = None):
        # set up rng
        self.rng = _Rand(rSeed)
        self.random = self.rng.random

        # flag for policy checking
        self.loadedPolicy = False
        self.lastPolicyDir = ""

        # initialize our policy dict (indicates when to reset)
        # our state space will be (enhance_level, primary_level) tuples
        self.policy : MutableMapping[tuple[int, int], bool] = defaultdict(lambda : False)

    def performTrial(self, target: int, policyPath: str, erdaFragLim: int) -> dict:
        """
        Performs a single execution of the hexa stat core trial session.

        Args:
            policyPath: The location of a pickled policy to load. Should be empty if unused.
            forcePUpdate: Forces the policy to be updated in the proceeding execution.
        """
        # edge cases
        if target > HexaStatCore.MAX_STAT_LEVEL:
            raise ValueError("Target primary stat level cannot be higher than {} (was {})".format(HexaStatCore.MAX_STAT_LEVEL, target))
        elif erdaFragLim < 0:
            raise ValueError("Limiting erda fragment value cannot be lower than 0.")

        # check for arguments on erdaLim (frag cost)
        ignoreLims = True
        if erdaFragLim != 0:
            ignoreLims = False

        # Either import new policy or adjust based on target level if necessary
        if not self.loadedPolicy or self.lastPolicyDir != policyPath:
            forcePUpdate = False
            self.loadedPolicy = True
            self.lastPolicyDir = policyPath
            
            try:
                self.attemptPolicyImport(policyPath)
            except RuntimeError:
                self.updatePolicyTarget(target)

        # Then run simulation until target reached
        curCore = HexaStatCore(rngFunc = self.random)
        totCost, totResets, numEnhances = 0, 0, 0
        while curCore.level != curCore.MAX_LEVEL or curCore.primaryStatLevel < target:
            # first make sure our current frag cost doesn't exceed the max
            if not ignoreLims and totCost + curCore.curFragCost > erdaFragLim:
                break
            
            # Then proceed to enhance or reset based on our policy
            if self.policy[(curCore.level, curCore.primaryStatLevel)]: # reset
                totResets += 1
                curCore.resetNode()
            else:   # enhance
                totCost += curCore.levelNode()[1]
                numEnhances += 1

        return {
            "totalFragCost" : totCost,
            "totalEnhances" : numEnhances,
            "primaryLevel" : curCore.primaryStatLevel,
            "secondaryLevel" : curCore.secondStatLevel,
            "thirdLevel" : curCore.thirdStatLevel,
            "numResets" : totResets
        }
    
    def forceInjectPolicy(self, newPolicy: MutableMapping[tuple[int, int], bool]):
        """ Allows the policy to be manipulated by the end user without a pickled value. """
        self.policy = newPolicy
        self.loadedPolicy = True

    def attemptPolicyImport(self, policyPath: str) -> None:
        """ Tries to import a policy that represents a mapping from state space to action space """
        try:
            with open(policyPath, 'rb') as inFile:
                curObj = pickle.load(inFile)
                if not issubclass(curObj.__class__, dict):
                    raise TypeError("Improper object type passed into load.")
                self.policy = curObj
        except FileNotFoundError:
            raise RuntimeError # allows proper catching of empty directory contents

    def updatePolicyTarget(self, targetLevel: int) -> None:
        for lowerInd in range(1, targetLevel):
            self.policy[(20, lowerInd)] = True