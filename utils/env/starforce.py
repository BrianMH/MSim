"""
starforce.py

Framework used to simulate the process of upgrading the hexa stat core. As of now, the only target available (finish state)
is reaching the desire star force value, but it may be interesting enough to set a threshold value instead and condition the
best final result on the amount available.
        
The implementations of star force across different servers seems to vary wildly, but for now we assume the following are true:
    1) The initial starting state of any star force trial can vary, but is noted as it's current "star value"
    2) There exists some cap level beyond which star force is no longer possible (25/30)
    3) Each trial (or attempt) can have the following results:
        3.1) \\alpha chance of succeeding (star value + 1)
        3.2) \\beta chance of failing (star value + 0)
        3.3) \\gamma chance of destorying item (star value = (0 if star value < 12), 12 otherwise)

        Of course, no matter which of these occur, we also take not of another non-critical state being changed. No matter what happens
        there will be an increase of the number of mesos used in the trial.

Events seem to have special effects on either the success / failure / or destruction of an equip (unknown how star catching plays a role still),
but they need to keep track of the state to identify their additive adjustments (multiplicative will just be converted into an additive adjustment based
on current state), so they will be designed with the Item Star Force class state in mind.

IMPL DETAILS:
    1) State (S_c) is tuple of (item_level, item_starforce_value)
    2) Performing a state transition on markov P(X|S=S_c) incurs cost (C) and induces new states under X={"success", "fail", "boom"}
    3) Events are multipliers on either the cost (C) or the probabilities. When applied on probabilities, the removed "quantity" under a reduced boom is re-organized
        such that it becomes a failure [ P(X=boom|S=S_c^E={E_1, ...}) = P(X=boom|S=S_c^E={}) - epsilon) => P(X=fail|S=S_c^E={E_1,...}) = P(X=fail|S=S_C^E={}) + epsilon ]
"""
from ..framework import Framework as _FW
from random import Random as _Rand
from typing import Callable
from enum import Enum


'''
    EVENT INTRINSICS   -- STATE,  P_S ,  P_F ,  P_B , C(A) => E(P_S), E(P_F), E(P_B), E(C(A))
'''
type EventReturn = Callable[[tuple[int, int], float, float, float, int], tuple[float, float, float, int]]


class ItemStarForceMarkovValues():
    """
    Base class that contains the markov values for individual servers. Based on the input, returns a tuple of the lists containing the respective
    markov transition probabilities along with a functor that identifies the cost of any given attempt throughout the process based on the current
    star level.
    """
    class RegionEnum(Enum):
        """
        Region enum used to identify return value
        """
        KMS = "kms"
        GMS = "gms"
        MSEA = "msea"

    @staticmethod
    def _KMSMatrix() -> tuple[list[float], list[float], list[float], Callable[[int], int]]:
        P_SUCC_VALS: list[float] = [.95, .90, .85, .85, .80, .75, .70, .65, .60, .55, .50, .45, .40, .35, .30, .30, .30, .15, .15, .15, .30, .15, .15, .10, .10, .10, .07, .05, .03, .01]
        P_FAIL_VALS: list[float] = [.05, .10, .15, .15, .20, .25, .30, .35, .40, .45, .50, .55, .60, .65, .70, .679, .679, .782, .782, .765, .595, .7225, .68, .72, .72, .72, .744, .76, .776, .792]
        P_BOOM_VALS: list[float] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, .021, .021, .068, .068, .085, .105, .1275, .17, .18, .18, .18, .186, .19, .194, .198]
        costFunctorDiv: list[int] = [36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 571, 314, 214, 157, 107, 200, 200, 150, 70, 45, 200, 125, 200, 200, 200, 200, 200, 200, 200, 200]
        costFunctor = lambda curLevel, curStarValue : round(1000 + (pow(curLevel, 3) * pow(curStarValue + 1), 2.7) / costFunctorDiv[curStarValue])

        return (P_SUCC_VALS, P_FAIL_VALS, P_BOOM_VALS, costFunctor)
    
    @staticmethod
    def returnRegionMatrix(region: str) -> tuple[list[float], list[float], list[float], Callable[[int], int]]:
        match region:
            case ItemStarForceMarkovValues.RegionEnum.KMS.value:
                return ItemStarForceMarkovValues._KMSMatrix()
            case _:
                raise NotImplementedError
            

    '''
        EVENT METHODS
    '''
    @staticmethod
    def _KMSCostEvent() -> EventReturn:
        return lambda sv, ps, pf, pb, ca : (ps, pf, pb, 0.7*ca)
    
    @staticmethod
    def _KMSBoomEvent() -> EventReturn:
        return lambda sv, ps, pf, pb, ca : (ps, pf + 0.3*pb, 0.7*pb, ca) if 15 <= sv[1] <= 21 else (ps, pf, pb, ca)
    
    @staticmethod
    def _MVPCostEvent() -> EventReturn:
        return lambda sv, ps, pf, pb, ca: (ps, pf, pb, 0.95*ca) if sv[1] <= 17 else (ps, pf, pb, ca)
    
    @staticmethod
    def _StarCatchEvent() -> EventReturn:
        """
            Per Namu, star catch is eff. 1.05 multiplier on P_SUCC, but the remaining value is distributed in accordance with the ratio between P_FAIL : P_BOOM. In other words, under the event...
                     (P_SUCC, P_FAIL, P_BOOM) -> ( 1.05 * P_SUCC, (P_FAIL)/(P_FAIL+P_BOOM)*(1 - 1.05 * P_SUCC), (P_BOOM)/(P_FAIL+P_BOOM)*(1 - 1.05 * P_SUCC))
        """
        return lambda sv, ps, pf, pb, ca: (1.05*ps, (pf/(pf+pb))*(1-1.05*ps), (pb/(pf+pb))*(1-1.05*ps), ca)


