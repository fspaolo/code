#!/usr/bin/env python

# Author: Raashid Baig <raashid@aero.iitb.ac.in>
# License: BSD Style.

from enthought.tvtk.tools.visual import curve, box, vector, show
from numpy import arange, array

lorenz = curve( color = (1,1,1), radius=0.3 )

# Draw grid
for x in xrange(0,51,10):
    curve(points = [[x,0,-25],[x,0,25]], color = (0,0.5,0), radius = 0.3 )
    box(pos=(x,0,0), axis=(0,0,50), height=0.4, width=0.4, length = 50)

for z in xrange(-25,26,10):
    curve(points = [[0,0,z], [50,0,z]] , color = (0,0.5,0), radius = 0.3 )
    box(pos=(25,0,z), axis=(50,0,0), height=0.4, width=0.4, length = 50)

dt = 0.01
y = vector(35.0, -10.0, -7.0)

pts = []
for i in xrange(2000):
    # Integrate a funny differential equation
    dydt = vector(      -8.0/3*y[0] + y[1]*y[2],
                          - 10*y[1] +   10*y[2],
                   - y[1]*y[0] + 28*y[1] - y[2])
    y = y + dydt * dt
    
    pts.append(y)
    if len(pts) > 20:
        lorenz.extend(pts)
        pts[:] = []

show()
