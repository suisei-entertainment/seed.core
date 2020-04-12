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
Contains the implementation of the base Application class.
"""

# Platform Imports
import os
import logging
from enum import IntEnum

# Dependency Imports
import sentry_sdk

# SEED Imports
from suisei.seed.utils import ServiceLocator

from .businesslogic import BusinessLogic
from .applicationaccessservice import ApplicationAccessService

class ApplicationReturnCodes(IntEnum):

    """
    Contains the list of application exit codes supported by SEED.

    Authors:
        Attila Kovacs
    """

    # Application execution finished successfully.
    SUCCESS = 200

    # Uncaught exception was triggered.
    UNCAUGHT_EXCEPTION = 666

class Application:

    """
    Base class that provides functionality that is common between all
    application types.

    Authors:
        Attila Kovacs
    """

    @property
    def BusinessLogic(self) -> 'BusinessLogic':

        """
        Provides access to the business logic of the application.

        Authors:
            Attila Kovacs
        """

        return self._business_logic

    @property
    def IsDebugMode(self) -> bool:

        """
        Returns whether or not the application was started in debug mode.

        Authors:
            Attila Kovacs
        """

        return self._debug_mode

    @property
    def IsSentryIOUsed(self) -> bool:

        """
        Whether or not Sentry.IO is used.

        Authors:
            Attila Kovacs
        """

        return self._use_sentry_io

    @property
    def ServiceDirectory(self) -> str:

        """
        Path to the directory containing the initial services of the
        application.

        Authors:
            Attila Kovacs
        """

        return self._service_directory

    @property
    def ServicePackage(self) -> str:

        """
        Package name to use when loading the initial services.

        Authors:
            Attila Kovacs
        """

        return self._service_package

    @property
    def ConfigDirectory(self) -> str:

        """
        Path to the directory containing the initial application configuration.

        Authors:
            Attila Kovacs
        """

        return self._config_directory

    @property
    def DataDirectory(self) -> str:

        """
        Path to the directory containing the data the application is working
        with.

        Authors:
            Attila Kovacs
        """

        return self._data_directory

    def __init__(self,
                 business_logic: 'BusinessLogic',
                 service_directory: str = '',
                 service_package: str = '',
                 config_directory: str = '',
                 data_directory: str = '',
                 debug_mode: bool = False,
                 service_dir_required: bool = False,
                 config_dir_required: bool = False,
                 data_dir_required: bool = False,
                 sentry_dsn: str=None) -> None:

        """
        Creates a new Application instance.

        Args:
            service_directory:      The directory which contains the initial
                                    services.
            service_package:        The name of the package containing the
                                    services.
            config_directory:       The directory which contains the initial
                                    application configuration.
            data_directory:         The directory which contains data the
                                    application is working with.
            business_logic:         The business logic representation.
            debug_mode:             Whether or not the application should be
                                    started in debug mode.
            service_dir_required:   Whether or not providing a valid service
                                    directory and service package is requried.
            config_dir_required:    Whether or not providing a valid config
                                    directory is required.
            data_dir_required:      Whether or not providing a valid data
                                    directory is required.
            sentry_dsn:             The endpoint in Sentry.IO that this
                                    application is using.

        Raises:
            InvalidInputError:      Raised when no valid business logic
                                    implementation is provided.
            InvalidInputError:      Raised when a directory path or service
                                    package is not provided even though it
                                    was marked as required.
            RuntimeError:           Raised when the application access service
                                    cannot be retrieved.

        Authors:
            Attila Kovacs
        """

        if business_logic is None:
            raise InvalidInputError('No valid business logic implementation '
                                    'was provided.')

        self._business_logic = business_logic
        """
        The actual business logic implementation of the application.
        """

        self._debug_mode = debug_mode
        """
        Whether or not the application should be started in debug mode.
        """

        self._logger = logging.getLogger('suisei.seed.application')
        """
        The logger object to be used by this class.
        """

        # Whether or not Sentry.IO should be used.
        self._use_sentry_io = False

        # Initialize Sentry.IO
        if sentry_dsn:
            self._use_sentry_io = True
            sentry_sdk.init(dsn=sentry_dsn)

        # Validate the provided directories.
        try:
            self._validate_service_directory(service_directory,
                                             service_dir_required)
            self._validate_service_package(service_package,
                                           service_dir_required)
            self._validate_config_directory(config_directory,
                                            config_dir_required)
            self._validate_data_directory(data_directory,
                                          data_dir_required)
        except InvalidInputError:
            raise

        self._service_directory = service_directory
        """
        The service directory containing the initial services of the
        application.
        """

        self._service_package = service_package
        """
        The service package to be used when loading the services from the
        service directory.
        """

        self._config_directory = config_directory
        """
        The directory containing the initial services of the application.
        """

        self._data_directory = data_directory
        """
        The directory containing the additional data of the application.
        """

        # Configure initial services
        self._business_logic.initialize_services()

        # Make the application instance available through the application
        # access service
        access_service = ServiceLocator.instance().get_provider(
            ApplicationAccessService)

        if not access_service:
            raise RuntimeError(
                'Failed to retrieve the application access service.')

        access_service.set_application(self)

    def excecute(self) -> int:

        """
        Contains the main execution logic of the application.

        Authors:
            Attila Kovacs
        """

        # Pylint doesn't recognize the instance() method of Singleton.
        #pylint: disable=no-member

        # Load the configuration
        configuration = ServiceLocator.instance().get_provider(
            ConfigurationService)

        if configuration is not None:
            configuration.load()
        else:
            self._logger.error('Failed to retrieve configuration service.')

        # Catching every uncaught exception here is intentional so that
        # the applications can react to it and to also set the proper
        # exit code of the application.
        #pylint: disable=broad-except

        try:
            self._business_logic.before_main_loop()
            result = self._business_logic.main_loop()
            self._business_logic.after_main_loop()
        except Exception as error:
            self._business_logic.on_uncaught_exception(error)
            sentry_sdk.capture_exception(error)
            result = ApplicationReturnCodes.UNCAUGHT_EXCEPTION

        return result

    @staticmethod
    def _validate_service_diretory(service_directory: str,
                                   service_dir_required: bool) -> None:

        """
        Validates the service directory of the application.

        Args:
            service_directory:      The directory which contains the initial
                                    services.
            service_dir_required:   Whether or not providing a valid service
                                    directory and service package is requried.

        Raises:
            InvalidInputError:      Raised if there is no service directory
                                    provided, or the provided directory doesn't
                                    exist.

        Authors:
            Attila Kovacs
        """

        if not service_dir_required:
            return

        if not service_directory or service_directory == '':
            raise InvalidInputError('No valid service directory was provided.')

        real_path = os.path.abspath(os.path.expanduser(service_directory))

        if not os.path.isdir(real_path):
            raise InvalidInputError(
                'Service directory {} does not exist.'.format(real_path))

    @staticmethod
    def _validate_service_package(service_package: str,
                                  service_dir_required: bool) -> None:

        """
        Validates the service package of the application.

        Args:
            service_package:        The name of the package containing the
                                    services.
            service_dir_required:   Whether or not providing a valid service
                                    directory and service package is requried.

        Raised:
            Raised if there is no service package provided or the provided
            service package cannot be imported.

        Authors:
            Attila Kovacs
        """

        if not service_dir_required:
            return

        if not service_package:
            raise InvalidInputError('No service package was provided.')

        try:
            __import__(service_package)
        except ImportError:
            raise InvalidInputError(
                'The provided service package ({}) cannot be '
                'imported.'.format(service_package))

    @staticmethod
    def _validate_config_diretory(config_directory: str,
                                  config_dir_required: bool) -> None:

        """
        Validates the configuration directory of the application.

        Args:
            config_directory:       The directory which contains the initial
                                    application configuration.
            config_dir_required:    Whether or not providing a valid config
                                    directory is required.

        Raises:
            InvalidInputError:      Raised if there is no config directory
                                    provided, or the provided directory doesn't
                                    exist.

        Authors:
            Attila Kovacs
        """

        if not config_dir_required:
            return

        if not config_directory or config_directory == '':
            raise InvalidInputError('No valid service directory was provided.')

        real_path = os.path.abspath(os.path.expanduser(config_directory))

        if not os.path.isdir(real_path):
            raise InvalidInputError(
                'Configuration directory {} does not exist.'.format(real_path))

        return

    @staticmethod
    def _validate_data_directory(data_directory: str,
                                 data_dir_required: bool) -> None:

        """
        Validates the data directory of the application.

        Args:
            data_directory:         The directory which contains the additional
                                    data used by the application.
            data_dir_required:      Whether or not providing a valid data
                                    directory is required.

        Raises:
            InvalidInputError:      Raised if there is no data directory
                                    provided, or the provided directory doesn't
                                    exist.

        Authors:
            Attila Kovacs
        """

        if not data_dir_required:
            return

        if not data_directory or data_directory == '':
            raise InvalidInputError('No valid data directory was provided.')

        real_path = os.path.abspath(os.path.expanduser(data_directory))

        if not os.path.isdir(real_path):
            raise InvalidInputError(
                'Data directory {} does not exist.'.format(real_path))
