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
Contains the implementation of the DaemonApplication class.
"""

# Platform Imports
import os
import sys
import signal
import errno
import time
import platform
import atexit

# SEED Imports
from .application import Application
from .businesslogic import BusinessLogic

class DaemonApplication(Application):

    """
    Implements a Unix daemon application.

    This implementation is based on the python-daemon implementation at:
        https://github.com/serverdensity/python-daemon
    which is derived from:
        http://www.jejik.com/articles/2007/02/
        a_simple_unix_linux_daemon_in_python/www.boxedice.com

    Authors:
        Attila Kovacs
    """

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
                 sentry_dsn: str = '',
                 pid_file: str,
                 stdin: str = os.devnull,
                 stdout: str = os.devnull,
                 stderr: str = os.devnull,
                 working_directory: str = './',
                 umask: int = 0o22,
                 debug_mode: bool = False) -> None:

        """
        Creates a new DaemonApplication instance.

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
            pid_file:               Path to the pid file the daemon will use.
            stdin:                  The input stream to be used by the daemon.
            stdout:                 The output stream to be used by the daemon.
            stderr:                 The error stream to be used by the daemon.
            working_directory:      Path to the working directory of the daemon
                                    process.
            umask:                  The umask to use for files created by the
                                    daemon process.
            debug_mode:             Whether or not the application should be
                                    started in debug mode.

        Authors:
            Attila Kovacs
        """

        super().__init__(business_logic=business_logic,
                         service_directory=service_directory,
                         service_package=service_package,
                         config_directory=config_directory,
                         data_directory=data_directory,
                         debug_mode=debug_mode,
                         service_dir_required=service_dir_required,
                         config_dir_required=config_dir_required,
                         data_dir_required=data_dir_required,
                         sentry_dsn=sentry_dsn)

        self._pid_file = os.path.abspath(os.path.expanduser(pid_file))
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr
        self._working_directory = os.path.abspath(
            os.path.expanduser(working_directory))
        self._umask = umask
        self._alive = False

    def start(self, *args: list, **kwargs: list) -> None:

        """
        Starts the daemon.

        Args:
            args:       List of normal arguments.
            kwargs:     List of named arguments.

        Authors:
            Attila Kovacs
        """

        # Check the pid file to see if the daemon is already running.
        pid = self.get_pid()

        if pid:
            message = 'PID file {} already exists. The daemon is already ' \
                      'running?'.format(self._pid_file)
            sys.stderr.write(message)
            sys.exit(1)

        # Start the daemon
        self._daemonize()

        pid = self.get_pid()
        message = 'Daemon created with PID {}'.format(pid)
        sys.stdout.write(message)

        self.execute(*args, **kwargs)

    def stop(self) -> None:

        """
        Stops the daemon.

        Authors:
            Attila Kovacs
        """

        print('Trying to stop the daemon...')

        pid = self.get_pid()

        if not pid:
            message = 'PID file {} does not exist, The daemon is not ' \
                      'running?'.format(self._pid_file)
            sys.stderr.write(message)
            sys.exit(1)

            # Just to be sure. A ValueError might occur if the PID file is
            # empty, but it actually exists
            print('Deleting pid...')
            self.delete_pid()

            # not an error during a restart
            return

        # Try killing the daemon process
        try:
            i = 0
            while 1:
                print('Sending SIGTERM...')
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
                i = i + 1
                if i % 10 == 0:
                    print('Sending SIGHUP...')
                    os.kill(pid, signal.SIGHUP)
        except OSError as error:
            print(error)
            if error.errno == errno.ESRCH:
                print('Deleting PID...')
                self.delete_pid()
            else:
                print(str(error))
                sys.exit(1)

    def restart(self, *args: list, **kwargs: list) -> None:

        """
        Restarts the daemon.

        Args:
            args:       List of normal arguments.
            kwargs:     List of named arguments.

        Authors:
            Attila Kovacs
        """

        self.stop()
        self.start(*args, **kwargs)

    def get_pid(self) -> int:

        """
        Returns the pid of a running daemon process.
        """

        try:
            with open(self._pid_file, 'r') as pid_file:
                pid = int(pid_file.read().strip())
        except IOError:
            pid = None
        except SystemExit:
            pid = None

        return pid

    def get_status(self) -> str:

        """
        Returns the current status of the daemon.

        Returns:
            A status report string reflecting the current status of the daemon.

        Authors:
            Attila Kovacs
        """

        pid = self.get_pid()

        if pid is not None:
            return 'Daemon is running with PID {}'.format(pid)

        return 'Daemon is not running.'

    def is_running(self) -> bool:

        """
        Returns whether or not the daemon is running.

        Returns:
            'True' if the daemon process is running, 'False' otherwise.

        Authors:
            Attila Kovacs
        """

        pid = self.get_pid()

        if pid is None:
            # Process is stopped
            return False

        if os.path.exists('/proc/{}'.format(pid)):
            # Process is running
            return True

        # Process is killed
        return False

    def delete_pid(self) -> None:

        """
        Deletes the PID file.

        Authors:
            Attila Kovacs
        """

        try:
            # The process may fork itself again
            pid = int(open(self._pid_file, 'r').read().strip())
            if pid == os.getpid():
                os.remove(self._pid_file)
        except OSError as error:
            if error.errno == errno.ENOENT:
                pass
            else:
                raise

    def handle_sigterm(self, signum: int, frame: object) -> None:

        """
        Handler function that is called when SIGTERM is received.

        Args:
            signum:     The actual signam number that was received.
            frame:      The current stack frame.

        Authors:
            Attila Kovacs
        """

        del signum
        self._business_logic.handle_sigterm(frame)
        self._alive = False
        sys.exit(0)

    def handle_sigint(self, signum: int, frame: object) -> None:

        """
        Handler function that is called when SIGTERM is received.

        Args:
            signum:     The actual signam number that was received.
            frame:      The current stack frame.

        Authors:
            Attila Kovacs
        """

        del signum
        self._business_logic.handle_sigint(frame)
        self._alive = False
        sys.exit(0)

    def handle_sigalrm(self, signum: int, frame: object) -> None:

        """
        Handler function that is called when SIGALRM is received.

        Args:
            signum:     The actual signam number that was received.
            frame:      The current stack frame.

        Authors:
            Attila Kovacs
        """

        del signum
        self._business_logic.handle_sigalrm(frame)

    def handle_sigusr1(self, signum: int, frame: object) -> None:

        """
        Handler function that is called when SIGUSR1 is received.

        Args:
            signum:     The actual signam number that was received.
            frame:      The current stack frame.

        Authors:
            Attila Kovacs
        """

        del signum
        self._business_logic.handle_sigusr1(frame)

    def handle_sigusr2(self, signum: int, frame: object) -> None:

        """
        Handler function that is called when SIGUSR2 is received.

        Args:
            signum:     The actual signam number that was received.
            frame:      The current stack frame.

        Authors:
            Attila Kovacs
        """

        del signum
        self._business_logic.handle_sigusr2(frame)

    def _daemonize(self) -> None:

        """
        Daemonizes the process using the Unix double-fork method.

        For details, see Stevens' "Advanced Programming in the UNIX
        Environment" (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16

        Authors:
            Attila Kovacs
        """

        # Daemonization only works on Unix systems, so don't attempt it on
        # Windows
        if platform.system().lower() == 'windows':
            return

        # Execute the first fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)
        except OSError as error:
            print(error)
            sys.stderr.write(
                'ERROR >> First fork failed. Errno: {} Error: {}'.format(
                    error.errno, error.strerror))
            sys.exit(1)

        # Decouple from the parent environment
        os.chdir(self._working_directory)
        os.setsid()
        os.umask(self._umask)

        # Execute the second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit the second fork
                sys.exit(0)
        except OSError as error:
            print(error)
            sys.stderr.write(
                'ERROR >> Second fork failed. Errno: {} Error: {}'.format(
                    error.errno, error.strerror))
            sys.exit(1)

        # Redirect standard file descriptors.
        sys.stdout.flush()
        sys.stderr.flush()

        std_in = open(self._stdin, 'r')
        std_out = open(self._stdout, 'a+')
        std_err = std_out

        if self._stderr:
            std_err = open(self._stderr, 'a+', 1)

        # Duplicate file descriptors
        os.dup2(std_in.fileno(), sys.stdin.fileno())
        os.dup2(std_out.fileno(), sys.stdout.fileno())
        os.dup2(std_err.fileno(), sys.stderr.fileno())

        # Register signals
        signal.signal(signal.SIGTERM, self.handle_sigterm)
        signal.signal(signal.SIGINT, self.handle_sigint)
        signal.signal(signal.SIGALRM, self.handle_sigalrm)
        signal.signal(signal.SIGUSR1, self.handle_sigusr1)
        signal.signal(signal.SIGUSR2, self.handle_sigusr2)

        # Make sure that the PID is removed at exit
        atexit.register(self.delete_pid)

        # Retrieve the PID
        pid = str(os.getpid())

        # Write the PID file
        open(self._pid_file, 'w+').write('%s\n' % pid)
