#------------------------------------------------------------------------------
# Copyright (c) 2007, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: Enthought, Inc.
# Description: <Enthought statistical distribution package component>
#------------------------------------------------------------------------------

from distribution import Distribution

from enthought.traits.api import Float
from enthought.traits.ui.api import View, Item

class Uniform(Distribution):
    """ A uniform distribution """
    low = Float
    high = Float
    
    view = View(Item('low'), Item('high'))
    
    def _get_value(self, n):
        return self._state.uniform(self.low, self.high, n)