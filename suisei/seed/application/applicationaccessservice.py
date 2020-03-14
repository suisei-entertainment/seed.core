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
Contains the implementation of the application access service.
"""

class ApplicationAccessService:

    """
    Simple, globally accessible service to provide access to the application
    object.

    Authors:
        Attila Kovacs
    """

    def set_application(self, application: 'Application') -> None:

        """
        Sets the application object.

        Args:
            application:        The application object to provide access to.

        Authors:
            Attila Kovacs
        """

        #pylint: disable=no-self-use

        return

    def get_application(self) -> 'Application':

        """
        Returns the application object.

        Authors:
            Attila Kovacs
        """

        #pylint: disable=no-self-use

        return None


@Service(ApplicationAccessService)
class DefaultApplicationAccessService(ApplicationAccessService):

    """
    Simple, globally accessible service implementation to provide access to
    the application object.

    Authors:
        Attila Kovacs
    """

    def __init__(self) -> None:

        """
        Creates a new DefaultApplicationAccessService object.
        """

        # The application object to provice access to.
        self._application = None

    def set_application(self, application: 'Application') -> None:

        """
        Sets the application object.

        Args:
            application:        The application object to provide access to.

        Authors:
            Attila Kovacs
        """

        self._application = application

    def get_application(self) -> 'Application':

        """
        Returns the application object.

        Authors:
            Attila Kovacs
        """

        return self._application