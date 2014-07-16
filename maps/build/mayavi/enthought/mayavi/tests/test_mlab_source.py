"""
Test for MlabSource and its subclasses.
"""
# Author: Prabhu Ramachandran <prabhu@aero.iitb.ac.in>
# Copyright (c) 2008, Enthought, Inc.
# License: BSD Style.

import unittest
import numpy as N

from enthought.mayavi.tools import sources

################################################################################
# `TestMGlyphSource`
################################################################################ 
class TestMGlyphSource(unittest.TestCase):
    def setUp(self):
        self.x = x = N.ones(10, float)
        self.y = y = N.ones(10, float)*2.0
        self.z = z = N.linspace(0, 10, 10)
        self.v = v = N.ones((10, 3), float)*10.0
        self.s = s = N.ones(10, float)
        src = sources.MGlyphSource()
        src.reset(x=x, y=y, z=z, u=v[:,0], v=v[:,1], w=v[:,2], scalars=s)
        self.src = src

    def tearDown(self):
        return

    def get_data(self):
        return self.x, self.y, self.z, self.v, self.s, self.src

    def check_traits(self):
        """Check if the sources traits are set correctly."""
        x, y, z, v, s, src = self.get_data()
        # Check if points are set correctly.
        self.assertEqual(N.alltrue(src.points[:,0].ravel() == x), True)
        self.assertEqual(N.alltrue(src.points[:,1].ravel() == y), True)
        self.assertEqual(N.alltrue(src.points[:,2].ravel() == z), True)
        # Check the vectors and scalars.
        self.assertEqual(N.alltrue(src.vectors == v), True)
        self.assertEqual(N.alltrue(src.scalars == s), True)

    def check_dataset(self):
        """Check the TVTK dataset."""
        x, y, z, v, s, src = self.get_data()
        # Check if the dataset is setup right.
        pts = src.dataset.points.to_array()
        self.assertEqual(N.alltrue(pts[:,0].ravel() == x), True)
        self.assertEqual(N.alltrue(pts[:,1].ravel() == y), True)
        self.assertEqual(N.alltrue(pts[:,2].ravel() == z), True)
        vec = src.dataset.point_data.vectors.to_array()
        sc = src.dataset.point_data.scalars.to_array()
        self.assertEqual(N.alltrue(vec == v), True)
        self.assertEqual(N.alltrue(sc == s), True)

    def test_reset(self):
        "Test the reset method."
        x, y, z, v, s, src = self.get_data()
        self.check_traits()
        self.check_dataset()

        # Call reset again with just a few things changed to see if it
        # works correctly.
        x *= 5.0
        s *= 10
        v *= 0.1
        src.reset(x=x, u=v[:,0], v=v[:,1], w=v[:,2], scalars=s)

        self.check_traits()
        self.check_dataset()

    def test_reset1(self):

        "Test the reset method."
        x, y, z, v, s, src = self.get_data()
        self.check_traits()
        self.check_dataset()
        # Call reset again with just a few things changed to see if it
        # works correctly.
        
        self.x = x = N.ones(20, float)*30.0
        self.y = y = N.ones(20, float)*30.0
        self.z = z = N.ones(20, float)*30.0
        points = N.ones((20, 3), float)*30.0
        self.s = s = N.ones(20, float)
        self.v = v = N.ones((20, 3), float)*30.0  
       
        src.reset(x=x,y=y,z=z, u=v[:,0], v=v[:,1], w=v[:,2], scalars=s,points=points,vectors=v)       
        self.check_traits()
        self.check_dataset()

    def test_handlers(self):
        "Test if the various static handlers work correctly."
        x, y, z, v, s, src = self.get_data()
        x *= 2.0
        y *= 2.0
        z *= 2.0
        v *= 2.0
        s *= 2.0
        src.x = x
        src.y = y
        src.z = z 
        src.u = v[:,0]
        src.v = v[:,1]
        src.w = v[:,2]
        src.scalars = s
        self.check_traits()
        self.check_dataset()

    def test_set(self):
        "Test if the set method works correctly."
        x, y, z, v, s, src = self.get_data()
        x *= 2.0
        z *= 2.0
        s *= 2.0
        src.set(x=x, z=z, scalars=s)
        self.check_traits()
        self.check_dataset()

    def test_strange_shape(self):
        " Test the MGlyphSource with strange shapes for the arguments "
        x, y, z, v, s, src = self.get_data()
        x = y = z = v = s = 0
        src.reset(x=x, y=y, z=z, u=v, v=v, w=v, scalars=None)
        src.reset(x=x, y=y, z=z, u=v, v=v, w=v, scalars=s)       
        x = y = z = v = s = 1
        src.set(x=x, y=y, z=z, u=v, v=v, w=v, scalars=None) 
        src.set(x=x, y=y, z=z, u=v, v=v, w=v, scalars=s)       


