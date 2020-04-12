## ============================================================================
##                   **** SEED Virtual Reality Platform ****
##                Copyright (C) 2019-2020, Suisei Entertainment
## ============================================================================
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
## ============================================================================

"""
Contains the implementation of the BusinessLogic class.
"""

# SEED Imports
from suisei.seed.utils import ServiceLocator
from .application import ApplicationReturnCodes

class BusinessLogic:

    """
    Common base class for the representation of the business logic part of an
    application.

    Authors:
        Attila Kovacs
    """

    def main_loop(self) -> ApplicationReturnCodes:

        """
        Contains the main loop (or the main business execution logic of
        the application.

        Returns:
            The overall return code of the application.
            ApplicationReturnCodes.SUCCESS for successful execution, or an
            integer value to indicate issues.

        Authors:
            Attila Kovacs
        """

        #pylint: disable=no-self-use

        return ApplicationReturnCodes.SUCCESS

    def before_main_loop(self) -> None:

        """
        Function that is called before the application enters its main loop.

        Authors:
            Attila Kovacs
        """

        #pylint: disable=no-self-use

        return

    def after_main_loop(self) -> None:

        """
        Function that is called after the application exited the main loop in
        a normal way.

        Authors:
            Attila Kovacs
        """

        #pylint: disable=no-self-use

        return

    def initialize_services(self) -> None:

        """
        Initializes the services used by the application. It is called by the
        application upon initialization.

        Authors:
            Attila Kovacs
        """

        return

    def on_uncaught_exception(self, exception: Exception) -> None:

        """
        Handler function called when the application encounters an uncaught
        exception.

        Args:
            exception:      The exception that was not handled properly.

        Authors:
            Attila Kovacs
        """

        #pylint: disable=no-self-use

        del exception

    def on_sigterm(self, frame: object) -> None:

        """
        Handler function called when the application receives a SIGTERM signal.

        Args:
            frame:      The current stack frame.

        Authors:
            Attila Kovacs
        """

        #pylint: disable=no-self-use

        del frame

    def on_sigint(self, frame: object) -> None:

        """
        Handler function called when the application receives a SIGINT signal.

        Args:
            frame:      The current stack frame.

        Authors:
            Attila Kovacs
        """

        #pylint: disable=no-self-use

        del frame

    def on_sigalrm(self, frame: object) -> None:

        """
        Handler function called when the application receives a SIGALRM signal.

        Args:
            frame:      The current stack frame.

        Authors:
            Attila Kovacs
        """

        #pylint: disable=no-self-use

        del frame

    def on_sigusr1(self, frame: object) -> None:

        """
        Handler function called when the application receives a SIGUSR1 signal.

        Args:
            frame:      The current stack frame.

        Authors:
            Attila Kovacs
        """

        #pylint: disable=no-self-use

        del frame

    def on_sigusr2(self, frame: object) -> None:

        """
        Handler function called when the application receives a SIGUSR2 signal.

        Args:
            frame:      The current stack frame.

        Authors:
            Attila Kovacs
        """

        #pylint: disable=no-self-use

        del frame
