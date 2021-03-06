#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------
""" The interface for an interactive Python shell. """

# Enthought library imports.
from enthought.traits.api import Event

# Local imports.
from key_pressed_event import KeyPressedEvent
from i_widget import IWidget


class IPythonShell(IWidget):
    """ The interface for an interactive Python shell. """

    #### 'IPythonShell' interface #############################################

    # A command has been executed.
    command_executed = Event

    # A key has been pressed.
    key_pressed = Event(KeyPressedEvent)

    ###########################################################################
    # 'IPythonShell' interface.
    ###########################################################################

    def interpreter(self):
        """ Returns the code.InteractiveInterpreter instance. """

    def bind(self, name, value):
        """ Binds a name to a value in the interpreter's namespace. """

    def execute_command(self, command, hidden=True):
        """ Execute a command in the interpreter.

        If 'hidden' is True then nothing is shown in the shell - not even
        a blank line.
        """

    def execute_file(self, path, hidden=True):
        """ Execute a file in the interpeter.

        If 'hidden' is True then nothing is shown in the shell - not even
        a blank line.
        """


class MPythonShell(object):
    """ The mixin class that contains common code for toolkit specific
    implementations of the IPythonShell interface.

    Implements: bind(), _on_command_executed()
    """

    ###########################################################################
    # 'IPythonShell' interface.
    ###########################################################################

    def bind(self, name, value):
        """ Binds a name to a value in the interpreter's namespace. """

        self.interpreter().locals[name] = value

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _on_command_executed(self):
        """ Called when a command has been executed in the shell. """

        self.command_executed = self

#### EOF ######################################################################
