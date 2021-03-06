"""An Image file reader object.

"""
# Author:  KK Rai (kk.rai [at] iitb.ac.in)
#          R. Ambareesha (ambareesha [at] iitb.ac.in)
#          Chandrashekhar Kaushik
#          Suyog Dutt Jain <suyog.jain [at] aero.iitb.ac.in>
#          Prabhu Ramachandran <prabhu [at] aero.iitb.ac.in>
# Copyright (c) 2007, Enthought, Inc.
# License: BSD Style.

from os.path import basename

# Enthought library imports.
from enthought.traits.api import Instance, Str, Dict
from enthought.traits.ui.api import View, Group, Item, Include
from enthought.tvtk.api import tvtk

# Local imports.
from enthought.mayavi.core.file_data_source import FileDataSource
from enthought.mayavi.core.pipeline_info import PipelineInfo


########################################################################
# `ImageReader` class
########################################################################
class ImageReader(FileDataSource):

    """A Image file reader. The reader supports all the
    different types of Image files.
    """

    # The version of this class.  Used for persistence.
    __version__ = 0

    # The Image data file reader.
    reader = Instance(tvtk.Object, allow_none=False, record=True)    

    # Information about what this object can produce.
    output_info = PipelineInfo(datasets=['image_data'])

    # Our view.
    view = View(Group(Include('time_step_group'),
                      Item(name='base_file_name'),
                      Item(name='reader',
                           style='custom',
                           resizable=True),
                      show_labels=False),
                resizable=True)

    ######################################################################
    # Private Traits   
    _image_reader_dict = Dict(Str, Instance(tvtk.Object))

    ######################################################################
    # `object` interface
    ######################################################################
    def __init__(self, **traits):
        d = {'bmp':tvtk.BMPReader(),
             'jpg':tvtk.JPEGReader(),
             'png':tvtk.PNGReader(),
             'pnm':tvtk.PNMReader(),
             'dcm':tvtk.DICOMImageReader(),
             'tiff':tvtk.TIFFReader(),           
             'ximg':tvtk.GESignaReader(),
             'dem':tvtk.DEMReader(),          
             'mha':tvtk.MetaImageReader(),
             'mhd':tvtk.MetaImageReader(),
            }
        # Account for pre 5.2 VTk versions, without MINC reader
        if hasattr(tvtk, 'MINCImageReader'):
            d['mnc'] = tvtk.MINCImageReader()
        d['jpeg'] = d['jpg']
        self._image_reader_dict = d
        # Call parent class' init.
        super(ImageReader, self).__init__(**traits)

    def __set_pure_state__(self, state):
        # The reader has its own file_name which needs to be fixed.
        state.reader.file_name = state.file_path.abs_pth
        # Now call the parent class to setup everything.
        super(ImageReader, self).__set_pure_state__(state) 
    
    ######################################################################
    # `FileDataSource` interface
    ######################################################################
    def update(self):
        self.reader.update()        
        if len(self.file_path.get()) == 0:
            return
        self.render()
  
    ######################################################################
    # Non-public interface
    ######################################################################
    def _file_path_changed(self, fpath):
        value = fpath.get()
        if len(value) == 0:
            return
        # Extract the file extension
        splitname = value.strip().split('.')
        extension = splitname[-1].lower()
        # Select image reader based on file type
        old_reader = self.reader
        if self._image_reader_dict.has_key(extension):
            self.reader = self._image_reader_dict[extension]
        else:
            self.reader = tvtk.ImageReader()

        self.reader.file_name = value.strip()
        self.reader.update()
        self.reader.update_information()
        
        if old_reader is not None:
            old_reader.on_trait_change(self.render, remove=True)
        self.reader.on_trait_change(self.render)

        self.outputs = [self.reader.output]

        # Change our name on the tree view
        self.name = self._get_name()

    def _get_name(self):
        """ Returns the name to display on the tree view.  Note that
        this is not a property getter.  
        """
        fname = basename(self.file_path.get())
        ret = "%s"%fname
        if len(self.file_list) > 1:
            ret += " (timeseries)"
        if '[Hidden]' in self.name:
            ret += ' [Hidden]'

        return ret

