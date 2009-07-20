#!/usr/bin/python
# =============================================================================
# Standard Python modules
# =============================================================================
import os, sys, string, pdb, copy, time

# =============================================================================
# External Python modules
# =============================================================================
from numpy import linspace, cos, pi, hstack, zeros, ones, sqrt, imag, interp, \
    array, real, reshape, meshgrid, dot, cross, vstack

# =============================================================================
# Extension modules
# =============================================================================
from matplotlib.pylab import *

# pySpline
sys.path.append('../pySpline/python')

#cfd-csm pre
sys.path.append('../../pyHF/pycfd-csm/python/')

#pyGeo
import pyGeo


# Wing Information

naf=8
airfoil_list = ['af15-16.inp','af15-16.inp','af15-16.inp','af15-16.inp','af15-16.inp','af15-16.inp','af15-16.inp','pinch.inp']
chord = [1.25,1,.8,.65,.65,0.65,.65,.65]
x = [1.25,1.25,1.25,1.25,1.25,1.25,1.25,1.25]
y = [0,0.1,0.2,0.4,.405,.55,.6,1.2]
z = [0,2,4,6,6.05,6.2,6.2,6.2]
rot_x = [0,0,0,0,0,-90,-90,-90]
rot_y = [0,0,0,0,0,0,0,0]
tw_aero = [-4,0,4,4.5,4.5,0,0,0] # ie rot_z
ref_axis1 = pyGeo.ref_axis(x,y,z,rot_x,rot_y,tw_aero)
offset = zeros((naf,2))
offset[:,0] = .25 #1/4 chord

# Make the break-point vector
breaks = [3,6] #zero based
Nctlv = [4,4,4] # Length breaks + 1

# Procedure for Using pyGEO

# Step 1: Run the folloiwng Commands: (Uncomment between -------)
# ---------------------------------------------------------------------
# wing = pyGeo.pyGeo('lifting_surface',xsections=airfoil_list,scale=chord,offset=offset,ref_axis=ref_axis1,breaks=breaks,fit_type='lms',Nctlu = 13,Nctlv=Nctlv)
# wing.calcEdgeConnectivity(1e-2,1e-2)
# wing.writeEdgeConnectivity('wing.con')
# wing.writeTecplot('wing.dat')
# print 'Done Step 1'
# sys.exit(0)
# ----------------------------------------------------------------------
# Now: -> Load wing.dat to check connectivity information and modifiy
# wing.con file to correct any connectivity info and set
# continuity. Re-run step 1 until all connectivity information and
# continutity information is correct.

# Step 2: -> Run the following Commands (Uncomment between --------)
# After step 1 we can load connectivity information from file,
# propagate the knot vectors, stitch the edges, and then fit the
# entire surfaces with continuity constraints.  This output is then
# saved as an igs file which is the archive format storage format we
# are using for bspline surfaces

# ----------------------------------------------------------------------
# wing = pyGeo.pyGeo('lifting_surface',xsections=airfoil_list,scale=chord,offset=offset,ref_axis=ref_axis1,breaks=breaks,fit_type='lms',Nctlu = 13,Nctlv=Nctlv)
# wing.readEdgeConnectivity('wing.con')
# wing.propagateKnotVectors()
# wing.stitchEdges()
# #wing.fitSurfaces()
# wing.writeTecplot('wing.dat')
# wing.writeIGES('wing.igs')
# print 'Done Step 2'
# sys.exit(0)
# ----------------------------------------------------------------------

# Step 3: -> After step 2 we now have two files we need, the stored
# iges file as well as the connectivity file. The IGES file which has
# been generated can be used to generate a 3D CFD mesh in ICEM.  Now
# to load a geometry for an optimization run we simply load the IGES
# file as well as the connectivity file and we are good to go.

# ----------------------------------------------------------------------