################################################################################
# `TestMGlyphSource`
################################################################################ 
class TestMVerticalSource(unittest.TestCase):
    def setUp(self):
        self.x = x = N.ones(10, float)
        self.y = y = N.ones(10, float)*2.0
        self.z = z = N.linspace(0, 10, 10)
        self.s = s = N.ones(10, float)
        src = sources.MVerticalGlyphSource()
        src.reset(x=x, y=y, z=z, scalars=s)
        self.src = src

    def tearDown(self):
        return

    def get_data(self):
        return self.x, self.y, self.z, self.s, self.src

    def check_traits(self):
        """Check if the sources traits are set correctly."""
        x, y, z, s, src = self.get_data()
        # Check if points are set correctly.
        self.assertEqual(N.alltrue(src.points[:,0].ravel() == x), True)
        self.assertEqual(N.alltrue(src.points[:,1].ravel() == y), True)
        self.assertEqual(N.alltrue(src.points[:,2].ravel() == z), True)
        # Check the vectors and scalars.
        self.assertEqual(N.alltrue(src.vectors[:, -1] == s), True)
        self.assertEqual(N.alltrue(src.vectors[:, :-1] == 1), True)
        self.assertEqual(N.alltrue(src.scalars == s), True)

    def check_dataset(self):
        """Check the TVTK dataset."""
        x, y, z, s, src = self.get_data()
        # Check if the dataset is setup right.
        pts = src.dataset.points.to_array()
        self.assertEqual(N.alltrue(pts[:,0].ravel() == x), True)
        self.assertEqual(N.alltrue(pts[:,1].ravel() == y), True)
        self.assertEqual(N.alltrue(pts[:,2].ravel() == z), True)
        vec = src.dataset.point_data.vectors.to_array()
        sc = src.dataset.point_data.scalars.to_array()
        self.assertEqual(N.alltrue(vec[:, -1] == s), True)
        self.assertEqual(N.alltrue(vec[:, :-1] == 1), True)
        self.assertEqual(N.alltrue(sc == s), True)

    def test_reset(self):
        "Test the reset method."
        x, y, z, s, src = self.get_data()
        self.check_traits()
        self.check_dataset()

        # Call reset again with just a few things changed to see if it
        # works correctly.
        x *= 5.0
        s *= 10
        src.reset(x=x, scalars=s)

        self.check_traits()
        self.check_dataset()

    def test_reset1(self):

        "Test the reset method."
        x, y, z, s, src = self.get_data()
        self.check_traits()
        self.check_dataset()
        # Call reset again with just a few things changed to see if it
        # works correctly.
        
        self.x = x = N.ones(20, float)*30.0
        self.y = y = N.ones(20, float)*30.0
        self.z = z = N.ones(20, float)*30.0
        points = N.ones((20, 3), float)*30.0
        self.s = s = N.ones(20, float)
       
        src.reset(x=x, y=y, z=z, scalars=s, points=points)
        self.check_traits()
        self.check_dataset()

    def test_handlers(self):
        "Test if the various static handlers work correctly."
        x, y, z, s, src = self.get_data()
        x *= 2.0
        y *= 2.0
        z *= 2.0
        s *= 2.0
        src.x = x
        src.y = y
        src.z = z 
        src.scalars = s
        self.check_traits()
        self.check_dataset()

    def test_set(self):
        "Test if the set method works correctly."
        x, y, z, s, src = self.get_data()
        x *= 2.0
        z *= 2.0
        s *= 2.0
        src.set(x=x, z=z, scalars=s)
        self.check_traits()
        self.check_dataset()


