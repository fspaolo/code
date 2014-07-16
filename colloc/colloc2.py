#!/usr/bin/env python

#    colloc.py - Program to compute Free-air Anomaly or Geoid Height 
#    by the Least Squares Collocation (LSC) method, using sea surface 
#    gradients (SDH) and marine gravity anomalies (GRAV) as data type.
#    
#    Input < observations of type (1) SDH or (2) SDH + GRAV
#    Output > signal of type (a) GRAV or (b) GEOID
#    
#    Author:	Fernando Paolo 
#    Date:		Jan/2009.
#    Usage:		python colloc.py -h


import numpy as N
import optparse
from sys import argv, exit
from scipy import weave
from scipy.weave.converters import blitz

# Scan comand line arguments ----------------------------------------------

usage = "python %prog [options]"
epilog = "Units: lon (deg), lat (deg), esph_dist (deg), SSH (m), " + \
         "SDH (m), grav (mGal), geoid (m), cov_ll (m**2), " + \
		 "cov_mm (m**2), cov_gg (mGal**2), cov_gl (mGal*m), cov_nl (m*m)"""
parser = optparse.OptionParser(usage=usage, epilog=epilog)
parser.add_option('-E', 
    	          dest='filesdh',
                  default=None, 
                  help='data file with observations of type "SDH": -Esdh.txt',
                  )
parser.add_option('-G', 
    	          dest='filegrav',
                  default=None, 
                  help='data file with observations of type "GRAV": -Ggrav.txt',
                  )
parser.add_option('-e',
    	          dest='colsd',
                  default='(0,1,2,3)', 
                  help='cols to be loaded from FILESDH [lon,lat,sdh,azmth,err]: -e0,1,2,3',
                  )
parser.add_option('-g',
    	          dest='colsg',
                  default='(0,1,2,3)', 
                  help='cols to be loaded from FILEGRAV [lon,lat,grav,err]: -g0,1,2,3',
                  )
parser.add_option('-S', 
				  dest='signal',
				  default='g', 
				  help='signal to be computed of type "g" (grav) or "n" (geoid): -Sg',
				  )
parser.add_option('-A',
    	          dest='covhh',
                  default='covhh.txt', 
                  help='file with C_hh [deg,cov]: -Acovhh.txt',
                  )
parser.add_option('-B',
    	          dest='covgh',
                  default='covgh.txt', 
                  help='file with C_gh [deg,cov]: -Bcovgh.txt',
                  )
parser.add_option('-C',
    	          dest='covgg',
                  default='covgg.txt', 
                  help='file with C_gg [deg,cov]: -Ccovgg.txt',
                  )
parser.add_option('-D',
    	          dest='covng',
                  default='covng.txt', 
                  help='file with C_ng [deg,cov]: -Dcovng.txt',
                  )
parser.add_option('-o',
    	          dest='fileout',
                  default='colloc.out', 
                  help='write output to FILEOUT [lon,lat,signal]: -ocolloc.out',
                  )
parser.add_option('-v',
    	          dest='varsig',
                  default=230.0, 
				  type='float',
                  help='variance of the signal to be computed: -v230.0',
                  )
parser.add_option('-d', 
    	          dest='diameter',
                  default=None, 
		          type='float',
                  help='diameter of circular cell used in the calculation [deg]: -d0.5',
                  )
parser.add_option('-l', 
    	          dest='side',
                  default=None, 
		          type='float',
                  help='side of square cell used in the calculation [deg]: -l0.5',
                  )
parser.add_option('-R', 
    	          dest='region',
                  default='(308,330,-6,8)', 
                  help='region to generate the grid [deg]: -Rwest,east,south,north',
                  )
parser.add_option('-I', 
    	          dest='resolut',
                  default=2, 
		          type='float',
                  help='final grid resolution [deg]: -I2',
                  )
parser.add_option('-s',
    	          dest='scale',
                  action='store_true',
                  default=False, 
                  help='use local (cell) scale factor for cov functions: -s',
                  )
options, remainder = parser.parse_args()

filesdh = options.filesdh
filegrav = options.filegrav

if filesdh == None and filegrav == None:
    parser.print_help()
    exit()

colsd = eval(options.colsd)
colsg = eval(options.colsg)
signal = options.signal
fcovhh = options.covhh
fcovgg = options.covgg
fcovgh = options.covgh
fcovng = options.covng
fileout = options.fileout
var_sig = options.varsig
d = options.diameter
l = options.side
region = eval(options.region)
dx = options.resolut
dy = options.resolut
scale = options.scale

# minimum number of observations accepted per inversion cell 
# for signal calculation. ATTENTION: this number will depend on 
# the size of the cell
MIN_OBS = 30 

# maximum value accepted for the calculated signal (to avoid absurds)
# otherwise the signal is forced to be zero
MAX_VAL = 200.0

#--------------------------------------------------------------------------

def load_data(filesdh, colsd, filegrav=None, colsg=None):

    """Load data in cols x y z.. from one or two data files."""

    if filegrav==None:
        print 'loading data from file:\n%s' % filesdh
        return N.loadtxt(filesdh, usecols=colsd)
    elif not filegrav==None:
        print 'loading data from files:\n%s\n%s' % (filesdh, filegrav)
        return N.loadtxt(filesdh, usecols=colsd), \
               N.loadtxt(filegrav, usecols=colsg)

#--------------------------------------------------------------------------

def select_points(IN, OUT, lon, lat, d):

    """Selects the pts inside the circle pi*(d/2)**2 
	centering at (lon,lat) -> Circular inversion cell."""

    nrow = IN.shape[0]
    ncol = IN.shape[1]
    r = d/2.0

    functions = \
    """
	// Distance between two points (P and Q)

	double distance_pq(double lon_1, double lat_1, 
	                   double lon_2, double lat_2) {

			return hypot(lon_1 - lon_2, lat_1 - lat_2);
	}
    """
	
    main_code = \
    """
	int k = 0;
	double dist, x, y;

    for (int i = 0; i < nrow; i++) {
	    x = IN(i,0);  // lon
	    y = IN(i,1);  // lat

        dist = distance_pq(lon, lat, x, y);  // deg

	    if (dist <= r) {
	        for (int j = 0; j < ncol; j++){
		        OUT(k,j) = IN(i,j);
		    }
	        k++;
	   }
	}

	return_val = k;  // number of selected pts
	"""
    vars = ['IN', 'OUT', 'lon', 'lat', 'r', 'nrow', 'ncol']
    return weave.inline(main_code, vars, support_code=functions, 
	                    type_converters=blitz)

#--------------------------------------------------------------------------
def select_points2(IN, OUT, lon, lat, l):

    """Selects the pts inside the square l**2 centering 
	at (lon,lat) -> Square inversion cell"""

    nrow = IN.shape[0]
    ncol = IN.shape[1]
    r = l/2.0

    main_code = \
    """
	int k = 0;
	double x, y, xmin = lon, xmax = lon, ymin = lat, ymax = lat;

    xmin -= r;
	xmax += r;
	ymin -= r;
	ymax += r;

    for (int i = 0; i < nrow; i++) {
	    x = IN(i,0);  // lon
	    y = IN(i,1);  // lat

	    if ( xmin <= x && x <= xmax && ymin <= y && y <= ymax) {
	        for (int j = 0; j < ncol; j++){
		        OUT(k,j) = IN(i,j);
		    }
	        k++;
	   }
	}

	return_val = k;  // number of selected pts
	"""
    vars = ['IN', 'OUT', 'lon', 'lat', 'r', 'nrow', 'ncol']
    return weave.inline(main_code, vars, type_converters=blitz)