class ItemStarForce():
    """
        Container for Item Star Force methods. Implements star force "tapping" based on arbitrary
        starting point. When tapping, returns the meso cost value of the tap. State can be checked
        at any point through the class.
    """
    def __init__(self, itemLevel: int, initLevel: int, * , region: str = "kms", events: list[EventReturn] = [], rngFunc: Callable[[], float]|None = None):
        # Keeps track of our passed init args so that reset can function properly
        self._initVals = (itemLevel, initLevel, region)

        # Initialize our base metadata
        self._starValue = initLevel
        self._itemLevel = itemLevel
        self._region = region
        self.rng : Callable[[], float]
        if rngFunc is not None:
            self.rng = rngFunc
        else:
            self.rngObj = _Rand()
            self.rng = self.rngObj.random

        # We allow revival of items, but in order to revive them, we must take into account when the item is boomed
        self.boomed = False

        # Associate our transition probabilities based on the region
        self._P_SUCC, self._P_FAIL, self._P_BOOM, self._costFunctor = ItemStarForceMarkovValues.returnRegionMatrix(region)
        self._COST_MULT = [1] * len(self._P_SUCC)
        self._maxStarValue = len(self._P_SUCC)

        # And initialize any "events" if they will be necessary by associating them with the current state
        self.eventArray = events

        # We can adjust the probability values given the events now...
        self.adjustEventProbsAndCost()

    def attemptStarForce(self) -> int:
        """
            Attempts to "tap" an item's star force level according to the provided probabilities and rng function.
            May either succeed, fail, or "boom" an item.
            
            If an item is not currently star forceable, throws an error.
        """
        if not self.canStarForce:
            raise RuntimeError("Item cannot currently be taped. Make sure it is not boomed or maxed already.")
        
        # Then attempt to tap and return the cost of the tap.
        curRoll = self.rng

    def reviveItem(self) -> None:
        """
            Unbooms an item (Used only to take up a step in the markov chain)
        """
        self.boomed = False

    def adjustEventProbsAndCost(self) -> None:
        """
            Uses the current set of events to adjust the set of probabilities the class is currently initialized with. Once finished, deletes
            the set of events so that this cannot have a compounded effect.

            This function also calculates the realized cost so that it isn't calculated on the fly every time.
        """
        

    @property
    def canStarForce(self) -> bool:
        return not self.boomed and self.starValue < self.MAX_SF_STAR

    @property
    def isBoomed(self) -> bool:
        return self.boomed

    @property
    def state(self) -> tuple[int, int]:
        """
            Our object's state can be defined as a tuple as follows:
                    (item_level, item_starvalue)
        """
        return (self._itemLevel, self._starValue)

    @property
    def starValue(self) -> int:
        return self._starValue
    
    @property
    def itemLevel(self) -> int:
        return self._itemLevel
    

class StarForceFramework(_FW):
    """
        A framework for performing trials for the SF system.
    """

    # CLASS VAR PARAMETERS
    MAN_MSG = ("Star Force Enhancement framework. Provides a basic implementation of star forcing " +
               "with arbitrary starting star force value and item level. For now only supports goal " +
               "specific star forcing (reaching X stars w/ no meso cap). Does not work with superior items.\n" +
               "Keeps track of total meso cost and boom occurrences.")
    
    ARG_TYPES : dict[str, type|tuple[type,...]] = {"Target SF Level": int,
                                                   "Item Level": int,
                                                   "Start SF Level": int,
                                                   "KMS Cost Event": str,
                                                   "KMS Boom Event": str}
    
    ARG_MAN = {"Target SF Level": "Sets the desired Star Force level [0-30]",
               "Item Level": "The level of the item to star force [0-250]",
               "Start SF Level": "The SF point to start from (0 by default) [0-30]",
               "KMS Cost Event": "Applies a 30%% discount to the cost of star forcing (KMS Sunday Event) (y/n)",
               "KMS Boom Event": "Applies a 30%% reduced chance to boom while star forcing, but only up to 21* (KMS Sunday Event) (y/n)"}    
    # CLASS INTRINSICS
    ARG_MAPPING = {"Target SF Level": "targetSfLevel",
                   "Item Level": "itemLevel",
                   "Start SF Level": "startSfLevel",
                   "KMS Cost Event": "eventKmsCost",
                   "KMS Boom Event": "eventKmsBoom"}
    
    
    def __init__(self, rSeed: int|None = None):
        # set up rng
        self.rng = _Rand(rSeed)
        self.random = self.rng.random

    def performTrial(self, targetSfLevel: int, itemLevel: int, startSfLevel: int, eventKmsCost: str, eventKmsBoom: str) -> dict:
        """
            Performs a single markov trial simulation. In this case, creates an item with a given starting SF Level, and then
            star forces it until it reaches the target SF level and returns a dict containing the total meso cost and number of booms.
        """
