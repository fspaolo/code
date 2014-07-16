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
""" The interface for a page in a wizard. """


# Enthought library imports.
from enthought.traits.api import Bool, Interface, Str, Tuple, Unicode


class IWizardPage(Interface):
    """ The interface for a page in a wizard. """

    #### 'IWizardPage' interface ##############################################

    # The unique Id of the page within the wizard.
    id = Str
    
    # The Id of the next page.
    next_id = Str

    # Set if this is the last page of the wizard.  It can be ignored for
    # simple linear wizards.
    last_page = Bool(False)
    
    # Is the page complete (i.e. should the 'Next' button be enabled)?
    complete = Bool(False)

    # The page heading.
    heading = Unicode
    
    # The page sub-heading.
    subheading = Unicode

    # The size of the page.
    size = Tuple
    
    ###########################################################################
    # 'IWizardPage' interface.
    ###########################################################################

    def create_page(self, parent):
        """ Creates the wizard page. """

    def dispose_page(self):
        """ Disposes the wizard page.

        Subclasses are expected to override this method if they need to
        dispose of the contents of a page.
        """

    ###########################################################################
    # Protected 'IWizardPage' interface.
    ###########################################################################

    def _create_page_content(self, parent):
        """ Creates the actual page content. """


class MWizardPage(object):
    """ The mixin class that contains common code for toolkit specific
    implementations of the IWizardPage interface.

    Implements: dispose_page()
    """

    ###########################################################################
    # 'IWizardPage' interface.
    ###########################################################################

    def dispose_page(self):
        """ Disposes the wizard page.

        Subclasses are expected to override this method if they need to
        dispose of the contents of a page.
        """

        pass

#### EOF ######################################################################