#--------------------------------------------------------------------------

def fill_cov_signal1(OBS, COVSH, C_sig, lon_grid, lat_grid, scale):

    """Fills vector of signal covariances: 
	
	    C_sig = [C_gd] or [C_nd]
	
	Finds covariances btw the signal (grav or geoid), in a grid point, 
	and the observations (SDH) to be used in the signal calculation 
	(inside a radius), by linear interpolation from tabulated covs: 
	a weighted average btw the two closest values is performed.

	OBS = SDH (sea surface gradients)
	COVSH = covariances btw signal and longitudinal component of SDH
	C_sig = vector of signal covariances
	scale = scale factor related to the cell (cov: global -> local)
	"""

    ne = OBS.shape[0] 
    ncov = COVSH.shape[0]

    functions = \
    """
	// Distance between two points (P and Q) ------------------------------

	double distance_pq(double lon_1, double lat_1, 
	                   double lon_2, double lat_2) {

			return hypot(lon_1 - lon_2, lat_1 - lat_2);
	}
	"""

    main_code = \
    """
	using namespace std;
    double lon_h1, lat_h1, lon_h2, lat_h2;
	double dist1, dist2, cov1, cov2, w1, w2, C_sh1, C_sh2;
	double dist_pq1, dist_pq2, s = scale;

    for (int i = 0; i < ne-1; i++) {                                      //!!!!!! ne-1 ???

        lon_h1 = OBS(i,0);    // SDH lon (deg)
        lat_h1 = OBS(i,1);    // SDH lat (deg)

        lon_h2 = OBS(i+1,0);    // SDH lon (deg)
        lat_h2 = OBS(i+1,1);    // SDH lat (deg)
     
        // distance btw pts P (grid-signal) and Q (observation)
        dist_pq1 = distance_pq(lon_grid, lat_grid, lon_h1, lat_h1);  // deg
        dist_pq2 = distance_pq(lon_grid, lat_grid, lon_h2, lat_h2);  // deg

		// se h_q nao eh extremo de trilha

		if ( abs(dist_pq2 - dist_pq1) < 0.1 ) {

            // finds a cov value according to distance btw: P--Q
            for (int j = 0; j < ncov-1; j++) {
            
                dist1 = COVSH(j,0);    // tabulated distance
                cov1 = COVSH(j,1);     // tabulated covariance 
                dist2 = COVSH(j+1,0);
                cov2 = COVSH(j+1,1);     
            
            	// a) if there is an exact tabulated distance no average is needed
            	if (dist_pq1 == dist1) {
            		C_sh1 = cov1;
            	    break;
                }
            	// b) if it is btw two values a weighted average is performed
                else if (dist1 < dist_pq1 && dist_pq1 <= dist2) {
                    w1 = (dist2 - dist_pq1)/(dist2 - dist1);   // weight cov1 
                    w2 = 1.0 - w1;                            // weight cov2
                    C_sh1 = w1 * cov1 + w2 * cov2;             // weighted average
            	    break;
                }
            	// c) if there isn't tabulated values for this distance in the file
                else if (j == ncov-2) {
                    cout << "Radius to large, no C_sh1 for: " << dist_pq1 << " deg, "
                         << "filling with 0.0" << endl;
            	    C_sh1 = 0.0;
                }
            }

            //////////
            
            // finds a cov value according to distance btw: P--Q+1
            for (int j = 0; j < ncov-1; j++) {
            
                dist1 = COVSH(j,0);    // tabulated distance
                cov1 = COVSH(j,1);     // tabulated covariance 
                dist2 = COVSH(j+1,0);
                cov2 = COVSH(j+1,1);     
            
            	// a) if there is an exact tabulated distance no average is needed
            	if (dist_pq2 == dist1) {
            		C_sh2 = cov1;
            	    break;
                }
            	// b) if it is btw two values a weighted average is performed
                else if (dist1 < dist_pq2 && dist_pq2 <= dist2) {
                    w1 = (dist2 - dist_pq2)/(dist2 - dist1);   // weight cov1 
                    w2 = 1.0 - w1;                            // weight cov2
                    C_sh2 = w1 * cov1 + w2 * cov2;             // weighted average
            	    break;
                }
            	// c) if there isn't tabulated values for this distance in the file
                else if (j == ncov-2) {
                    cout << "Radius to large, no C_sh2 for: " << dist_pq2 << " deg, "
                         << "filling with 0.0" << endl;
            	    C_sh2 = 0.0;
                }
            }
	        // calculates C_gd or C_nd ----------------------------------------

            C_sig(i) = (C_sh2 - C_sh1) * s;
		}
		else
            C_sig(i) = 0.001;
    }

    C_sig(ne-1) = 0.001;   // ultimo elemento eh descartado
    """
    vars = ['OBS', 'COVSH', 'C_sig', 'lon_grid', 'lat_grid', 'ne', \
	        'ncov', 'scale']
    weave.inline(main_code, vars, support_code=functions, type_converters=blitz)

#--------------------------------------------------------------------------