################################################################################
# `TestMArraySource`
################################################################################ 
class TestMArraySource(unittest.TestCase):
    def setUp(self):
        x, y, z = N.ogrid[-10:10:11j, 
                          -10:10:12j, 
                          -10:10:20j]
        self.x, self.y, self.z = x, y, z
        dims = (x.shape[0], y.shape[1], z.shape[2])
        self.v = v = N.ones(dims + (3,), float)
        v[...,2] = 2
        v[...,2] = 3 
        self.s = s = N.ones(dims, float)
        src = sources.MArraySource()
        src.reset(x=x, y=y, z=z, u=v[...,0], v=v[...,1], w=v[...,2], scalars=s)
        self.src = src

    def tearDown(self):
        return

    def get_data(self):
        return self.x, self.y, self.z, self.v, self.s, self.src

    def check_traits(self):
        """Check if the sources traits are set correctly."""
        x, y, z, v, s, src = self.get_data()
        # Check if points are set correctly.
        self.assertEqual(N.alltrue(src.x == x), True)
        self.assertEqual(N.alltrue(src.y == y), True)
        self.assertEqual(N.alltrue(src.z == z), True)
        # Check the vectors and scalars.
        self.assertEqual(N.alltrue(src.vectors == v), True)
        self.assertEqual(N.alltrue(src.scalars == s), True)

    def check_dataset(self):
        """Check the TVTK dataset."""
        x, y, z, v, s, src = self.get_data()
        # Check if the dataset is setup right.
        dx = x[1, 0, 0] - x[0, 0, 0]
        dy = y[0, 1, 0] - y[0, 0, 0]
        dz = z[0, 0, 1] - z[0, 0, 0]
        origin = [x.min(), y.min(), z.min()]
        spacing = [dx, dy, dz]
        dimensions = (x.shape[0], y.shape[1], z.shape[2])
        ds = src.dataset
        self.assertEqual(N.all(src.m_data.origin == origin), True)
        self.assertEqual(N.allclose(src.m_data.spacing, spacing), True)
        self.assertEqual(N.allclose(ds.dimensions, dimensions), True)

        vec = src.dataset.point_data.vectors.to_array()
        sc = src.dataset.point_data.scalars.to_array()
        v1 = v.transpose((2, 0, 1, 3))
        self.assertEqual(N.alltrue(vec.ravel() == v1.ravel()), True)
        s1 = s.transpose()
        self.assertEqual(N.alltrue(sc.ravel() == s1.ravel()), True)

    def test_reset(self):
        "Test the reset method."
        x, y, z, v, s, src = self.get_data()
        self.check_traits()
        self.check_dataset()

        # Call reset again with just a few things changed to see if it
        # works correctly.
        x *= 5.0
        s *= 10
        v *= 0.1
        src.reset(x=x, u=v[...,0], v=v[...,1], w=v[...,2], scalars=s)

        self.check_traits()
        self.check_dataset()

    def test_reset1(self):
        "Test the reset method."
        x, y, z, v, s, src = self.get_data()
        self.check_traits()
        self.check_dataset()
        # Call reset again with just a few things changed to see if it
        # works correctly.

        x, y, z = N.ogrid[-10:10:11j, 
                          -10:10:12j, 
                          -10:10:20j]
        self.x, self.y, self.z = x, y, z
        
        dims = (x.shape[0], y.shape[1], z.shape[2])
        self.v = v = N.ones(dims + (3,), float)
        v[...,2] = 2
        v[...,2] = 3 
        self.s = s = N.ones(dims, float)
        src = sources.MArraySource()
        src.reset(x=x, y=y, z=z, u=v[...,0], v=v[...,1], w=v[...,2], scalars=s,vectors=v)      
        self.check_traits()
        self.check_dataset()
        
    def test_handlers(self):
        "Test if the various static handlers work correctly."
        x, y, z, v, s, src = self.get_data()
        x *= 2.0
        y *= 2.0
        z *= 2.0
        v *= 2.0
        s *= 2.0
        src.x = x
        src.y = y
        src.z = z 
        src.u = v[...,0]
        src.v = v[...,1]
        src.w = v[...,2]
        src.scalars = s
        self.check_traits()
        self.check_dataset()

    def test_set(self):
        "Test if the set method works correctly."
        x, y, z, v, s, src = self.get_data()
        x *= 2.0
        z *= 2.0
        s *= 2.0
        src.set(x=x, z=z, scalars=s)
        self.check_traits()
        self.check_dataset()



