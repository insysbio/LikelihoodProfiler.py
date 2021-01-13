import math

f_1p = lambda x: 5.0 + (x[0]-3.0)**2 # [100., missing, missing, missing]

f_2p_1im = lambda x: 5.0 + (x[0]-3.0)**2 + 0.0*x[1]  # [3., missing, missing, missing]

f_2p = lambda x: 5.0 + (x[0]-3.0)**2 + (x[1]-4.0)**2  # [3., 4., missing, missing]

f_3p_1im = lambda x: 5.0 + (x[0]-3.0)**2 + (x[1]/x[2]-4.0)**2 # [3., missing, missing, missing]

f_3p_1im_dep = lambda x: 5.0 + (x[0]-3.0)**2 + (x[0]-x[1]-1.0)**2 + 0*x[2]**2

f_4p_2im = lambda x: 5.0 + (x[0]-3.0)**2 + (x[1]-4.0)**2 + 0.0*x[2] + 0.0*x[3] # [3., 4., missing, missing]

f_4p_3im = lambda x: 5.0 + (x[0]-3.0)**2 + (x[1]/x[2]-4.0)**2 + 0.0*x[3] # [3., missing, missing, missing]

f_1p_ex = lambda x: 5.0 + (x[0]-1e-8)**2 # [1e-8, missing, missing, missing]

f_5p_3im = lambda x: 5.0 + (x[0]-3.0)**2 + (math.exp(x[1])-1.0)**2 + (x[2]/x[3]-4.0)**2 + 0.0*x[4]

f_3p_im = lambda x: 5.0 + (x[0]-3.0)**2 + (math.exp(x[1])-1.0)**2 + 0.0*x[2]