def fill_cov_signal2(OBS, COVSH, COVSG, C_sig, lon_grid, lat_grid, 
                      ne, ng, scale):

    """Fills vector of signal covariances: 
	
	    C_sig = [C_gd C_gg] or [C_nd C_ng]
	
	Finds covariances btw the signal (grav or geoid), in a grid point, 
	and the observations (SDH and GRAV) to be used in the signal 
	calculation (inside a radius), by linear interpolation from tabulated 
	covs: a weighted average btw the two closest values is performed.

	OBS = SDH + GRAV (sea surface gradients + gravity anomalies)
	COVSH = covariances btw signal and longitudinal component of SDH
	COVSG = covariances btw signal and gravity anomaly (GRAV)
	C_sig = vector of signal covariances
	ne = number of observations SDH
	ng = number of observations GRAV
	scale = scale factor related to the cell (cov: global -> local)
	"""

    ncsh = COVSH.shape[0]
    ncsg = COVSG.shape[0]

    functions = \
    """
	// Distance between two point (P and Q) -------------------------------

	double distance_pq(double lon_1, double lat_1, 
	                   double lon_2, double lat_2) {

			return hypot(lon_1 - lon_2, lat_1 - lat_2);
	}
	"""

    main_code = \
    """
    using namespace std;
    double lon_h1, lat_h1, lon_h2, lat_h2;
	double dist1, dist2, cov1, cov2, w1, w2, C_sh1, C_sh2;
	double dist_pq1, dist_pq2;
	double lon_grav, lat_grav, C_sg;
	double s = scale;

    // (1) fill first part of C_sig with COVSH ---------------------------
    // from [0] to [ne-1] with C_sd

    for (int i = 0; i < ne-1; i++) {                                      //!!!!!! ne-1 ???

        lon_h1 = OBS(i,0);    // SDH lon (deg)
        lat_h1 = OBS(i,1);    // SDH lat (deg)

        lon_h2 = OBS(i+1,0);    // SDH lon (deg)
        lat_h2 = OBS(i+1,1);    // SDH lat (deg)
     
        // distance btw pts P (grid-signal) and Q (observation)
        dist_pq1 = distance_pq(lon_grid, lat_grid, lon_h1, lat_h1);  // deg
        dist_pq2 = distance_pq(lon_grid, lat_grid, lon_h2, lat_h2);  // deg

		if ( abs(dist_pq2 - dist_pq1) < 0.1 ) {   // se os pts pertencem a mesma trilha

            // finds a cov value according to distance btw: P--Q
            for (int j = 0; j < ncsh-1; j++) {
            
                dist1 = COVSH(j,0);    // tabulated distance
                cov1 = COVSH(j,1);     // tabulated covariance 
                dist2 = COVSH(j+1,0);
                cov2 = COVSH(j+1,1);     
            
            	// a) if there is an exact tabulated distance no average is needed
            	if (dist_pq1 == dist1) {
            		C_sh1 = cov1;
            	    break;
                }
            	// b) if it is btw two values a weighted average is performed
                else if (dist1 < dist_pq1 && dist_pq1 <= dist2) {
                    w1 = (dist2 - dist_pq1)/(dist2 - dist1);   // weight cov1 
                    w2 = 1.0 - w1;                            // weight cov2
                    C_sh1 = w1 * cov1 + w2 * cov2;             // weighted average
            	    break;
                }
            	// c) if there isn't tabulated values for this distance in the file
                else if (j == ncsh-2) {
                    cout << "Radius to large, no C_sh1 for: " << dist_pq1 << " deg, "
                         << "filling with 0.0" << endl;
            	    C_sh1 = 0.0;
                }
            }

            //////////
            
            // finds a cov value according to distance btw: P--Q+1
            for (int j = 0; j < ncsh-1; j++) {
            
                dist1 = COVSH(j,0);    // tabulated distance
                cov1 = COVSH(j,1);     // tabulated covariance 
                dist2 = COVSH(j+1,0);
                cov2 = COVSH(j+1,1);     
            
            	// a) if there is an exact tabulated distance no average is needed
            	if (dist_pq2 == dist1) {
            		C_sh2 = cov1;
            	    break;
                }
            	// b) if it is btw two values a weighted average is performed
                else if (dist1 < dist_pq2 && dist_pq2 <= dist2) {
                    w1 = (dist2 - dist_pq2)/(dist2 - dist1);   // weight cov1 
                    w2 = 1.0 - w1;                            // weight cov2
                    C_sh2 = w1 * cov1 + w2 * cov2;             // weighted average
            	    break;
                }
            	// c) if there isn't tabulated values for this distance in the file
                else if (j == ncsh-2) {
                    cout << "Radius to large, no C_sh2 for: " << dist_pq2 << " deg, "
                         << "filling with 0.0" << endl;
            	    C_sh2 = 0.0;
                }
            }
	        // calculates C_gd or C_nd ----------------------------------------

            C_sig(i) = (C_sh2 - C_sh1) * s;
		}
		else
            C_sig(i) = 0.001;
    }

    C_sig(ne-1) = 0.001;   // ultimo elemento eh descartado


    // (2) fill second part of C_sig with COVSG --------------------------
    // from [ne] to [ne+ng-1] with C_sg

    for (int i = ne; i < ne+ng; i++) {  

        lon_grav = OBS(i,0);  // lon GRAV at Q
        lat_grav = OBS(i,1);  // lat GRAV at Q

        // distance btw pts P (grid-signal) and Q (observation)
        dist_pq1 = distance_pq(lon_grid, lat_grid, lon_grav, lat_grav);  // deg
     
        // finds a cov value according to distance btw pts
        for (int j = 0; j < ncsg-1; j++) {

            dist1 = COVSG(j,0);    // tabulated distance
            cov1 = COVSG(j,1);     // tabulated covariance 
            dist2 = COVSG(j+1,0);
            cov2 = COVSG(j+1,1);     

			// a) if there is an exact tabulated distance no average is needed
			if (dist_pq1 == dist1) {

				C_sg = cov1;
        	    break;
            }
			// b) if it is btw two values a weighted average is performed
            else if (dist1 < dist_pq1 && dist_pq1 <= dist2) {

                w1 = (dist2 - dist_pq1)/(dist2 - dist1);   // weight cov1 
                w2 = 1.0 - w1;                            // weight cov2
                C_sg = w1 * cov1 + w2 * cov2;             // weighted average
        	    break;
            }
			// c) if there isn't tabulated values for this distance in the file
            else if (j == ncsg-2) {

                cout << "Radius to large, no C_sg for: " << dist_pq1 << " deg, "
                     << "filling with 0.0" << endl;
        	    C_sg = 0.0;
            }
        }

		// C_gg or C_ng ---------------------------------------------------

		C_sig(i) = C_sg * s;
    }
    """
    vars = ['OBS', 'COVSH', 'COVSG', 'C_sig', 'lon_grid', 'lat_grid', \
	        'ne', 'ng', 'ncsh', 'ncsg', 'scale']
    weave.inline(main_code, vars, support_code=functions, type_converters=blitz)

#--------------------------------------------------------------------------

