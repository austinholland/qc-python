""" compare_ppsd.py
This script takes a glob type argument and plots a comparison

Example:
compare_ppsd.py 'qcdata/2017/*/PPSDper50_CC.ASBU..BHZ.npz'
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
  title=''
  for file in files:
    fv=file.split('/')
    date=fv[1]+'-'+fv[2]+' '
    j,t=fv[-1].split('_')
    ch=t.split('.npz')
    d=np.load(file)
    f=d['arr_0'][0]
    a=d['arr_0'][1]
    plt.semilogx(f,a,label=date+ch[0])
  f,a=get_nlnm()
  plt.semilogx(f,a,'-k',label='NLNM')
  f,a=get_nhnm()
  plt.semilogx(f,a,'-k',label='NHNM')
  plt.xlabel('Period (s)')
  plt.ylabel('Amplitude (dB)')
  plt.legend()
  plt.show()


if len(sys.argv)>1:
  fmatch=sys.argv[1]
  print(fmatch)
  plot_ppsd(fmatch)
else:
  print("Cant' find any files")