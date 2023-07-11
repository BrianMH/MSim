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

class SpellTraceFramework(_FW):
    """
    A framework for calculating trials using spell traces.
    """

    # CLASS VAR PARAMETERS
    MAN_MSG = ("Spell Trace Enhancement framework. Provides the base framework needed to perform" +
               "enhancement of items using the available spell trace system. Constants for the" +
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

    # CLASS FUNCS
    def __init__(self):
        """
        Set up custom values for interface here along with any references that may be needed during
        simulation.
        """
        pass

    def performTrial(self, **kwargs) -> dict:
        """
        Performs a SINGLE trial simulation that caps out at a max horizon of maxHorizon and
        takes in all values in kwargs as potential arguments for the simulation.

        Note: It is strongly recommended to include a maximum horizon for trials that can possible
              go on infinitely, but it's ultimately a choice in the end...

        Args:
            **kwArgs: Collection representing the arguments to use as according to self specification

        Returns:
            A dictionary with all possibly relevant information collected.
        """
        raise NotImplementedError("Framework cannot be executed as it is a template class.")