def fill_cov_observ1(OBS, COVHH, C_OBS, scale):

    """Fills matrix of observations covariances: 
	
	    C_OBS = [C_dd + D_d]
	
	Finds covariances btw the observations (SDH), in a radius, to be 
	used in the signal (grid point) calculation, by linear interpolation 
	from tabulated covs: a weighted average btw the two closest values 
	is performed.

	The error variance is added to the diagonal elements.

	OBS = SDH (sea surface gradients inside a radius)
	COVHH = covariances btw longitudinal components of SDH
	C_OBS = matrix of observations covariances
	scale = scale factor related to the cell (cov: global -> local)
	"""

    ne = OBS.shape[0] 
    nchh = COVHH.shape[0]

    functions = \
    """
	// Distance between two point (P and Q) -------------------------------

	double distance_pq(double lon_1, double lat_1, 
	                   double lon_2, double lat_2) {

			return hypot(lon_1 - lon_2, lat_1 - lat_2);
	}
	"""

    main_code = \
    """
    using namespace std;
    double lon_p1, lon_p2, lat_p1, lat_p2, lon_q1, lon_q2, lat_q1, lat_q2; 
	double dist_p1q1, dist_p1q2, dist_p2q1, dist_p2q2; 
	double C_h1h1, C_h1h2, C_h2h1, C_h2h2;
	double dist1, dist2, cov1, cov2, w1, w2;
	double s = scale;

    for (int i = 0; i < ne-1; i++) {

        lon_p1 = OBS(i,0);    // lon h at P (deg)
        lat_p1 = OBS(i,1);    // lat h at P (deg)
        lon_p2 = OBS(i+1,0);  // lon h at P+1 (deg)
        lat_p2 = OBS(i+1,1);  // lat h at P+1 (deg)

        for (int j = 0; j < ne-1; j++) {

            lon_q1 = OBS(j,0);    // lon h at Q
            lat_q1 = OBS(j,1);    // lat h at Q
            lon_q2 = OBS(j+1,0);  // lon h at Q+1
            lat_q2 = OBS(j+1,1);  // lat h at Q+1

            // distance btw h's
            dist_p1q1 = distance_pq(lon_p1, lat_p1, lon_q1, lat_q1);  // deg
            dist_p1q2 = distance_pq(lon_p1, lat_p1, lon_q2, lat_q2);  // deg
            dist_p2q1 = distance_pq(lon_p2, lat_p2, lon_q1, lat_q1);  // deg
            dist_p2q2 = distance_pq(lon_p2, lat_p2, lon_q2, lat_q2);  // deg

			// se os dois pts (h_p e h_q) nao sao extremos de trilha

  		    if ( (abs(dist_p1q2 - dist_p1q1) < 0.1) && (abs(dist_p2q1 - dist_p1q1) < 0.1) ) {

                // finds a cov value according to distance btw pts:
                
                // for C_h1h1 -------------------------------------------------
                
                for (int k = 0; k < nchh-1; k++) {
                
                    dist1 = COVHH(k,0);    // tabulated distance
                    cov1 = COVHH(k,1);     // tabulated covariance 
                    dist2 = COVHH(k+1,0);
                    cov2 = COVHH(k+1,1);     
                
                    // a) if there is an exact tabulated distance no average is needed
                    if (dist_p1q1 == dist1) {
                
                    	C_h1h1 = cov1;
                        break;
                    }
                    // b) if it is btw two values a weighted average is performed
                    else if (dist1 < dist_p1q1 && dist_p1q1 <= dist2) {
                
                        w1 = (dist2 - dist_p1q1)/(dist2 - dist1);  // weight cov1 
                        w2 = 1.0 - w1;                           // weight cov2
                        C_h1h1 = w1 * cov1 + w2 * cov2;            // weighted average
                        break;
                    }
                    // c) if there isn't tabulated values for this distance in the file
                    else if (k == nchh-2) {
                
                        cout << "Radius to large, no C_h1h1 for: " << dist_p1q1 << " deg, "
                             << "filling with 0.0" << endl;
                        C_h1h1 = 0.0;
                    }
                }
                
                    // for C_h1h2 -------------------------------------------------
                    
                    for (int k = 0; k < nchh-1; k++) {
                    
                        dist1 = COVHH(k,0);    // tabulated distance
                        cov1 = COVHH(k,1);     // tabulated covariance 
                        dist2 = COVHH(k+1,0);
                        cov2 = COVHH(k+1,1);     
                    
                        // a)
                        if (dist_p1q2 == dist1) {
                    
                        	C_h1h2 = cov1;
                            break;
                        }
                        // b)
                        else if (dist1 < dist_p1q2 && dist_p1q2 <= dist2) {
                    
                            w1 = (dist2 - dist_p1q2)/(dist2 - dist1);  // weight cov1 
                            w2 = 1.0 - w1;                           // weight cov2
                            C_h1h2 = w1 * cov1 + w2 * cov2;            // weighted average
                            break;
                        }
                        // c) 
                        else if (k == nchh-2) {
                    
                            cout << "Radius to large, no C_h1h2 for: " << dist_p1q2 << " deg, "
                                 << "filling with 0.0" << endl;
                            C_h1h2 = 0.0;
                        }
                    }
                
                // for C_h2h1 -------------------------------------------------
                
                for (int k = 0; k < nchh-1; k++) {
                
                    dist1 = COVHH(k,0);    // tabulated distance
                    cov1 = COVHH(k,1);     // tabulated covariance 
                    dist2 = COVHH(k+1,0);
                    cov2 = COVHH(k+1,1);     
                
                    // a)
                    if (dist_p2q1 == dist1) {
                
                    	C_h2h1 = cov1;
                        break;
                    }
                    // b)
                    else if (dist1 < dist_p2q1 && dist_p2q1 <= dist2) {
                
                        w1 = (dist2 - dist_p2q1)/(dist2 - dist1);  // weight cov1 
                        w2 = 1.0 - w1;                           // weight cov2
                        
                        break;
                    }
                    // c) 
                    else if (k == nchh-2) {
                
                        cout << "Radius to large, no C_h2h1 for: " << dist_p2q1 << " deg, "
                             << "filling with 0.0" << endl;
                        C_h2h1 = 0.0;
                    }
                }
                
                // for C_h2h2 -------------------------------------------------
                
                for (int k = 0; k < nchh-1; k++) {
                
                    dist1 = COVHH(k,0);    // tabulated distance
                    cov1 = COVHH(k,1);     // tabulated covariance 
                    dist2 = COVHH(k+1,0);
                    cov2 = COVHH(k+1,1);     
                
                    // a)
                    if (dist_p2q2 == dist1) {
                
                    	C_h2h2 = cov1;
                        break;
                    }
                    // b)
                    else if (dist1 < dist_p2q2 && dist_p2q2 <= dist2) {
                
                        w1 = (dist2 - dist_p2q2)/(dist2 - dist1);  // weight cov1 
                        w2 = 1.0 - w1;                           // weight cov2
                        C_h2h2 = w1 * cov1 + w2 * cov2;            // weighted average
                        break;
                    }
                    // c) 
                    else if (k == nchh-2) {
                
                        cout << "Radius to large, no C_h2h2 for: " << dist_p2q2 << " deg, "
                             << "filling with 0.0" << endl;
                        C_h2h2 = 0.0;
                    }
                }
                // C_dd -------------------------------------------------------
                
                C_OBS(i,j) = (C_h2h2 - C_h2h1 - C_h1h2 + C_h1h1) * s;
                
                // Adds the error variance to the diagonal element ------------
                
                if (i == j && C_OBS(i,j) != 0)                       // TER CERTEZA !!!
                    C_OBS(i,j) += OBS(i,3);                          // + D_d

			}
			else
				C_OBS(i,j) = 0.001;

		}
        C_OBS(i,ne-1) = 0.001;   // ultima coluna eh descartada
	}
	for (int j = 0; j < ne; j++) 
        C_OBS(ne-1,j) = 0.001;   // ultima linha eh descartada

    """
    vars = ['OBS', 'COVHH','C_OBS', 'ne', 'nchh', 'scale']
    weave.inline(main_code, vars, support_code=functions, type_converters=blitz)

#--------------------------------------------------------------------------

