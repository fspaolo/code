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
""" The preference dialog. """


# Major package imports.
import wx

# Enthought library imports.
from enthought.pyface.api import HeadingText, LayeredPanel, SplitDialog
from enthought.pyface.util.font_helper import new_font_like
from enthought.pyface.viewer.api import TreeViewer, DefaultTreeContentProvider
from enthought.traits.api import Any, Dict, Float, Instance, Str

# Local imports.
from preference_node import PreferenceNode


class PreferenceDialog(SplitDialog):
    """ The preference dialog. """

    #### 'Dialog' interface ###################################################

    # The dialog title.
    title = Str('Preferences')

    #### 'SplitDialog' interface ##############################################

    # The ratio of the size of the left/top pane to the right/bottom pane.
    ratio = Float(0.25)

    #### 'PreferenceDialog' interface #########################################

    # The root of the preference hierarchy.
    root = Instance(PreferenceNode)

    #### Private interface ####################################################

    # The preference pages in the dialog (they are created lazily).
    _pages = Dict

    # The current visible preference page.
    _current_page = Any

    ###########################################################################
    # Protected 'Dialog' interface.
    ###########################################################################

    def _create_buttons(self, parent):
        """ Creates the buttons. """

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 'Done' button.
        done = wx.Button(parent, wx.ID_OK, "Done")
        done.SetDefault()
        wx.EVT_BUTTON(parent, wx.ID_OK, self._wx_on_ok)
        sizer.Add(done)

        return sizer

    ###########################################################################
    # Protected 'SplitDialog' interface.
    ###########################################################################

    def _create_lhs(self, parent):
        """ Creates the panel containing the preference page tree. """

        return self._create_tree(parent)

    def _create_rhs(self, parent):
        """ Creates the panel containing the selected preference page. """

        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)

        # The 'pretty' title bar ;^)
        self.__title = HeadingText(panel)
        sizer.Add(
            self.__title.control, 0,
            wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
        )

        # The preference page of the node currently selected in the tree.
        self._layered_panel = LayeredPanel(panel, min_width=-1, min_height=-1)
        sizer.Add(
            self._layered_panel.control, 1,
            wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5
        )

        # The 'Restore Defaults' button etc.
        buttons = self._create_page_buttons(panel)
        sizer.Add(buttons, 0, wx.ALIGN_RIGHT | wx.TOP | wx.RIGHT, 5)

        # A separator.
        line = wx.StaticLine(panel, -1)
        sizer.Add(line, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)

        # Resize the panel to fit the sizer's minimum size.
        sizer.Fit(panel)

        return panel

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _create_tree(self, parent):
        """ Creates the preference page tree. """

        tree_viewer = TreeViewer(
            parent,
            input            = self.root,
            show_images      = False,
            show_root        = False,
            content_provider = DefaultTreeContentProvider()
        )

        tree_viewer.on_trait_change(self._on_selection_changed, 'selection')

        return tree_viewer.control

    def _create_page_buttons(self, parent):
        """ Creates the 'Restore Defaults' button, etc.

        At the moment the "etc." is an optional 'Help' button.

        """

        self._button_sizer = sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 'Help' button. Comes first so 'Restore Defaults' doesn't jump around.
        self._help = help = wx.Button(parent, -1, "Help")
        wx.EVT_BUTTON(parent, help.GetId(), self._on_help)
        sizer.Add(help, 0, wx.RIGHT, 5)

        # 'Restore Defaults' button.
        restore = wx.Button(parent, -1, "Restore Defaults")
        wx.EVT_BUTTON(parent, restore.GetId(), self._on_restore_defaults)
        sizer.Add(restore)

        return sizer

    ###########################################################################
    # wx event handlers.
    ###########################################################################

    def _on_restore_defaults(self, event):
        """ Called when the 'Restore Defaults' button is pressed. """

        page = self._pages[self._layered_panel.current_layer_name]
        page.restore_defaults()

        return

    def _on_help(self, event):
        """ Called when the 'Help' button is pressed. """

        page = self._pages[self._layered_panel.current_layer_name]
        page.show_help_topic()

        return

    ###########################################################################
    # Trait event handlers.
    ###########################################################################

    def _on_selection_changed(self, selection):
        """ Called when a node in the tree is selected. """

        if len(selection) > 0:
            # The tree is in single selection mode.
            node = selection[0]

            # We only show the help button if the selected node has a help
            # topic Id.
            if len(node.help_id) > 0:
                self._button_sizer.Show(self._help, True)

            else:
                self._button_sizer.Show(self._help, False)

            # Show the selected preference page.
            layered_panel  = self._layered_panel
            parent = self._layered_panel.control

            # If we haven't yet displayed the node's preference page during the
            # lifetime of this dialog, then we have to create it.
            if not layered_panel.has_layer(node.name):
                page = node.create_page()
                layered_panel.add_layer(node.name, page.create_control(parent))
                self._pages[node.name] = page

            layered_panel.show_layer(node.name)
            self.__title.text = node.name

        return

#### EOF ######################################################################