wing = pyGeo.pyGeo('iges',file_name='wing.igs')
wing.readEdgeConnectivity('wing.con')
wing.stitchEdges() # Just to be sure
print 'Done Step 3'

# ----------------------------------------------------------------------

# Step 4: Now the rest of the code is up to the user. The user only
# needs to run the commands in step 3 to fully define the geometry of
# interest

print 'Attaching Ref Axis...'
wing.setRefAxis([0,1,2,3,4,5],ref_axis1)
wing.writeTecplot('wing.dat',write_ref_axis=True,write_links=True)

# --------------------------------------
# Define Design Variable functions here:
# --------------------------------------
def span_extension(val,ref_axis):
    '''Single design variable for span extension'''
    print 'span'
    print 'ref axis before:',ref_axis.x
    ref_axis.x[0:4:,2] = ref_axis.x0[0:4,2] * val
    ref_axis.x[4:,2] = ref_axis.x0[4:,2]-ref_axis.x[3,2]
    print 'ref axis after:',ref_axis.x
    return ref_axis

def span_extension_prop(val,ref_axis):
    #print 'extension'
    #print 'ref axis before:',ref_axis.x
    #ref_axis.x[4:,2] = ref_axis.x[3,2] + (ref_axis.x0[4:,2] - ref_axis.x0[3,2])
    #print 'ref axis after:',ref_axis.x
    return ref_axis

def twist(val,ref_axis):
    '''Twist'''
    ref_axis.rot[1,2] = ref_axis.rot0[1,2] + val
    ref_axis.rot[2,2] = ref_axis.rot0[2,2] + val
    return ref_axis

def sweep(val,ref_axis):
    '''Sweep the wing'''
    ref_axis.x[:,0] = ref_axis.x0[:,0] +  val * ref_axis.xs.s
    return ref_axis

def set_chord(val,ref_axis):
    '''Set the scales (and thus chords) on the wing'''
    ref_axis.scale = val

    return ref_axis
# ------------------------------------------

wing.attachSurface()
sys.exit(0)

#                        Name, value, lower,upper,function, ref_axis_id
#wing.addGeoDV(pyGeo.geoDV('span_ext',0,0.5,2.0,span_extension_prop,0))
wing.addGeoDV(pyGeo.geoDV('span',1,0.5,2.0,span_extension,0))

#wing.addGeoDV(pyGeo.geoDV('twist',0,-20,20,twist,0))
#wing.addGeoDV(pyGeo.geoDV('sweep',0,-20,20,sweep,0))
#wing.addGeoDV(pyGeo.geoDV('chord',ones(8),0.1,2,set_chord,0))

wing.DV_list['span'].value = .5
#wing.DV_list['twist'].value = -25
#wing.DV_list['sweep'].value = 2
#wing.DV_list['chord'].value = [1.2,1.5,1.2,1.1,0.9,0.7,0.6,0.4]

timeA = time.time()
wing.update()
timeB = time.time()

print 'update time is :',timeB-timeA

wing.writeTecplot('wing2.dat',write_ref_axis=True,write_links=True)



# ---------------------
# Old Code Unused
# ---------------------



#ref_axis1.x[:,2] *= 1.2

#ref_axis1.x[:,0] += 2.4*ref_axis1.xs.s
#ref_axis1.x[:,0] = ref_axis1.x0[:,0] + 2

#ref_axis1.x[:,1] += 0.4*ref_axis1.xs.s**2
#ref_axis1.rot[1,2] = 30
#ref_axis1.rot[2,2]= 30
#ref_axis1.rot[:,2] = 0
# ref_axis1.scale[0,0] = 1.2
# ref_axis1.scale[1,0] = 1.5
# ref_axis1.scale[2,0] = 1.2
# ref_axis1.scale[3,0] = 1.1
# ref_axis1.scale[4,0] = 0.9
# ref_axis1.scale[5,0] = 0.7
# ref_axis1.scale[6,0] = 0.6
# ref_axis1.scale[7,0] = 0.4
 