def fill_cov_observ2(OBS, COVHH, COVGG, COVGH, C_OBS, ne, ng, scale):

    """Fills matrix of observations covariances: 
	
        C_OBS = [C_dd + D_d  C_dg]
                [C_gd  C_gg + D_g]
	
	Finds covariances btw the observations (SDH + GRAV), in a radius, 
	to be used in the signal (grid point) calculation, by linear 
	interpolation from tabulated covs: a weighted average btw the 
	two closest values is performed.

	The error variance is added to the diagonal elements.

	OBS = SDH (sea surface gradients inside a radius)
	COVHH = covariances btw longitudinal components of SDH
	COVMM = covariances btw transversal components of SDH
	COVGG = covariances btw gravity anomalies GRAV
	COVGH = covariances btw gravity anomaly and longitudinal comp of SDH
	C_OBS = matrix of observations covariances
	ne = number of SDHs
	ng = number of GRAVs
	scale = scale factor related to the cell (cov: global -> local)
	"""

    nchh = COVHH.shape[0]
    ncgg = COVGG.shape[0]
    ncgh = COVGH.shape[0]

    functions = \
    """
	// Distance between two point (P and Q) -------------------------------

	double distance_pq(double lon_1, double lat_1, 
	                   double lon_2, double lat_2) {

			return hypot(lon_1 - lon_2, lat_1 - lat_2);
	}
	"""

    main_code = \
    """
    using namespace std;
    double lon_p1, lon_p2, lat_p1, lat_p2, lon_q1, lon_q2, lat_q1, lat_q2; 
	double dist_p1q1, dist_p1q2, dist_p2q1, dist_p2q2; 
	double C_h1h1, C_h1h2, C_h2h1, C_h2h2;
	double dist1, dist2, cov1, cov2, w1, w2;

    double lon_h1, lat_h1, lon_h2, lat_h2;
	double C_sh1, C_sh2;
	double dist_pq1, dist_pq2;
	double lon_g, lat_g, C_sg;

    double lon_p, lat_p, lon_q, lat_q; 
	double dist_pq, C_gg; 

	double s = scale;

    // (1) fill 1st part of C_OBS with COVHH -------------------------

	// from (0,0) to (ne-1,ne-1) with C_dd + D_d

    for (int i = 0; i < ne-1; i++) {

        lon_p1 = OBS(i,0);    // lon h at P (deg)
        lat_p1 = OBS(i,1);    // lat h at P (deg)
        lon_p2 = OBS(i+1,0);  // lon h at P+1 (deg)
        lat_p2 = OBS(i+1,1);  // lat h at P+1 (deg)

        for (int j = 0; j < ne-1; j++) {

            lon_q1 = OBS(j,0);    // lon h at Q
            lat_q1 = OBS(j,1);    // lat h at Q
            lon_q2 = OBS(j+1,0);  // lon h at Q+1
            lat_q2 = OBS(j+1,1);  // lat h at Q+1

            // distance btw h's
            dist_p1q1 = distance_pq(lon_p1, lat_p1, lon_q1, lat_q1);  // deg
            dist_p1q2 = distance_pq(lon_p1, lat_p1, lon_q2, lat_q2);  // deg
            dist_p2q1 = distance_pq(lon_p2, lat_p2, lon_q1, lat_q1);  // deg
            dist_p2q2 = distance_pq(lon_p2, lat_p2, lon_q2, lat_q2);  // deg

			// se os dois pts (h_p e h_q) nao sao extremos de trilha

  		    if ( (abs(dist_p1q2 - dist_p1q1) < 0.1) && (abs(dist_p2q1 - dist_p1q1) < 0.1) ) {

                // finds a cov value according to distance btw pts:
                
                // for C_h1h1 -------------------------------------------------
                
                for (int k = 0; k < nchh-1; k++) {
                
                    dist1 = COVHH(k,0);    // tabulated distance
                    cov1 = COVHH(k,1);     // tabulated covariance 
                    dist2 = COVHH(k+1,0);
                    cov2 = COVHH(k+1,1);     
                
                    // a) if there is an exact tabulated distance no average is needed
                    if (dist_p1q1 == dist1) {
                
                    	C_h1h1 = cov1;
                        break;
                    }
                    // b) if it is btw two values a weighted average is performed
                    else if (dist1 < dist_p1q1 && dist_p1q1 <= dist2) {
                
                        w1 = (dist2 - dist_p1q1)/(dist2 - dist1);  // weight cov1 
                        w2 = 1.0 - w1;                           // weight cov2
                        C_h1h1 = w1 * cov1 + w2 * cov2;            // weighted average
                        break;
                    }
                    // c) if there isn't tabulated values for this distance in the file
                    else if (k == nchh-2) {
                
                        cout << "Radius to large, no C_h1h1 for: " << dist_p1q1 << " deg, "
                             << "filling with 0.0" << endl;
                        C_h1h1 = 0.0;
                    }
                }
                
                    // for C_h1h2 -------------------------------------------------
                    
                    for (int k = 0; k < nchh-1; k++) {
                    
                        dist1 = COVHH(k,0);    // tabulated distance
                        cov1 = COVHH(k,1);     // tabulated covariance 
                        dist2 = COVHH(k+1,0);
                        cov2 = COVHH(k+1,1);     
                    
                        // a)
                        if (dist_p1q2 == dist1) {
                    
                        	C_h1h2 = cov1;
                            break;
                        }
                        // b)
                        else if (dist1 < dist_p1q2 && dist_p1q2 <= dist2) {
                    
                            w1 = (dist2 - dist_p1q2)/(dist2 - dist1);  // weight cov1 
                            w2 = 1.0 - w1;                           // weight cov2
                            C_h1h2 = w1 * cov1 + w2 * cov2;            // weighted average
                            break;
                        }
                        // c) 
                        else if (k == nchh-2) {
                    
                            cout << "Radius to large, no C_h1h2 for: " << dist_p1q2 << " deg, "
                                 << "filling with 0.0" << endl;
                            C_h1h2 = 0.0;
                        }
                    }
                
                // for C_h2h1 -------------------------------------------------
                
                for (int k = 0; k < nchh-1; k++) {
                
                    dist1 = COVHH(k,0);    // tabulated distance
                    cov1 = COVHH(k,1);     // tabulated covariance 
                    dist2 = COVHH(k+1,0);
                    cov2 = COVHH(k+1,1);     
                
                    // a)
                    if (dist_p2q1 == dist1) {
                
                    	C_h2h1 = cov1;
                        break;
                    }
                    // b)
                    else if (dist1 < dist_p2q1 && dist_p2q1 <= dist2) {
                
                        w1 = (dist2 - dist_p2q1)/(dist2 - dist1);  // weight cov1 
                        w2 = 1.0 - w1;                           // weight cov2
                        C_h2h1 = w1 * cov1 + w2 * cov2;            // weighted average
                        break;
                    }
                    // c) 
                    else if (k == nchh-2) {
                
                        cout << "Radius to large, no C_h2h1 for: " << dist_p2q1 << " deg, "
                             << "filling with 0.0" << endl;
                        C_h2h1 = 0.0;
                    }
                }
                
                // for C_h2h2 -------------------------------------------------
                
                for (int k = 0; k < nchh-1; k++) {
                
                    dist1 = COVHH(k,0);    // tabulated distance
                    cov1 = COVHH(k,1);     // tabulated covariance 
                    dist2 = COVHH(k+1,0);
                    cov2 = COVHH(k+1,1);     
                
                    // a)
                    if (dist_p2q2 == dist1) {
                
                    	C_h2h2 = cov1;
                        break;
                    }
                    // b)
                    else if (dist1 < dist_p2q2 && dist_p2q2 <= dist2) {
                
                        w1 = (dist2 - dist_p2q2)/(dist2 - dist1);  // weight cov1 
                        w2 = 1.0 - w1;                           // weight cov2
                        C_h2h2 = w1 * cov1 + w2 * cov2;            // weighted average
                        break;
                    }
                    // c) 
                    else if (k == nchh-2) {
                
                        cout << "Radius to large, no C_h2h2 for: " << dist_p2q2 << " deg, "
                             << "filling with 0.0" << endl;
                        C_h2h2 = 0.0;
                    }
                }
                // C_dd -------------------------------------------------------
                
                C_OBS(i,j) = (C_h2h2 - C_h2h1 - C_h1h2 + C_h1h1) * s;
                
                // Adds the error variance to the diagonal element ------------
                
                if (i == j && C_OBS(i,j) != 0)                       // TER CERTEZA !!!
                    C_OBS(i,j) += OBS(i,3);                          // + D_d

			}
			else
				C_OBS(i,j) = 0.001;

		}
        C_OBS(i,ne-1) = 0.001;   // ultima coluna eh descartada
	}
	for (int j = 0; j < ne; j++) 
        C_OBS(ne-1,j) = 0.001;   // ultima linha eh descartada

    //////////////

    // (2) fill 2nd part of C_OBS with COVGH -----------------------------

	// from (0,ne) to (ne-1,ne+ng-1) with C_dg

    for (int i = 0; i < ne-1; i++) {                                      //!!!!!! ne-1 ???

        lon_h1 = OBS(i,0);    // SDH lon (deg)
        lat_h1 = OBS(i,1);    // SDH lat (deg)

        lon_h2 = OBS(i+1,0);    // SDH lon (deg)
        lat_h2 = OBS(i+1,1);    // SDH lat (deg)

        for (int j = ne; j < ne+ng; j++) {

            lon_g = OBS(j,0);    // lon GRAV at Q
            lat_g = OBS(j,1);    // lat GRAV at Q
     
            // distance btw pts P (grid-signal) and Q (observation)
            dist_pq1 = distance_pq(lon_g, lat_g, lon_h1, lat_h1);  // deg
            dist_pq2 = distance_pq(lon_g, lat_g, lon_h2, lat_h2);  // deg
            
            if ( abs(dist_pq2 - dist_pq1) < 0.1 ) {   // se o h1 e h2 pertencem a mesma trilha
            
                // finds a cov value according to distance btw: P--Q
                for (int k = 0; k < ncgh-1; k++) {
                
                    dist1 = COVGH(k,0);    // tabulated distance
                    cov1 = COVGH(k,1);     // tabulated covariance 
                    dist2 = COVGH(k+1,0);
                    cov2 = COVGH(k+1,1);     
                
                	// a) if there is an exact tabulated distance no average is needed
                	if (dist_pq1 == dist1) {

                		C_sh1 = cov1;
                	    break;
                    }
                	// b) if it is btw two values a weighted average is performed
                    else if (dist1 < dist_pq1 && dist_pq1 <= dist2) {

                        w1 = (dist2 - dist_pq1)/(dist2 - dist1);   // weight cov1 
                        w2 = 1.0 - w1;                            // weight cov2
                        C_sh1 = w1 * cov1 + w2 * cov2;             // weighted average
                	    break;
                    }
                	// c) if there isn't tabulated values for this distance in the file
                    else if (k == ncgh-2) {

                        cout << "Radius to large, no C_sh1 for: " << dist_pq1 << " deg, "
                             << "filling with 0.0" << endl;
                	    C_sh1 = 0.0;
                    }
                }
            
                //////////
                
                // finds a cov value according to distance btw: P--Q+1
                for (int k = 0; k < ncgh-1; k++) {
                
                    dist1 = COVGH(k,0);    // tabulated distance
                    cov1 = COVGH(k,1);     // tabulated covariance 
                    dist2 = COVGH(k+1,0);
                    cov2 = COVGH(k+1,1);     
                
                	// a) if there is an exact tabulated distance no average is needed
                	if (dist_pq2 == dist1) {

                		C_sh2 = cov1;
                	    break;
                    }
                	// b) if it is btw two values a weighted average is performed
                    else if (dist1 < dist_pq2 && dist_pq2 <= dist2) {

                        w1 = (dist2 - dist_pq2)/(dist2 - dist1);   // weight cov1 
                        w2 = 1.0 - w1;                            // weight cov2
                        C_sh2 = w1 * cov1 + w2 * cov2;             // weighted average
                	    break;
                    }
                	// c) if there isn't tabulated values for this distance in the file
                    else if (k == ncgh-2) {

                        cout << "Radius to large, no C_sh2 for: " << dist_pq2 << " deg, "
                             << "filling with 0.0" << endl;
                	    C_sh2 = 0.0;
                    }
                }
                // calculates C_gd or C_nd ----------------------------------------
            
                C_OBS(i,j) = (C_sh2 - C_sh1) * s;
            }
            else
                C_OBS(i,j) = 0.001;
		}
	}
    for (int j = ne; j < ne+ng; j++) 
        C_OBS(ne-1,j) = 0.001;   // ultima linha eh descartada

    /////////////////////

    // (3) fill 3th part of C_OBS with COVGH -----------------------------

	// from (ne,0) to (ne+ng-1,ne-1) with C_gd = C_dg

    for (int i = ne; i < ne+ng; i++) {

        lon_g = OBS(i,0);    // lon GRAV at P
        lat_g = OBS(i,1);    // lat GRAV at P

        for (int j = 0; j < ne-1; j++) {

            lon_h1 = OBS(j,0);    // SDH lon (deg)
            lat_h1 = OBS(j,1);    // SDH lat (deg)

            lon_h2 = OBS(j+1,0);    // SDH lon (deg)
            lat_h2 = OBS(j+1,1);    // SDH lat (deg)

            // distance btw pts P (grid-signal) and Q (observation)
            dist_pq1 = distance_pq(lon_g, lat_g, lon_h1, lat_h1);  // deg
            dist_pq2 = distance_pq(lon_g, lat_g, lon_h2, lat_h2);  // deg
            
            if ( abs(dist_pq2 - dist_pq1) < 0.1 ) {   // se o h1 e h2 pertencem a mesma trilha
            
                // finds a cov value according to distance btw: P--Q
                for (int k = 0; k < ncgh-1; k++) {
                
                    dist1 = COVGH(k,0);    // tabulated distance
                    cov1 = COVGH(k,1);     // tabulated covariance 
                    dist2 = COVGH(k+1,0);
                    cov2 = COVGH(k+1,1);     
                
                	// a) if there is an exact tabulated distance no average is needed
                	if (dist_pq1 == dist1) {

                		C_sh1 = cov1;
                	    break;
                    }
                	// b) if it is btw two values a weighted average is performed
                    else if (dist1 < dist_pq1 && dist_pq1 <= dist2) {

                        w1 = (dist2 - dist_pq1)/(dist2 - dist1);   // weight cov1 
                        w2 = 1.0 - w1;                            // weight cov2
                        C_sh1 = w1 * cov1 + w2 * cov2;             // weighted average
                	    break;
                    }
                	// c) if there isn't tabulated values for this distance in the file
                    else if (k == ncgh-2) {

                        cout << "Radius to large, no C_sh1 for: " << dist_pq1 << " deg, "
                             << "filling with 0.0" << endl;
                	    C_sh1 = 0.0;
                    }
                }
            
                //////////
                
                // finds a cov value according to distance btw: P--Q+1
                for (int k = 0; k < ncgh-1; k++) {
                
                    dist1 = COVGH(k,0);    // tabulated distance
                    cov1 = COVGH(k,1);     // tabulated covariance 
                    dist2 = COVGH(k+1,0);
                    cov2 = COVGH(k+1,1);     
                
                	// a) if there is an exact tabulated distance no average is needed
                	if (dist_pq2 == dist1) {

                		C_sh2 = cov1;
                	    break;
                    }
                	// b) if it is btw two values a weighted average is performed
                    else if (dist1 < dist_pq2 && dist_pq2 <= dist2) {

                        w1 = (dist2 - dist_pq2)/(dist2 - dist1);   // weight cov1 
                        w2 = 1.0 - w1;                            // weight cov2
                        C_sh2 = w1 * cov1 + w2 * cov2;             // weighted average
                	    break;
                    }
                	// c) if there isn't tabulated values for this distance in the file
                    else if (k == ncgh-2) {

                        cout << "Radius to large, no C_sh2 for: " << dist_pq2 << " deg, "
                             << "filling with 0.0" << endl;
                	    C_sh2 = 0.0;
                    }
                }
                // calculates C_dg or C_dn ----------------------------------------
            
                C_OBS(i,j) = (C_sh2 - C_sh1) * s;
            }
            else
                C_OBS(i,j) = 0.001;
        }
        C_OBS(i,ne-1) = 0.001;   // ultima coluna eh descartada
    }

    // (4) fill 4th part of C_OBS with COVGG -----------------------------

	// from (ne,ne) to (ne+ng-1,ne+ng-1) with C_gg + D_g

    for (int i = ne; i < ne+ng; i++) {

        lon_p = OBS(i,0);    // lon GRAV at P (deg)
        lat_p = OBS(i,1);    // lat GRAV at P (deg)

        for (int j = ne; j < ne+ng; j++) {

            lon_q = OBS(j,0);    // lon GRAV at Q
            lat_q = OBS(j,1);    // lat GRAV at Q

            // distance btw GRAVs at P=(lon_p,lat_p) and Q=(lon_q,lat_q)
            dist_pq = distance_pq(lon_p, lat_p, lon_q, lat_q);  // deg
            
            // finds a cov value according to distance btw pts:

            // for C_gg ---------------------------------------------------

            for (int k = 0; k < ncgg-1; k++) {

                dist1 = COVGG(k,0);    // tabulated distance
                cov1 = COVGG(k,1);     // tabulated covariance 
                dist2 = COVGG(k+1,0);
                cov2 = COVGG(k+1,1);     

		        // a) if there is an exact tabulated distance no average is needed
		        if (dist_pq == dist1) {
		        	C_gg = cov1;
                    break;
                }
		        // b) if it is btw two values a weighted average is performed
                else if (dist1 < dist_pq && dist_pq <= dist2) {
                    w1 = (dist2 - dist_pq)/(dist2 - dist1);  // weight cov1 
                    w2 = 1.0 - w1;                           // weight cov2
                    C_gg = w1 * cov1 + w2 * cov2;            // weighted average
                    break;
                }
		        // c) if there isn't tabulated values for this distance in the file
                else if (k == nchh-2) {
                    cout << "Radius to large, no C_gg for: " << dist_pq << " deg, "
                         << "filling with 0.0" << endl;
                    C_gg = 0.0;
                }
            }

			// C_gg -------------------------------------------------------

            C_OBS(i,j) = C_gg * s;

            // Adds the error variance to the diagonal element ------------

            if (i == j && C_OBS(i,j) != 0)                       // TER CERTEZA !!!
                C_OBS(i,j) += OBS(i,3);                          // + D_g
        }
    }
    """
    vars = ['OBS', 'COVHH', 'COVGG', 'COVGH', 'C_OBS', 'ne', 'ng', \
	        'nchh', 'ncgg', 'ncgh', 'scale']
    weave.inline(main_code, vars, support_code=functions, type_converters=blitz)

