"""Actions to start various modules.

"""
# Author: Prabhu Ramachandran <prabhu_r@users.sf.net>
# Copyright (c) 2005-2008, Enthought, Inc.
# License: BSD Style.

import new

# Local imports.
from enthought.mayavi.core.registry import registry
from enthought.mayavi.core.metadata import ModuleMetadata
from enthought.mayavi.core.pipeline_info import PipelineInfo
from enthought.mayavi.action.filters import FilterAction

######################################################################
# `ModuleAction` class.
######################################################################
class ModuleAction(FilterAction):

    ###########################################################################
    # 'Action' interface.
    ###########################################################################
    def perform(self, event):
        """ Performs the action. """
        callable = self.metadata.get_callable()
        obj = callable()
        mv = self.mayavi
        mv.add_module(obj)
        mv.engine.current_selection = obj


######################################################################
# `AddModuleManager` class.
######################################################################
class AddModuleManager(ModuleAction):
    """ An action that adds a ModuleManager to the tree. """

    tooltip       = "Add a ModuleManager to the current source/filter"

    description   = "Add a ModuleManager to the current source/filter"

    metadata = ModuleMetadata(id="AddModuleManager",
                class_name="enthought.mayavi.core.module_manager.ModuleManager",
                menu_name="&Add ModuleManager",
                tooltip="Add a ModuleManager to the current source/filter",
                description="Add a ModuleManager to the current source/filter",
                input_info = PipelineInfo(datasets=['any'],
                                  attribute_types=['any'],
                                  attributes=['any'])
                )

    def perform(self, event):
        """ Performs the action. """
        from enthought.mayavi.core.module_manager import ModuleManager
        mm = ModuleManager()
        mv = self.mayavi
        mv.add_module(mm)
        mv.engine.current_selection = mm 


######################################################################
# Creating the module actions automatically.
for module in registry.modules:
    d = {'tooltip': module.tooltip,
         'description': module.desc,
         'metadata': module}
    action = new.classobj(module.id, (ModuleAction,), d)
    globals()[module.id] = action