################################################################################
# `TestMLineSource`
################################################################################ 
class TestMLineSource(unittest.TestCase):
    def setUp(self):
        self.x = x = N.ones(10, float)
        self.y = y = N.ones(10, float)*2.0
        self.z = z = N.linspace(0, 10, 10)
        self.s = s = N.ones(10, float)
        src = sources.MLineSource()
        src.reset(x=x, y=y, z=z, scalars=s)
        self.src = src

    def tearDown(self):
        return

    def get_data(self):
        return self.x, self.y, self.z, self.s, self.src

    def check_traits(self):
        """Check if the sources traits are set correctly."""
        x, y, z, s, src = self.get_data()
        # Check if points are set correctly.
        self.assertEqual(N.alltrue(src.points[:,0].ravel() == x), True)
        self.assertEqual(N.alltrue(src.points[:,1].ravel() == y), True)
        self.assertEqual(N.alltrue(src.points[:,2].ravel() == z), True)
        # Check the scalars.
        self.assertEqual(N.alltrue(src.scalars == s), True)

    def check_dataset(self):
        """Check the TVTK dataset."""
        x, y, z, s, src = self.get_data()
        # Check if the dataset is setup right.
        pts = src.dataset.points.to_array()
        self.assertEqual(N.alltrue(pts[:,0].ravel() == x), True)
        self.assertEqual(N.alltrue(pts[:,1].ravel() == y), True)
        self.assertEqual(N.alltrue(pts[:,2].ravel() == z), True)
        sc = src.dataset.point_data.scalars.to_array()
        self.assertEqual(N.alltrue(sc == s), True)

    def test_reset(self):
        "Test the reset method."
        x, y, z, s, src = self.get_data()
        self.check_traits()
        self.check_dataset()

        # Call reset again with just a few things changed to see if it
        # works correctly.
        x *= 5.0
        s *= 10
        src.reset(x=x, scalars=s)

        self.check_traits()
        self.check_dataset()

        y *= 6.0
        x *= 4
        src.reset(x=x, y=y)

        self.check_traits()
        self.check_dataset()

        s *= 4.5
        y /= 4
        src.reset(y=y, s=s)

        self.check_traits()
        self.check_dataset()

    def test_reset1(self):

        "Test the reset method."
        x, y, z, s, src = self.get_data()
        self.check_traits()
        self.check_dataset()
        # Call reset again with just a few things changed to see if it
        # works correctly.
        
        self.x = x = N.ones(20, float)*30.0
        self.y = y = N.ones(20, float)*30.0
        self.z = z = N.ones(20, float)*30.0
        points = N.ones((20, 3), float)*30.0
        self.s = s = N.ones(20, float)                 
        src.reset(x=x,y=y,z=z,scalars=s,points=points)       
        self.check_traits()
        self.check_dataset()


        

    def test_handlers(self):
        "Test if the various static handlers work correctly."
        x, y, z, s, src = self.get_data()
        x *= 2.0
        y *= 2.0
        z *= 2.0
        s *= 2.0
        src.x = x
        src.y = y
        src.z = z 
        src.scalars = s
        self.check_traits()
        self.check_dataset()

    def test_set(self):
        "Test if the set method works correctly."
        x, y, z, s, src = self.get_data()
        x *= 2.0
        z *= 2.0
        s *= 2.0
        src.set(x=x, z=z, scalars=s)
        self.check_traits()
        self.check_dataset()

        
        y *= 2.0
        s *= 2.0
        src.set(y=y, scalars=s)
        self.check_traits()
        self.check_dataset()