#--------------------------------------------------------------------------

def LSC_solver1(C_sig, C_OBS, obs, var_sig):

    """solves the Least Squares Collocation system: 

        signal = C_sig * C_OBS_inv * obs
        error = variance - C_sig * C_OBS_inv * C_sig_tansp

    using the Hwang and Parsons (1995) algorithm:
    
        signal = b.T * y
        error = variance - b.T * b
		
    for one single point.
    """

    # signal calculation 
    L = N.linalg.cholesky(C_OBS)     # cholesky decomposition = L_MAT
    L_i = N.linalg.inv(L)            # L_MATRIX invertion
    b = N.dot(L_i, C_sig.T)          # L_MAT_inv * sig_VEC_transp = b_VEC
    b_t = b.T                        # b_VEC transpost
    y = N.dot(L_i, obs)              # L_MAT_inv * obs_VEC = y_VEC
    signal = N.dot(b_t, y)           # b_VEC_transp * y_VEC
    
    # error calculation
    error = var_sig - N.dot(b_t, b)  # var_ESC - b_VEC_transp * b_VEC

    return signal, error

#--------------------------------------------------------------------------

def LSC_solver2(C_sig, C_OBS, obs, var_sig):

    """solves the Least Squares Collocation system: 

        signal = C_sig * C_OBS_inv * obs
        error = variance - C_sig * C_OBS_inv * C_sig_tansp

    using conventional matrix invertion, for one single point.
    """

    # signal calculation 
    C_OBS_i = N.linalg.inv(C_OBS)               # matrix invertion
    signal = N.dot(N.dot(C_sig, C_OBS_i), obs)  # dot product

    # error calculation
    C_sig_t = C_sig.T                           # vector transpost
    error = var_sig - N.dot(N.dot(C_sig, C_OBS_i), C_sig_t)

    return signal, error

