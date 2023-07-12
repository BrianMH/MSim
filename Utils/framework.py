"""
Framework.py

Interface that defines the general way that other simulation frameworks
should be implemented. This is an example that can be imported but cannot
be executed. Other frameworks should be derived from this class.

This provides no physical support for simulation and is only a template class,
so this will fail if used as the framework for the simulator.
"""

class Framework():
    """
    An interface for the testing framework to simplify future derived frameworks. Sets out
    the general structure of the expected functions to use along with the location of the
    expected declaration of arguments and specifications for the class.
    """
    # CLASS PARAMETERS
    ARG_DIST : int = 16

    # CLASS VAR PARAMETERS
    MAN_MSG = ("Framework provides the general interface for simulation calculation along with a " +
               "templated methods to make future frameworks simpler to derive. It provides some " +
               "basic type checking to ensure that user arguments will not create errors in the " +
               "program.")
    
    ARG_TYPES : dict[str, type[int | float | str]|tuple[type[int | float | str],...]] = {"EXAMPLE1": int,
                                                                                         "EXAMPLE2": float,
                                                                                         "EXAMPLE3": (float, int)}
    
    ARG_MAN = {"EXAMPLE1" : "Sets the specification EXAMPLE1 to some integer value.",
               "EXAMPLE2" : "Sets the specification EXAMPLE2 to some float value.",
               "EXAMPLE3" : "Sets the specification EXAMPLE3 to some desired integer or float value."}
    
    # CLASS INTRINSICS
    ARG_MAPPING = {}    # used to convert human legible params above to func params

    # CLASS FUNCS
    def __init__(self):
        """
        Set up custom values for interface here along with any references that may be needed during
        simulation.
        """
        pass

    def performTrial(self, EXAMPLE1, EXAMPLE2, EXAMPLE3) -> dict:
        """
        Performs a SINGLE trial simulation that caps out at a max horizon of maxHorizon and
        takes in all values in kwargs as potential arguments for the simulation.

        Note: It is strongly recommended to include a maximum horizon for trials that can possible
              go on infinitely, but it's ultimately a choice in the end...

        Args:
            **kwArgs: Collection representing the arguments to use as according to self specification

        Returns:
            A dictionary with all possibly relevant information collected from the trial.
        """
        raise NotImplementedError("Framework cannot be executed as it is a template class.")
    
    """
    NOTE: These functions below can be overriden, but they should be generic enough to work for most instances.
    """
    def checkAndPerformTrial(self, userInputArgs: dict) -> dict:
        """
        A wrapper around the above performTrial that also ensures that the input args are at least
        of the correct format to prevent some basic user-causes misfunction.

        Args:
            userInputArgs: A collection representing the arguments to pass into the function

        Returns:
            A dictionary with all possible relevant information collected from the trial.
        """
        if not self.checkInvalidArgs(userInputArgs):
            return self.performTrial(**self.mapArgs(userInputArgs))
        else:
            raise ValueError("Input args were of an incorrect format.")
        
    def getArgs(self) -> list[str]:
        """
        Returns the arguments list as an iterable object.
        """
        return list(self.ARG_MAN.keys())
    
    def getArgTypes(self) -> dict[str, type[int | float | str]|tuple[type[int | float | str],...]]:
        """
        Returns a collection representing the framework arguments along with the allowed types.
        """
        return self.ARG_TYPES.copy()
    
    def mapArgs(self, userInputDict: dict) -> dict:
        """
        Prepares for trials by converting a dict with human legible parameters into the appropriate
        keyword dictionary necessary for performTrial to function properly. This depends on the
        class intrinsic ARG_MAPPING being properly overriden for every new class.

        (If not overwritten, the mapping is simply returned as is and is assumed to conform to
        the arguments of performTrial as is.)
        """
        if not self.ARG_MAPPING:
            return userInputDict
        else:
            return {self.ARG_MAPPING[userKey]:val for userKey,val in userInputDict.items()}
    
    def announceSelf(self) -> str:
        """
        Returns a string that represents the expected arguments for this framework along with any
        potential explanations of what is necessary for the trial to function properly.

        Returns:
            Framework specification as a string
        """
        # Grab self-explanation and usage
        retMsg = self.MAN_MSG + "\n\n" + "Arguments:\n"

        # Then include each formatted argument
        for argName, argMsg in self.ARG_MAN.items():
            retMsg += "{: >{}}\t{}\n".format(argName, self.ARG_DIST, argMsg)

        return retMsg

    def checkInvalidArgs(self, argDict: dict) -> list[str]:
        """
        Checks to see if all arguments passed by the user are valid. If an invalid argument is found,
        then returns a list of names for ill-defined arguments. If no invalid argument is present, then
        an empty list is returned.

        If argDict is ill-formed (extra/missing args), then this throws an exception.

        Args:
            argDict: A collection representing the mapping between arguments and the values to pass to them.
        """
        # edge case with more args than necessary
        if len(argDict) != len(self.ARG_TYPES):
            raise ValueError("Extra argument detected.")

        invalidArgs = list()
        for argName, argTypes in self.ARG_TYPES.items():
            if argName not in argDict:
                raise ValueError("Input argument dict did not contain expected argument for variable {}".format(argName))
            elif not isinstance(argDict[argName], argTypes):
                invalidArgs.append(argName)

        return invalidArgs
    