################################################################################
# `TestMArray2DSource`
################################################################################ 
class TestMArray2DSource(unittest.TestCase):
    def setUp(self):
        x, y = N.mgrid[-10:10:11j, 
                          -10:10:12j]          
       
        self.x, self.y  = x, y
        dims = (x.shape[0], y.shape[1])        
        self.s = s = N.ones(dims, float)
        src = sources.MArray2DSource()
        src.reset(x=x, y=y,scalars=s)
        self.src = src

    def tearDown(self):
        return

    def get_data(self):
        return self.x, self.y, self.s, self.src

    def check_traits(self):
        """Check if the sources traits are set correctly."""
        x, y, s, src = self.get_data()

        # Check if points are set correctly.        
        self.assertEqual(N.alltrue(src.x == x), True)
        self.assertEqual(N.alltrue(src.y == y), True)
        # Check the scalars.       
        self.assertEqual(N.alltrue(src.scalars == s), True)

    def check_dataset(self):
        """Check the TVTK dataset."""
        x, y, s, src = self.get_data()
        # Check if the dataset is setup right.
        x = N.atleast_2d(x.squeeze().T)[0, :].squeeze()
        y = N.atleast_2d(y.squeeze())[0, :].squeeze()
        dx = x[1] - x[0]
        dy = y[1] - y[0]
       
        origin = [x.min(), y.min(),0 ]
        spacing = [dx, dy, 1]
        ds = src.dataset
        self.assertEqual(N.all(ds.origin == origin), True)
        self.assertEqual(N.allclose(src.m_data.spacing, spacing), True)
              
        sc = src.dataset.point_data.scalars.to_array()      
        s1 = s.transpose()
        self.assertEqual(N.alltrue(sc.ravel() == s1.ravel()), True)

    def test_reset(self):
        "Test the reset method."
        
        x, y, s, src = self.get_data()

        self.check_traits()
        self.check_dataset()

        # Call reset again with just a few things changed to see if it
        # works correctly.
        x *= 5.0
        s *= 10       
        src.reset(x=x,y=y, scalars=s)
       

        self.check_traits()
        self.check_dataset()

    def test_handlers(self):
        "Test if the various static handlers work correctly."
        x, y, s, src = self.get_data()
        x *= 2.0
        y *= 2.0
        s *= 2.0
        src.x = x
        src.y = y       
        src.scalars = s
       
        self.check_traits()
        self.check_dataset()

   
    def test_set(self):
        "Test if the set method works correctly."
        x, y, s, src  = self.get_data()
        x *= 2.0        
        s *= 2.0
        src.set(x=x,scalars=s)

      
        self.check_traits()
        self.check_dataset()

        y *= 9.0
        s *= 2.0
        src.set(y=y, scalars=s)
        self.check_traits()
        self.check_dataset()