#--------------------------------------------------------------------------

def scale_factor(obs, COVHH, ne, COVGG=False, ng=0):

    """calculates the local scale factor for each cell to scale the
	covariance functions in the inversion procedure.

    obs = observations
	COVHH = cov(l,l)
	ne = number of SDHs
	COVGG = cov(g,g)
	ng = number of GRAVs
	"""

    convert_factor = 23.504430595412476       # asec**2 -> urad**2
    #convert_factor = 1.0/23.504430595412476  # urad**2 -> asec**2
    
    # ratio btw estimated (local) and modeled (global) variances

    ## a = ratio for SDHs
    local_var_e = N.var(obs[:ne])	 
    global_var_e = COVHH[0,1] * convert_factor  
    a = local_var_e / global_var_e            # adimensional

    ## b = ratio for GRAVs
    if not ng == 0:
        local_var_g = N.var(obs[ne:ng])	 
        global_var_g = COVGG[0,1]
        b = local_var_g / global_var_g
    else:
        b = 0

    # scale factor related to the cell
    scale = (ne * a + ng * b) / (ne + ng)

    # to ensure the covariance wont be increased: 0 <= s <= 1
    if scale <= 1.0:
        s = scale
    else:
        s = 1.0

    return s


#--------------------------------------------------------------------------

