""" compare_ppsd.py
This script takes a glob type argument and plots a comparison
"""

import matplotlib.pyplot as plt
import numpy as np
import glob
import sys
from obspy.signal.spectral_estimation import get_nlnm, get_nhnm

def plot_ppsd(fmatch):

  files=glob.glob(fmatch)
  print(files)
  plt.figure()
  for file in files:
    d=np.load(file)
    f=d['arr_0'][0]
    a=d['arr_0'][1]
    plt.semilogx(f,a)
  f,a=get_nlnm()
  plt.semilogx(f,a,'-k',label='NLNM')
  f,a=get_nhnm()
  plt.semilogx(f,a,'-k',label='NHNM')
  plt.xlabel('Period (s)')
  plt.ylabel('Amplitude (dB)')
  
  plt.show()


if len(sys.argv)>1:
  fmatch=sys.argv[1]
  print(fmatch)
  plot_ppsd(fmatch)
else:
  print("Cant' find any files")