################################################################################
# `TestMGridSource`
################################################################################ 
class TestMGridSource(unittest.TestCase):
    def setUp(self):
        self.x = x = N.ones([10,10], float)
        self.y = y = N.ones([10,10], float)*2.0
        self.z = z = N.ones([10,10], float)*3.0
        self.s = s = N.ones([10,10], float)
        src = sources.MGridSource()
        src.reset(x=x, y=y, z=z, scalars=s)
        self.src = src

    def tearDown(self):
        return

    def get_data(self):
        return self.x, self.y, self.z, self.s, self.src

    def check_traits(self):
        """Check if the sources traits are set correctly."""
        x, y, z, s, src = self.get_data()
       
        # Check if points are set correctly.
        self.assertEqual(N.alltrue(src.points[:,0].ravel() == x.ravel()), True)
        self.assertEqual(N.alltrue(src.points[:,1].ravel() == y.ravel()), True)
        self.assertEqual(N.alltrue(src.points[:,2].ravel() == z.ravel()), True)
        # Check the  scalars.
        
        self.assertEqual(N.alltrue(src.scalars == s), True)

    def check_dataset(self):
        """Check the TVTK dataset."""
        x, y, z, s, src = self.get_data()
        # Check if the dataset is setup right.
       
        pts = src.dataset.points.to_array()
        self.assertEqual(N.alltrue(pts[:,0].ravel() == x.ravel()), True)
        self.assertEqual(N.alltrue(pts[:,1].ravel() == y.ravel()), True)
        self.assertEqual(N.alltrue(pts[:,2].ravel() == z.ravel()), True)
        sc = src.dataset.point_data.scalars.to_array()
        self.assertEqual(N.alltrue(sc == s.ravel()), True)

    def test_reset(self):
        "Test the reset method."
        
        x, y, z, s, src = self.get_data()
        self.check_traits()
        self.check_dataset()

        # Call reset again with just a few things changed to see if it
        # works correctly.
        x *= 5.0
        s *= 10
       
        src.reset(x=x, scalars=s)
        self.check_traits()
        self.check_dataset()

    def test_handlers(self):
        "Test if the various static handlers work correctly."
        x, y, z, s, src = self.get_data()
        x *= 2.0
        y *= 2.0
        z *= 2.0
        s *= 2.0
        src.x = x
        src.y = y
        src.z = z 
        src.scalars = s
        self.check_traits()
        self.check_dataset()

    def test_set(self):
        "Test if the set method works correctly."
        x, y, z, s, src = self.get_data()
        x *= 2.0
        z *= 2.0
        s *= 2.0
        src.set(x=x, z=z, scalars=s)
        self.check_traits()
        self.check_dataset()

################################################################################
# `TestMArray2DSourceNoArgs`
################################################################################ 
class TestMArray2DSourceNoArgs(unittest.TestCase):
    """Special Test Case for MArray2DSource when both x and y are specified as None"""
    def setUp(self):
        
        x=None
        y=None
       
        self.x, self.y  = x, y
        
        if x is not None and y is not None:
            dims = (x.shape[0], y.shape[1])
        else:
            dims=(10,10)

        self.s = s = N.ones(dims, float)
        src = sources.MArray2DSource()
        src.reset(x=x, y=y,scalars=s)
        self.src = src

    def tearDown(self):
        return

    def get_data(self):
        return self.x, self.y, self.s, self.src

    def check_traits(self):
        """Check if the sources traits are set correctly."""
        x, y, s, src = self.get_data()
        # Check if points are set correctly.

        if x is not None and y is not None:
            self.assertEqual(N.alltrue(src.x == x), True)
            self.assertEqual(N.alltrue(src.y == y), True)
        
        else:
            nx, ny = s.shape        
            x1, y1 = N.mgrid[-nx/2.:nx/2, -ny/2.:ny/2]            
            self.assertEqual(N.alltrue(src.x == x1), True)
            self.assertEqual(N.alltrue(src.y == y1), True)
    
        # Check the scalars.       
        self.assertEqual(N.alltrue(src.scalars == s), True)

    def check_dataset(self):
        """Check the TVTK dataset."""
        x, y, s, src = self.get_data()
        # Check if the dataset is setup right.

        nx, ny = src.scalars.shape

        if x is None and y is None:
            x, y = N.mgrid[-nx/2.:nx/2, -ny/2.:ny/2]

        x = N.atleast_2d(x.squeeze().T)[0, :].squeeze()
        y = N.atleast_2d(y.squeeze())[0, :].squeeze()
        dx = x[1] - x[0]
        dy = y[1] - y[0]        
        origin = [x.min(), y.min(),0 ]
        spacing = [dx, dy, 1]      
        ds = src.dataset
        self.assertEqual(N.all(ds.origin == origin), True)
        self.assertEqual(N.allclose(ds.spacing, spacing), True)
       
        sc = src.dataset.point_data.scalars.to_array()      
        s1 = s.transpose()
        self.assertEqual(N.alltrue(sc.ravel() == s1.ravel()), True)

    def test_reset(self):
        "Test the reset method."       
        x, y, s, src = self.get_data()  

        self.check_traits()
        self.check_dataset()

        # Call reset again with just a few things changed to see if it
        # works correctly.
      
        s *= 10       
        src.reset(x=x,y=y, scalars=s)           

        self.check_traits()
        self.check_dataset()

    def test_handlers(self):
        "Test if the various static handlers work correctly."       
        x, y, s, src = self.get_data()       
        s *= 2.0         
        src.scalars = s
       
        self.check_traits()
        self.check_dataset()

   
    def test_set(self):
        "Test if the set method works correctly."       
        x, y, s, src = self.get_data()             
        s *= 2.0
        src.set(x=x,y=y,scalars=s)
      
        self.check_traits()
        self.check_dataset()