def main():

    ### (1) observations: SDH
    if filegrav == None:             
        DATAE = load_data(filesdh, colsd) 
        ne = DATAE.shape[0]
        AUXE = N.empty((ne, 4), 'float64')
        print 'observations: SDH'

        # a) signal: GRAV | covs: C_ll, C_mm, C_gl
        if signal == 'g':
            COVHH = N.loadtxt(fcovhh)
            COVGH = N.loadtxt(fcovgh)
            print 'signal: GRAV'
            print 'covariances: C_ll, C_mm, C_gl'
        # b) signal: GEOID | covs: C_ll, C_mm, C_nl
        elif signal == 'n':
            COVHH = N.loadtxt(fcovhh)
            print 'signal: GEOID'
            print 'covariances: C_ll, C_mm, C_nl'
        else:
            print 'Error with signal choice: -s[g|n]'
            exit()

    ### (2) observations: SDH + GRAV
    else: 
        DATAE, DATAG = load_data(filesdh, colsd, filegrav, colsg) 
        ne = DATAE.shape[0]
        ng = DATAG.shape[0]
        AUXE = N.empty((ne, 4), 'float64')
        AUXG = N.empty((ng, 4), 'float64')
        print 'observations: SDH + GRAV'

        # a) signal: GRAV | covs: C_ll, C_mm, C_gg, C_gl
        if signal == 'g':
            COVHH = N.loadtxt(fcovhh)
            COVGG = N.loadtxt(fcovgg)
            COVGH = N.loadtxt(fcovgh)
            print 'signal: GRAV'
            print 'covariances: C_ll, C_mm, C_gg, C_gl'
        # b) signal: GEOID | covs: C_ll, C_mm, C_gg, C_gl, C_ng, C_nl
        elif signal == 'n':
            COVHH = N.loadtxt(fcovhh)
            COVGG = N.loadtxt(fcovgg)
            COVGH = N.loadtxt(fcovgh)
            COVNG = N.loadtxt(fcovng)
            print 'signal: GEOID'
            print 'covariances: C_ll, C_mm, C_gg, C_gl, C_ng, C_nl'
        else:
            print 'Error with signal choice: -s[g|n]'
            exit()

    xmin, xmax, ymin, ymax = region

    # change longitude: -180/180 -> 0/360
    if xmin < 0:
        xmin += 360.
    if xmax < 0:
        xmax += 360.

    if scale == True:
        print 'using cell scale factor (local covariances)'
    else:
        s = 1.0

    if not d == None:
        print 'circular inversion cell: d =', d, '(deg)'
        print 'min points per inversion cell:', MIN_OBS
    elif not l == None:
        print 'square inversion cell: l =', l, '(deg)'
        print 'min points per inversion cell:', MIN_OBS
    else:
        print 'Error: diameter (-d) or side (-l) of cell is missing!'
        exit()

    # grid calculation ----------------------------------------------------

    TEMP = N.empty(4, 'float64')
    GRID = N.empty((0, 4), 'float64')

    print "grid spacing: %.2f' x %.2f'" % (dx*60.0, dy*60.0)
    print 'calculating grid: %.2f/%.2f/%.2f/%.2f ...' % region

    for lat in N.arange(ymin, ymax, dy):
        for lon in N.arange(xmin, xmax, dx):

            # select points inside the inversion cell

            if filegrav == None:
                if not d == None:
                    nobs = select_points(DATAE, AUXE, lon, lat, d)  # circular
                    ne = nobs
                else:
                    nobs = select_points2(DATAE, AUXE, lon, lat, l) # square
                    ne = nobs
            else:
                if not d == None:
                    ne = select_points(DATAE, AUXE, lon, lat, d)  
                    ng = select_points(DATAG, AUXG, lon, lat, d)
                else:
                    ne = select_points2(DATAE, AUXE, lon, lat, l)  
                    ng = select_points2(DATAG, AUXG, lon, lat, l)
                nobs = ne + ng

            # if there are sufficient observations inside the cell 
            # (i.e. it is a valid point of the grid outside the continent):
            # fill obs, C_sig (cov_sig_obs), C_OBS (cov_obs_obs)

            if nobs >= MIN_OBS:  # num of obs sufficient for signal calculation
                
                ### (1) obsservations: SDH
                if filegrav == None or ng == 0:        # no GRAV observations
                    OBS = AUXE[:nobs,:]                # SDHs
                    obs = OBS[:,2]                     # VECTOR of observations
                    C_sig = N.empty(nobs, 'float64')   # VECTOR of signal covs
                    C_OBS = N.empty((nobs,nobs), 'float64') # MATRIX of obs covs + err

                    # cell scale factor
                    if scale == True:
                        s = scale_factor(obs, COVHH, nobs)
                        #print s  #################################

                    # a) signal: GRAV
                    if signal == 'g':
                        fill_cov_signal1(OBS, COVGH, C_sig, lon, lat, s)
                        fill_cov_observ1(OBS, COVHH, C_OBS, s)


                    # b) signal: GEOID
                    elif signal == 'n':
                        fill_cov_signal1(OBS, COVHH, C_sig, lon, lat, s)
                        fill_cov_observ1(OBS, COVHH, COVMM, C_OBS, s)

                ### (2) observations: SDH + GRAV
                else:					
                    OBS = AUXE[:ne,:]
                    OBS = N.vstack((OBS, AUXG[:ng,:]))
                    obs = OBS[:,2]                          
                    C_sig = N.empty(nobs, 'float64')        
                    C_OBS = N.empty((nobs,nobs), 'float64') 

                    # cell scale factor
                    if scale == True:
                        s = scale_factor(obs, COVHH, ne, COVGG, ng)
                        #print s  #################################

                    # a) signal: GRAV
                    if signal == 'g':
                        fill_cov_signal2(OBS, COVGH, COVGG, C_sig, lon, lat, ne, ng, s)
                        fill_cov_observ2(OBS, COVHH, COVGG, COVGH, C_OBS, ne, ng, s)

                    # b) signal: GEOID
                    elif signal == 'n':
                        fill_cov_signal2(OBS, COVHH, COVNG, C_sig, lon, lat, ne, ng, s)
                        fill_cov_observ2(OBS, COVHH, COVGG, COVGH, C_OBS, ne, ng, s)
    			 

                ### reduction                
                
                cond = N.ones(nobs, 'i')
                cond[ne-1] = 0
                C_sig = N.compress(cond, C_sig)
                
                C_OBS = N.compress(cond, C_OBS, 0)
                C_OBS = N.compress(cond, C_OBS, 1)
                
                obs = N.compress(cond, obs)


                ### solves the LSC system: sig = C_sig * C_OBS_inv * obs
                ### for each point (cell) in the grid


                # (1) using the Hwang and Parsons (1995) algorithm
                try:
                    sig, err = LSC_solver1(C_sig, C_OBS, obs, var_sig)

                # (2) using conventional matrix inversion
                except:
                    sig, err = LSC_solver2(C_sig, C_OBS, obs, var_sig)
                
                # avoid singular matrix
                else:
                    sig = 0.0
                    err = 0.0
                    

                # to avoid absurd values
                if N.abs(sig) > MAX_VAL:
                    sig = 0.0

            # if no obs or not sufficient -> signal = 0 -------------------
            else:
                sig = 0.0         
                err = 0.0

            TEMP[0] = lon                  # lon grid point
            TEMP[1] = lat                  # lat grid point
            TEMP[2] = sig                  # signal on grid point
            TEMP[3] = err                  # error on grid point
    
            GRID = N.vstack((GRID, TEMP))

    print 'saving data ...'
    N.savetxt(fileout, GRID, fmt='%f', delimiter=' ')
    print 'output [lon,lat,signal,error] -> ' + fileout


if __name__ == '__main__':
    main()
