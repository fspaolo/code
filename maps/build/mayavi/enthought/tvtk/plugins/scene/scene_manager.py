""" Manage the TVTK scenes. """

# Enthought library imports.
from enthought.tvtk.pyface.tvtk_scene import TVTKScene
from enthought.pyface.workbench.api import WorkbenchWindow
from enthought.traits.api import HasTraits, List, Instance, Property
from enthought.traits.api import implements, on_trait_change
from enthought.tvtk.plugins.scene.scene_editor import SceneEditor

# Local imports.
from i_scene_manager import ISceneManager


class SceneManager(HasTraits):
    """ Manage the TVTK scenes. """

    implements(ISceneManager)

    #### 'SceneManager' interface #############################################

    # The currently active scene (None, if no scene is active).
    current_scene = Property(Instance(TVTKScene))

    # A list of all open scenes.
    scenes = List(TVTKScene)
    
    # The workbench window that the manager is in (there is one scene manager
    # per workbench window).
    window = Instance(WorkbenchWindow)
    
    #### Private interface ####################################################

    # Shadow trait for the 'current_scene' property.
    _current_scene = Instance(TVTKScene)

    ###########################################################################
    # 'SceneManager' interface.
    ###########################################################################

    #### Trait properties #####################################################
    
    def _get_current_scene(self):
        """ Property getter. """

        scene_count = len(self.scenes)
        if scene_count == 0:
            scene = None

        elif scene_count == 1:
            scene = self.scenes[0]

        else:
            scene = self._current_scene

        return scene

    def _set_current_scene(self, scene):
        """ Property setter. """
        
        self._current_scene = scene

        return
    
    #### Trait change handlers ################################################

    @on_trait_change('window:editor_opened')
    def _on_editor_opened(self, obj, trait_name, old, new):
        """ Dynamic trait change handler. """

        if isinstance(new, SceneEditor):
            self.scenes.append(new.scene)
            
        return

    @on_trait_change('window:editor_closing')
    def _on_editor_closed(self, obj, trait_name, old, new):
        """ Dynamic trait change handler. """

        if isinstance(new, SceneEditor):
            self.scenes.remove(new.scene)
            
        return

    @on_trait_change('window:active_editor')
    def _on_active_editor_changed(self, obj, trait_name, old, new):
        """ Dynamic trait change handler. """

        if isinstance(new, SceneEditor):
            self.current_scene = new.scene

        else:
            self.current_scene = None
            
        return
    
#### EOF ######################################################################