################################################################################
# `TestMTriangularMeshSource`
################################################################################ 
class TestMTriangularMeshSource(unittest.TestCase):
    def setUp(self):
        x, y, z = N.array([0, 0, 0]), N.array([0, 0, 1]), N.array([0, 1, 1])
        s = N.array([0.1, 0.2, 0.3])
        self.x, self.y, self.z, self.s = x, y, z, s
        self.triangles = triangles = N.array([[0, 1, 2]])
      
        src = sources.MTriangularMeshSource()
        src.reset(x=x, y=y, z=z, triangles=triangles, scalars=s)
        self.src = src

    def tearDown(self):
        return

    def get_data(self):
        return self.x, self.y, self.z, self.triangles, self.s, self.src

    def check_traits(self):
        """Check if the sources traits are set correctly."""
        x, y, z, triangles, s, src = self.get_data()
       
        # Check if points are set correctly.        
        self.assertEqual(N.alltrue(src.x == x), True)
        self.assertEqual(N.alltrue(src.y == y), True)
        self.assertEqual(N.alltrue(src.z == z), True)
        # Check the scalars.       
        self.assertEqual(N.alltrue(src.scalars == s), True)

    def test_reset(self):
        "Test the reset method."
        
        x, y, z, triangles, s, src = self.get_data()
        self.check_traits()

        # Call reset again with just a few things changed to see if it
        # works correctly.
        x *= 5.0
        s *= 10       
        src.reset(x=x,y=y,z=z, triangles=triangles, scalars=s)     

        self.check_traits()

    def test_changed_size(self):
        """ Change the number of the points, and establish
            to new points, to check that we don't get errors with the
            dimensions of the scalars.
        """
        n = 100
        _, _, _, _, _, src = self.get_data()
        triangles = N.c_[N.arange(n-3),
                            N.arange(n-3)+1,
                            n-1-N.arange(n-3)]
        x, y, z = N.random.random((3, n))
        src.reset(x=x, y=y, z=z, triangles=triangles)


    def test_handlers(self):
        "Test if the various static handlers work correctly."
        x, y, z, triangles, s, src = self.get_data()
        x *= 2.0
        y *= 2.0
        s *= 2.0
        src.x = x
        src.y = y       
        src.scalars = s
        src.triangles = triangles
       
        self.check_traits()

   
    def test_set(self):
        "Test if the set method works correctly."
        x, y, z, triangles, s, src = self.get_data()
        x *= 2.0        
        s *= 2.0
        src.set(x=x,scalars=s) 
     
        self.check_traits()

        y *= 9.0
        s *= 2.0
        src.set(y=y, scalars=s)

        self.check_traits()



if __name__ == '__main__':
    unittest.main()
