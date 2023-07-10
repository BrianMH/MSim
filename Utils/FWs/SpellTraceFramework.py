"""
SpellTraceFramework.py

Sets up a framework class type for spell trace simulation. Spell traces are unique in that
they only dependent on the equip level and type. They have a pre-defined cost depending on
equip level and do have some skills that can possible manipulate the probability of success
following a step in the trial.

For this simulator, it should also be possible to adjust the probability of the clean slates
and innocence scroll to reflect the optimal choice in a later update. (Generally, just choose
the scrolls with the lower expected value, but they should be equal in general.)

Stats will be irrelevant for now (since they can be computer after-the-fact using the evidence
of passes/fails.)
"""
from ..Framework import Framework
import SpellTraceConstants as Consts

class SpellTraceFramework(Framework):
    """
    A framework for calculating trials using spell traces.
    """

    # CLASS VAR PARAMETERS
    MAN_MSG = ("Framework provides the general interface for simulation calculation along with a" +
               "templated methods to make future frameworks simpler to derive. It provides some" +
               "basic type checking to ensure that user arguments will not create errors in the" +
               "program.")
    
    ARG_TYPES : dict[str, type|tuple[type,...]] = {"EXAMPLE1": int,
                                                "EXAMPLE2": float,
                                                "EXAMPLE3": (int, float)}
    
    ARG_MAN = {"EXAMPLE1" : "Sets the specification EXAMPLE1 to some integer value.",
               "EXAMPLE2" : "Sets the specification EXAMPLE2 to some float value.",
               "EXAMPLE3" : "Sets the specification EXAMPLE3 to some desired integer or float value."}

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