""" Download a day of data by Channel and look at the PPSD for that day of data
"""
from obspy.core import *
import obspy.clients.fdsn as fdsn
import obspy.clients.iris as iris
from obspy.io.xseed import Parser
from obspy.signal import PPSD
from obspy.imaging.cm import pqlx
import numpy as np
import glob
import sys
import os
import logging

logger = logging.getLogger('log')
logger.setLevel(logging.DEBUG)

def respfilename(seedid):
  return "%sRESP.%s" % (respdir,ch)
  
def path_verify(path):
  head,tail=os.path.split(path)
  try:
    os.makedirs(head)
  except:
    pass
  return path
  
# Should use command line arguments to enter these
stations=[
'ASBU',
'CIHL',
'CPCO',
'CLCV',
'CLMS',
'CLBH',
'CRST',
'CLWZ',
'HUSB',
'HIYU',
'JRO',
'KWBU',
'NORM',
'PRLK',
'SWNB',
'TMBU',
'SWF2',
'SHRK',
'WIFE',
'TCBU',
'STD',
'VALT',
'SVIC',
'SUG',
'SEP',
'OSBR',
'PANH',
'PALM',
'TIMB',
'SR41'
]
network='CC'
if len(sys.argv)>1:
  day=UTCDateTime(sys.argv[1])
else:
  day=UTCDateTime('2017-022T00:00:00.0')
secperday=24*60*60.
datadir="data/"
respdir="resp/"
qcfigs="qcfigs/"
qcdata="qcdata/"
path_verify(qcdata)
path_verify(datadir)
path_verify(qcfigs)
path_verify(respdir)



client=fdsn.Client("IRIS",timeout=240)

for station in stations:
  # Look for channel files that already exist
  files_exist=False
  files=glob.glob("%s%d/%03d/%s.%s*.seed" % (datadir,day.year,day.julday,network,station))
  st=Stream()
  # Read files from disk if they exist
  if len(files)>0:
    files_exist=True
    for file in files:
      st+=read(file)
  else:
    try:
      st=client.get_waveforms(network,station,"*","*",day,day+secperday)
    except:
      print("Unable to download data for %s %s" %(station,str(day)))
  # Get all of our channel ids
  ids=[]
  for tr in st:
   ids.append(tr.id)
  ids=set(ids)
  #Write each channel to its own file
  if not files_exist:
    for ch in ids:
      #print(st)
      stch=st.select(id=ch)
      #print(stch)
      filename="%s%d/%03d/%s.seed" % (datadir,day.year,day.julday,ch)
      path_verify(filename)
      stch.write(filename,format='MSEED',reclen=512)
  # Make sure our resp files are up to date
  irisclient=iris.Client()
  for ch in ids:
    n,s,loc,chan=ch.split('.')
    try:
      resp=irisclient.resp(network,station,location=loc,channel=chan,starttime=UTCDateTime('2004-001T00:00:00.0'),endtime=day+secperday,filename=respfilename(ch))
      resp=irisclient.evalresp(network,station,loc,chan,filename="%s%s.png" % (qcfigs,ch),output='plot')
    except:
      print("No response data for channel %s" % (ch))
  data={}
  for ch in ids:
    print(respfilename(ch))
    stch=st.select(id=ch) # Just take the data for a single channel
    try:
      ppsd=PPSD(stch[0].stats,metadata=str(respfilename(ch)))
      ppsd.add(stch)
      figname="%s%d/%03d/%s.png" % (qcfigs,day.year,day.julday,ch)
      path_verify(figname)
      ppsd.plot(figname,cmap=pqlx)
      data=ppsd.get_percentile(percentile=50)
      fname="%s%d/%03d/PPSDper50_%s.npz" % (qcdata,day.year,day.julday,ch)
      path_verify(fname)
      np.savez(fname,data)
    except:
      print("Error with PPSD for %s check for response" % (ch))
	
    
